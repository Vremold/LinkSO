import os
import sys
import json

from config import TIJPATHUTIL, WORD_EMBEDDING_CONFIG
from nltk.tokenize import sent_tokenize, word_tokenize
from bert_serving.client import BertClient
import numpy as np

bc = BertClient(check_length=False)

def extract_summary_for_section(textbook_dir, save_filepath):
    outf = open(save_filepath, "w", encoding="utf-8")
    for chapter in os.listdir(textbook_dir):
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            with open(os.path.join(textbook_dir, chapter, section), "r", encoding="utf-8") as inf:
                outf.write("{}\t{}\t{}".format(chapter, section, inf.readline()))
    outf.close()
    pass


def compute_bert_semantic_feature(src_summary_filepath, dst_semantic_filepath):

    outf = open(dst_semantic_filepath, "w", encoding="utf-8")
    with open(src_summary_filepath, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.strip().split("\t")
            chapter = splits[0]
            section = splits[1]
            summary = splits[2]

            sent_cnt = 0
            sent_vecs = bc.encode(sent_tokenize(summary))
            embed = np.average(sent_vecs, axis=0)
            embed = [float(x) for x in embed]

            outf.write("{}\t{}\t{}\n".format(chapter, section, json.dumps(list(embed))))

if __name__ == "__main__":
    # extract_summary_for_section(TIJPATHUTIL.textbook_dir, TIJPATHUTIL.textbook_summary_path)
    compute_bert_semantic_feature(TIJPATHUTIL.textbook_summary_path, TIJPATHUTIL.textbook_bert_semantic_path)