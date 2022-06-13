import os
import sys
import json
import pickle
import math
import re

import spacy

from config import TIJPATHUTIL

nlp = spacy.load("en_core_web_md")

def resovle_noun_phrase(resolved_np):
    resolved_np = resolved_np.replace(" 's", "'s")
    resolved_np = resolved_np.replace(" - ", "-")
    resolved_np = resolved_np.replace(" ( )", "()")
    resolved_np = re.sub(r"\\u[0-9a-z]{4}", "", resolved_np)
    if "www" in resolved_np or "http:" in resolved_np or "https:" in resolved_np:
        return ""
    return resolved_np.strip()

def extract_noun_phrases_from_text(text):
    nps = list()
    doc = nlp(text)
    for sent in doc.sents:
        for np in sent.noun_chunks:
            resolved_np = ""
            for token in np:
                # print(token.pos_)
                if token.pos_ == "PRON" or token.pos_ == "DET" or token.pos_ == "SPACE":
                    continue
                resolved_np += token.lemma_ + " "
            if resolved_np:
                nps.append(resovle_noun_phrase(resolved_np))
    return nps

def extract_noun_phrases(textbook_dir, save_file):
    result = dict()
    for chapter in os.listdir(textbook_dir):
        if chapter not in result:
            result[chapter] = dict()
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            if section not in result[chapter]:
                result[chapter][section] = list()

            print(f"{chapter}-{section}")
            # extract keyphrase in section titles
            result[chapter][section] = extract_noun_phrases_from_text(section)
            with open(os.path.join(textbook_dir, chapter, section), "r", encoding="utf-8") as inf:
                line = inf.readline()
                result[chapter][section] += extract_noun_phrases_from_text(line)
    with open(save_file, "w", encoding="utf-8") as outf:
        json.dump(result, outf)

def refine_nouns(nouns_file):
    def refine(noun):
        useless_adjs = ["much", "big", ]
        noun = noun.replace("—", "-")
        noun = re.sub(r"[”\"“,'‘’\(\)]+", "", noun)
        noun = re.sub(r" +", " ", noun)
        return noun.strip()
        # noun = re.sub(pattern, repl, string)
    with open(nouns_file, "r", encoding="utf-8") as inf:
        obj = json.load(inf)
    result = dict()
    for chapter in obj:
        if chapter not in result:
            result[chapter] = dict()
        for section in obj[chapter]:
            if section not in result[chapter]:
                result[chapter][section] = list()
            for noun in obj[chapter][section]:
                refined_noun = refine(noun)
                if refined_noun:
                    result[chapter][section].append(refined_noun)
    with open(nouns_file, "w", encoding="utf-8") as outf:
        json.dump(result, outf)

def tfidf_analysis(noun_file, chapter_keyphrase_path, section_keyphrase_path):
    with open(noun_file, "r", encoding="utf-8") as inf:
        obj = json.load(inf)
    word_idx = dict()
    word_freq = dict()
    for chapter in obj:
        if chapter not in word_freq:
            word_freq[chapter] = dict()
        for section in obj[chapter]:
            for word in obj[chapter][section]:
                if word not in word_idx:
                    word_idx[word] = len(word_idx)
                if word not in word_freq[chapter]:
                    word_freq[chapter][word] = 0
                word_freq[chapter][word] += 1
    tf = dict()
    for chapter in word_freq:
        tmp = sum(word_freq[chapter].values())
        for word in word_freq[chapter]:
            if word not in tf:
                tf[word] = dict()
            tf[word][chapter] = word_freq[chapter][word] / tmp
    
    word_contains = dict()
    for word in tf:
        if word not in word_contains:
            word_contains[word] = 0
        for chapter in word_freq:
            if word in word_freq[chapter]:
                word_contains[word] += 1
    
    idf = dict()
    D = len(word_freq)
    for word in tf:
        idf[word] = math.log(D / (word_contains[word]))

    tf_idf = dict()
    for word in tf:
        if word not in tf_idf:
            tf_idf[word] = dict()
        for chapter in tf[word]:
            tf_idf[word][chapter] = tf[word][chapter] * idf[word]
    
    chapter_outf = open(chapter_keyphrase_path, "w", encoding="utf-8")
    section_outf = open(section_keyphrase_path, "w", encoding="utf-8")
    chapter_keyphrases = dict()
    for chapter in obj:
        chapter_kws = dict()
        for section in obj[chapter]:
            section_kws = dict()
            for kw in obj[chapter][section]:
                section_kws[kw] = tf_idf[kw][chapter]
                chapter_kws[kw] = tf_idf[kw][chapter]
            section_outf.write("{}\t{}\t{}\n".format(chapter, section, json.dumps(list(section_kws.items()))))
        chapter_outf.write("{}\t{}\n".format(chapter, json.dumps(list(chapter_kws.items()))))

if __name__ == "__main__":
    '''First step'''
    # extract_noun_phrases("../data/textbook", "../tmp/TIJNouns.json")
    # '''Second step'''
    # refine_nouns("../tmp/TIJNouns.json")
    '''Third step'''
    tfidf_analysis("../tmp/TIJNouns.json", TIJPATHUTIL.textbook_key_phrase_for_chapter_path, TIJPATHUTIL.textbook_key_phrase_for_section_path)
    pass