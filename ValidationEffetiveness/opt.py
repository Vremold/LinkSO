import sys
sys.path.append("..")
import os
import json
import csv
import re
import numpy as np

from match_so_to_tb import MatcherFromSOToTB

# choices: mprank, stringmatch
lexical_choice="mprank"
# choices: sentence-bert, word2vec
semantic_choice="sentence-bert"
matcher = MatcherFromSOToTB(lexical_choice=lexical_choice, semantic_choice=semantic_choice)

class Judger(object):
    def __init__(self):
        pass

    def judge_section(self, x, y, z, lx_section_scores, sm_section_scores, c_section_scores, label):
        if len(sm_section_scores) != len(lx_section_scores) or len(sm_section_scores) != len(c_section_scores):
            return False, False
        section_scores = dict()
        for section in sm_section_scores:
            if section not in section_scores:
                section_scores[section] = 0
            section_scores[section] += x * lx_section_scores[section] + y * sm_section_scores[section] + z * c_section_scores[section]
        section_scores = sorted(section_scores.items(), key=lambda x : x[1], reverse=True)
        pred_sections = [section_scores[0][0], section_scores[1][0], section_scores[2][0]]
        # pred_sections = [s.replace("#", "/") for s in pred_sections]
        if pred_sections[0] in label:
            return 1, 1, 1
        elif pred_sections[1] in label:
            return 0, 1, 1
        if pred_sections[2] in label:
            return 0, 0, 1
        return 0, 0, 0

    def judge_chapter(self, x, y, z, lx_chapter_scores, sm_chapter_scores, c_chapter_scores, label):
        chapter_scores = dict()
        for chapter in lx_chapter_scores:
            if chapter not in chapter_scores:
                chapter_scores[chapter] = 0
            chapter_scores[chapter] += x * lx_chapter_scores[chapter] + y * sm_chapter_scores[chapter] + z * c_chapter_scores[chapter]
        chapter_scores = sorted(chapter_scores.items(), key=lambda x : x[1], reverse=True)
        # print(chapter_scores)
        pred_chapters = [chapter_scores[0][0], chapter_scores[1][0], chapter_scores[2][0]]
        if pred_chapters[0] == label:
            return 1, 1, 1
        elif pred_chapters[1] == label:
            return 0, 1, 1
        if label in pred_chapters:
            return 0, 0, 1
        return 0, 0, 0

class Optimizer(object):
    def __init__(self, log_file, d=0.01):
        self.d = 0.01
        self.log = open(log_file, "w", encoding="utf-8")
        self.judger = Judger()
    
    def optimize_chapter(self, lx_scores, sm_scores, c_scores, labels):
        total_samples = len(lx_scores)

        best_config = dict()

        for x in np.linspace(0, 1, num=101, endpoint=True):
            for y in np.linspace(0, 1, num=101, endpoint=True):
                if y + x > 1:
                    break
                z = 1 - x - y
                right1, right2, right3 = 0, 0, 0
                for (lx, sm, c, l) in zip(lx_scores, sm_scores, c_scores, labels):
                    tmp1, tmp2, tmp3 = self.judger.judge_chapter(x, y, z, lx, sm, c, l)
                    right1 += tmp1
                    right2 += tmp2
                    right3 += tmp3
                if len(best_config) == 0 or right1 > best_config["right1"]:
                    best_config = {
                        "right1": right1,
                        "right2": right2,
                        "right3": right3,
                        "x": x,
                        "y": y,
                        "z": z
                    }
                elif right1 == best_config["right1"] and right2 > best_config["right2"]:
                    best_config = {
                        "right1": right1,
                        "right2": right2,
                        "right3": right3,
                        "x": x,
                        "y": y,
                        "z": z
                    }
                elif right1 == best_config["right1"] and right2 == best_config["right2"] and right3 > best_config["right3"]:
                    best_config = {
                        "right1": right1,
                        "right2": right2,
                        "right3": right3,
                        "x": x,
                        "y": y,
                        "z": z
                    }

                self.log.write("[CHAPTER] lx_weight=%0.4f, sm_weight=%0.4f, c_weight=%0.4f, right1=%s, right2=%s, right3=%s, total=%d\n" % (x, y, z, str(right1).zfill(3), str(right2).zfill(3), str(right3).zfill(3), total_samples))
        
        print(best_config)
        return best_config
    
    def optimize_section(self, lx_scores, sm_scores, c_scores, labels):
        total_samples = len(lx_scores)

        best_config = dict()

        for x in np.linspace(0, 1, num=101, endpoint=True):
            for y in np.linspace(0, 1, num=101, endpoint=True):
                if y + x > 1:
                    break
                z = 1 - x - y
                right1, right2, right3 = 0, 0, 0
                for (lx, sm, c, l) in zip(lx_scores, sm_scores, c_scores, labels):
                    tmp1, tmp2, tmp3 = self.judger.judge_section(x, y, z, lx, sm, c, l)
                    right1 += tmp1
                    right2 += tmp2
                    right3 += tmp3
                if len(best_config) == 0 or right1 > best_config["right1"]:
                    best_config = {
                        "right1": right1,
                        "right2": right2,
                        "right3": right3,
                        "x": x,
                        "y": y,
                        "z": z
                    }
                elif right1 == best_config["right1"] and right2 > best_config["right2"]:
                    best_config = {
                        "right1": right1,
                        "right2": right2,
                        "right3": right3,
                        "x": x,
                        "y": y,
                        "z": z
                    }
                elif right1 == best_config["right1"] and right2 == best_config["right2"] and right3 > best_config["right3"]:
                    best_config = {
                        "right1": right1,
                        "right2": right2,
                        "right3": right3,
                        "x": x,
                        "y": y,
                        "z": z
                    }

                self.log.write("[SECTION] lx_weight=%0.4f, sm_weight=%0.4f, c_weight=%0.4f, right1=%s, right2=%s, right3=%s, total=%d\n" % (x, y, z, str(right1).zfill(3), str(right2).zfill(3), str(right3).zfill(3), total_samples))
        
        print(best_config)
        return best_config

def train(clean_cache=False):
    matcher.set_debug(True)
    opt = Optimizer(log_file="train{}-{}.log".format(lexical_choice, semantic_choice))
    
    cache_file = os.path.join("cache", "train{}-{}.txt".format(lexical_choice, semantic_choice))
    if not clean_cache and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as inf:
            lx_chapter_scores = json.loads(inf.readline())
            sm_chapter_scores = json.loads(inf.readline())
            c_chapter_scores = json.loads(inf.readline())
            answer_chapters = json.loads(inf.readline())
            lx_section_scores = json.loads(inf.readline())
            sm_section_scores = json.loads(inf.readline())
            c_section_scores = json.loads(inf.readline())
            answer_sections = json.loads(inf.readline())
        print("...loading data and refering finished")
        
        chapter_config = opt.optimize_chapter(lx_chapter_scores, sm_chapter_scores, c_chapter_scores, answer_chapters)
        section_config = opt.optimize_section(lx_section_scores, sm_section_scores, c_section_scores, answer_sections)
        print("...optimizing finished")
        return chapter_config, section_config
    
    Xs, ys = list(), list()
    with open("./train.csv", "r", encoding="utf-8") as inf:
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            # print(line)
            qid = int(line[0])
            qtitle = line[2]
            qbody = line[3]
            qcodes = json.loads(line[4])
            aid = int(line[6])
            abody = line[7]
            acodes = json.loads(line[8])
            chapter_label = line[9]
            section_labels = json.loads(line[10])
            Xs.append((qid, qtitle, qbody, qcodes, aid, abody, acodes))
            ys.append((chapter_label, section_labels))
    
    print("...loading data finished")
    lx_chapter_scores, sm_chapter_scores, c_chapter_scores, answer_chapters = list(), list(), list(), list()
    lx_section_scores, sm_section_scores, c_section_scores, answer_sections = list(), list(), list(), list()

    for X, y in zip(Xs, ys):
        lc, sc, cc = matcher.match_in_chapter(X[1], X[2], X[5], X[3], X[6])
        lx_chapter_scores.append(lc)
        sm_chapter_scores.append(sc)
        c_chapter_scores.append(cc)
        answer_chapters.append(y[0])
        ls, ss, cs = matcher.match_in_section(X[1], X[2], X[5], X[3], X[6], y[0])
        lx_section_scores.append(ls)
        sm_section_scores.append(ss)
        c_section_scores.append(cs)
        answer_sections.append(y[1])

    print("...refering finished")
    with open(cache_file, "w", encoding="utf-8") as outf:
        outf.write(json.dumps(lx_chapter_scores)+"\n")
        outf.write(json.dumps(sm_chapter_scores)+"\n")
        outf.write(json.dumps(c_chapter_scores)+"\n")
        outf.write(json.dumps(answer_chapters)+"\n")
        outf.write(json.dumps(lx_section_scores)+"\n")
        outf.write(json.dumps(sm_section_scores)+"\n")
        outf.write(json.dumps(c_section_scores)+"\n")
        outf.write(json.dumps(answer_sections)+"\n")

    chapter_config = opt.optimize_chapter(lx_chapter_scores, sm_chapter_scores, c_chapter_scores, answer_chapters)
    section_config = opt.optimize_section(lx_section_scores, sm_section_scores, c_section_scores, answer_sections)
    print("...optimizing finished")

    return chapter_config, section_config

def validate(cx, cy, cz, sx, sy, sz, outf):
    outf = open(outf, "w", encoding="utf-8")
    matcher.set_debug(False)

    Xs, ys = list(), list()
    chapter_right1, chapter_right2, chapter_right3, section_right1, section_right2, section_right3, total_samples = 0, 0, 0, 0, 0, 0, 0
    with open("./validate.csv", "r", encoding="utf-8") as inf:
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            total_samples += 1
            # print(line)
            qid = int(line[0])
            qtitle = line[2]
            qbody = line[3]
            qcodes = json.loads(line[4])
            aid = int(line[6])
            abody = line[7]
            acodes = json.loads(line[8])
            chapter_label = line[9]
            section_labels = json.loads(line[10])

            # predicating chapters
            matcher.set_weights(cx, cy, cz)
            chapter_scores = matcher.match_in_chapter(qtitle, qbody, abody, qcodes, acodes)
            chapter_scores = sorted(chapter_scores.items(), key=lambda x: x[1], reverse=True)
            pred_chapters = [chapter_scores[0][0], chapter_scores[1][0], chapter_scores[2][0]]
            outf.write("{}----{}\t".format(chapter_label, pred_chapters))
            if chapter_label == pred_chapters[0]:
                chapter_right1 += 1
                chapter_right3 += 1
                chapter_right2 += 1
            elif chapter_label == pred_chapters[1]:
                chapter_right2 += 1
                chapter_right3 += 1
            elif chapter_label in pred_chapters:
                chapter_right3 += 1
            
            # predicating sections
            matcher.set_weights(sx, sy, sz)
            section_scores = matcher.match_in_section(qtitle, qbody, abody, qcodes, acodes, chapter_label)
            section_scores = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)
            pred_sections = [section_scores[0][0], section_scores[1][0], section_scores[2][0]]
            pred_sections = [s.replace("#", "/") for s in pred_sections]
            outf.write("{}----{}\n".format(list(section_labels.keys()), pred_sections))
            if pred_sections[0] in section_labels:
                section_right1 += 1
                section_right3 += 1
                section_right2 += 1
            elif pred_sections[1] in section_labels:
                section_right2 += 1
                section_right3 += 1
            elif pred_sections[2] in section_labels:
                section_right3 += 1
    
    print(chapter_right1, chapter_right2, chapter_right3, section_right1, section_right2, section_right3, total_samples)

def validate_train(cx, cy, cz, sx, sy, sz, outf):
    outf = open(outf, "w", encoding="utf-8")
    matcher.set_debug(False)

    Xs, ys = list(), list()
    chapter_right1, chapter_right2, chapter_right3, section_right1, section_right2, section_right3, total_samples = 0, 0, 0, 0, 0, 0, 0
    with open("./train.csv", "r", encoding="utf-8") as inf:
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            total_samples += 1
            # print(line)
            qid = int(line[0])
            qtitle = line[2]
            qbody = line[3]
            qcodes = json.loads(line[4])
            aid = int(line[6])
            abody = line[7]
            acodes = json.loads(line[8])
            chapter_label = line[9]
            section_labels = json.loads(line[10])

            # predicating chapters
            matcher.set_weights(cx, cy, cz)
            chapter_scores = matcher.match_in_chapter(qtitle, qbody, abody, qcodes, acodes)
            chapter_scores = sorted(chapter_scores.items(), key=lambda x: x[1], reverse=True)
            pred_chapters = [chapter_scores[0][0], chapter_scores[1][0], chapter_scores[2][0]]
            outf.write("{}----{}\t".format(chapter_label, pred_chapters))
            if chapter_label == pred_chapters[0]:
                chapter_right1 += 1
                chapter_right3 += 1
                chapter_right2 += 1
            elif chapter_label == pred_chapters[1]:
                chapter_right2 += 1
                chapter_right3 += 1
            elif chapter_label in pred_chapters:
                chapter_right3 += 1
            
            # predicating sections
            matcher.set_weights(sx, sy, sz)
            section_scores = matcher.match_in_section(qtitle, qbody, abody, qcodes, acodes, chapter_label)
            section_scores = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)
            pred_sections = [section_scores[0][0], section_scores[1][0], section_scores[2][0]]
            # pred_sections = [s.replace("#", "/") for s in pred_sections]
            outf.write("{}----{}\n".format(list(section_labels.keys()), pred_sections))
            if pred_sections[0] in section_labels:
                section_right1 += 1
                section_right3 += 1
                section_right2 += 1
            elif pred_sections[1] in section_labels:
                section_right2 += 1
                section_right3 += 1
            elif pred_sections[1] in section_labels or pred_sections[2] in section_labels:
                section_right3 += 1
    
    print(chapter_right1, chapter_right2, chapter_right3, section_right1, section_right2, section_right3, total_samples)


if __name__ == "__main__":
    chapter_config, section_config = train(clean_cache=True)
    validate(chapter_config["x"], chapter_config["y"], chapter_config["z"], section_config["x"], section_config["y"], section_config["z"], "validate_result.txt")
    # validate(0, 0.3, 0.7, 0, 0.9, 0.1, "validate_result.txt")
    # validate_train(0, 0.3, 0.7, 0, 0.9, 0.1, "train_result.txt")