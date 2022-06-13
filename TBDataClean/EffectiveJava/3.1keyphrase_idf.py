import os
import json
import sys
import csv
import math

import pke
from nltk.corpus import stopwords
import string

from config import MPRANK_CONFIG, EJPATHUTIL

def keyphrase_chapter_idf():
    chapter_kws = dict()
    with open(EJPATHUTIL.textbook_key_phrase_for_chapter_path, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.strip().split("\t")
            chapter = splits[0]
            kws = json.loads(splits[1])
            chapter_kws[chapter] = kws
    
    kw_contains = dict()
    for chapter in chapter_kws:
        for [kw, importance] in chapter_kws[chapter]:
            if kw not in kw_contains:
                kw_contains[kw] = 0
            kw_contains[kw] += 1
    
    D = len(chapter_kws)
    kw_idf = dict()
    for kw in kw_contains:
        kw_idf[kw] = math.log(D / kw_contains[kw])
    
    with open(EJPATHUTIL.textbook_key_phrase_idf_path, "w", encoding="utf-8") as outf:
        json.dump(kw_idf, outf)
            
if __name__ == "__main__":
    keyphrase_chapter_idf()