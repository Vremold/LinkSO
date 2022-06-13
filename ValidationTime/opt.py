import sys
sys.path.append("..")
import os
import json
import csv
import re
import numpy as np
import time

from match_so_to_tb import MatcherFromSOToTB

# choices: mprank, stringmatch
lexical_choice="mprank"
# choices: sentence-bert, word2vec
semantic_choice="word2vec"

def validate(cx, cy, cz, sx, sy, sz):
    matcher = MatcherFromSOToTB(lexical_choice=lexical_choice, semantic_choice=semantic_choice)
    matcher.set_debug(False)
    with open("./validate.csv", "r", encoding="utf-8") as inf:
        csv_reader = csv.reader(inf)
        for line in csv_reader:
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
            
            # predicating sections
            matcher.set_weights(sx, sy, sz)
            section_scores = matcher.match_in_section(qtitle, qbody, abody, qcodes, acodes, chapter_label)
            section_scores = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)
            pred_sections = [section_scores[0][0], section_scores[1][0], section_scores[2][0]]
            pred_sections = [s.replace("#", "/") for s in pred_sections]

            

if __name__ == "__main__":
    # sentence-bert
    # st = time.time()
    # validate(0.0, 0.3, 0.7, 0.0, 0.9, 0.1)
    # ed = time.time()
    # print((ed - st) / 150)

    # word2vec
    st = time.time()
    validate(0.05, 0, 0.95, 1, 0, 0)
    ed = time.time()
    print((ed - st)/10)