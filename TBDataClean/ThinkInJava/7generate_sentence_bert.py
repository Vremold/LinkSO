import os
import sys
import json

import numpy as np
from sentence_transformers import SentenceTransformer, util

from config import TIJPATHUTIL

bert_model = SentenceTransformer("sentence-transformers/msmarco-distilbert-cos-v5")

def get_a_paragraph_semantic(para):
    para_emb = bert_model.encode(para)
    print(para_emb.shape)
    return para_emb

def get_textbook_semantic(textbook_dir, dst_path):
    result = dict()
    for chapter in os.listdir(textbook_dir):
        if chapter not in result:
            result[chapter] = dict()
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            print("Now processing {}-{}".format(chapter, section))
            with open(os.path.join(textbook_dir, chapter, section), "r", encoding="utf-8") as inf:
                para_cnt = 0
                para_emb = np.zeros(768)
                for line in inf:
                    para_cnt += 1
                    para_emb += get_a_paragraph_semantic(line)
                para_emb /= para_cnt
                result[chapter][section] = list(para_emb)
    with open(dst_path, "w", encoding="utf-8") as outf:
        for chapter in result:
            for section in result[chapter]:
                outf.write("{}\t{}\t{}\n".format(chapter, section, json.dumps(result[chapter][section])))

if __name__ == "__main__":
    get_textbook_semantic(TIJPATHUTIL.textbook_dir, TIJPATHUTIL.textbook_bert_semantic_path)
