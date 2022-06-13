import sys
sys.path.append("..")
import os
import json
import csv
import re

from match_so_to_tb import MatcherFromSOToTB

test_filepath = "../SODataClean/so_posts_duplicate.csv"

# choices: mprank, stringmatch
lexical_choice="mprank"
# choices: sentence-bert, word2vec
semantic_choice="sentence-bert"

class DuplicateSOValidater(object):
    def __init__(self, src_filepath):
        self.xs = list()
        with open(src_filepath, "r", encoding="utf-8") as inf:
            csv_reader = csv.reader(inf)
            for line in csv_reader:
                self.xs.append((
                    [int(line[0]), line[2], line[3], json.loads(line[4]), int(line[6]), line[7], json.loads(line[8])],
                    [int(line[9]), line[11], line[12], json.loads(line[13]), int(line[15]), line[16], json.loads(line[17])],
                ))
        self.matcher = MatcherFromSOToTB(lexical_choice=lexical_choice, semantic_choice=semantic_choice)
        self.matcher.set_debug(False)
    
    def config_weight(self, l, s, c):
        self.matcher.set_weights(l, s, c)

    def validate_chapter(self, save_result_path):
        print("starting validating chapter")
        outf = open(save_result_path, "w", encoding="utf-8")
        for x1, x2 in self.xs:
            chapter_scores1 = self.matcher.match_in_chapter(x1[1], x1[2], x1[5], x1[3], x1[6])
            chapter_scores2 = self.matcher.match_in_chapter(x2[1], x2[2], x2[5], x2[3], x2[6])
            chapter_scores1 = sorted(chapter_scores1.items(), key=lambda x: x[1], reverse=True)
            chapter_scores2 = sorted(chapter_scores2.items(), key=lambda x: x[1], reverse=True)
            pred1 = [chapter_scores1[0][0], chapter_scores1[1][0], chapter_scores1[2][0]]
            pred2 = [chapter_scores2[0][0], chapter_scores2[1][0], chapter_scores2[2][0]]

            outf.write("{}\t{}\n".format(json.dumps(pred1), json.dumps(pred2)))

if __name__ == "__main__":
    dsv =  DuplicateSOValidater(test_filepath)
    # # Think In Java
    # dsv.config_weight(0, 0.3, 0.7)
    # dsv.validate_chapter("thinkinjava.txt")

    # # Core Java Volume 1
    # dsv.config_weight(0, 0.12, 0.88)
    # dsv.validate_chapter("corejava1.txt")

    # # Core Java Volume 2?
    dsv.config_weight(0, 0.18, 0.82)
    dsv.validate_chapter("corejava2.txt")