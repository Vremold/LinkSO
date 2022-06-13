import os
import json
import sys
import csv

import pke
from nltk.corpus import stopwords
import string

from config import MPRANK_CONFIG, CJ1PATHUTIL

def mprank_textbook_section(textbook_dir, save_filepath):
    stoplist = list(string.punctuation)
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    stoplist += stopwords.words('english')
    stoplist += MPRANK_CONFIG.DEFAULT_STOPWORDS

    crawled_sections = dict()
    with open(save_filepath, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.split("\t")
            if (splits[0] not in crawled_sections):
                crawled_sections[splits[0]] = list()
            crawled_sections[splits[0]].append(splits[1])

    outf = open(save_filepath, "a+", encoding="utf-8")
    for chapter in os.listdir(textbook_dir):
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            if chapter in crawled_sections and section in crawled_sections[chapter]:
                continue
            print("[mprank_textbook_section] now processing {}".format(os.path.join(textbook_dir, chapter, section)))

            extractor = pke.unsupervised.MultipartiteRank()
            extractor.load_document(os.path.join(textbook_dir, chapter, section))

            extractor.candidate_selection(grammar=MPRANK_CONFIG.NP_GRAMMER, maximum_word_number=MPRANK_CONFIG.MAX_NP_WORD_COUNT, stopwords=stoplist, remove_url=True)
            extractor.candidate_weighting(
                alpha=1.3, threshold=0.74, method='average')
            keyphrases = extractor.get_n_best(n=20)
            
            outf.write("{}\t{}\t{}\n".format(chapter, section, json.dumps(keyphrases, ensure_ascii=False)))


def mprank_textbook_chapter(textbook_dir, save_filepath):

    stoplist = list(string.punctuation)
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    stoplist += stopwords.words('english')
    
    stoplist += MPRANK_CONFIG.DEFAULT_STOPWORDS

    crawled_chapter = set()
    if os.path.exists(save_filepath):
        with open(save_filepath, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.split("\t")
                crawled_chapter.add(splits[0])

    outf = open(save_filepath, "a+", encoding="utf-8")
    
    for chapter in os.listdir(textbook_dir):
        if chapter in crawled_chapter:
            continue
        
        print("[mprank_textbook_chapter] now processing {}".format(os.path.join(textbook_dir, chapter)))
        
        chapter_text = ""
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            with open(os.path.join(textbook_dir, chapter, section), "r", encoding="utf-8") as inf:
                chapter_text += inf.read()
        
        extractor = pke.unsupervised.MultipartiteRank()
        extractor.load_document(chapter_text)

        extractor.candidate_selection(grammar=MPRANK_CONFIG.NP_GRAMMER, maximum_word_number=MPRANK_CONFIG.MAX_NP_WORD_COUNT, stopwords=stoplist, remove_url=True)

        extractor.candidate_weighting(
            alpha=1.3, threshold=0.74, method='average')
        keyphrases = extractor.get_n_best(n=50)
        
        outf.write("{}\t{}\n".format(chapter, json.dumps(keyphrases, ensure_ascii=False)))

def truncate_file(filepath):
    with open(filepath, "w", encoding="utf-8") as outf:
        outf.truncate()

if __name__ == "__main__":
    truncate_file(CJ1PATHUTIL.textbook_key_phrase_for_section_path)
    mprank_textbook_section(CJ1PATHUTIL.textbook_dir, CJ1PATHUTIL.textbook_key_phrase_for_section_path)
    # truncate_file(CJ1PATHUTIL.textbook_key_phrase_for_chapter_path)
    # mprank_textbook_chapter(CJ1PATHUTIL.textbook_dir, CJ1PATHUTIL.textbook_key_phrase_for_chapter_path)