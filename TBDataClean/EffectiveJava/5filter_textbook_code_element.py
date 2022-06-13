import os
import sys
import json
import math

from config import EJPATHUTIL


def load_data():
    chapter_packages = dict()
    chapter_cis = dict()
    chapter_apis = dict()
    with open(EJPATHUTIL.textbook_code_element_path, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.strip().split("\t")
            chapter = splits[0]
            section = splits[1]
            packages = json.loads(splits[2])
            cis = json.loads(splits[3])
            apis = json.loads(splits[4])
            if chapter not in chapter_packages:
                chapter_packages[chapter] = dict()
                chapter_cis[chapter] = dict()
                chapter_apis[chapter] = dict()
            for p in packages:
                if p not in chapter_packages[chapter]:
                    chapter_packages[chapter][p] = 0
                chapter_packages[chapter][p] += packages[p]
            for ci in cis:
                if ci not in chapter_cis[chapter]:
                    chapter_cis[chapter][ci] = 0
                chapter_cis[chapter][ci] += cis[ci]
            for api in apis:
                if api not in chapter_apis[chapter]:
                    chapter_apis[chapter][api] = 0
                chapter_apis[chapter][api] += apis[api][1]
    return chapter_packages, chapter_cis, chapter_apis

def chapter_tf_idf(chapter_items, save_idf_path=""):
    tf = dict()
    for chapter in chapter_items:
        for item in chapter_items[chapter]:
            if item not in tf:
                tf[item] = dict()
            tf[item][chapter] = chapter_items[chapter][item] / sum(chapter_items[chapter].values())
    
    contains = dict()
    for item in tf:
        if item not in contains:
            contains[item] = 0
        for chapter in chapter_items:
            if item in chapter_items[chapter]:
                contains[item] += 1
    
    idf = dict()
    D = len(chapter_items)
    for item in tf:
        idf[item] = math.log(max(D / (contains[item] + 1), 1))
    
    if save_idf_path:
        with open(save_idf_path, "a+", encoding="utf-8") as outf:
            outf.write(json.dumps(idf) + "\n")

    tfidf = dict()
    for item in tf:
        if item not in tfidf:
            tfidf[item] = dict()
        for chapter in tf[item]:
            tfidf[item][chapter] = tf[item][chapter] * idf[item]
    
    return tfidf

def write_back():
    chapter_packages, chapter_cis, chapter_apis = load_data()
    package_tfidf = chapter_tf_idf(chapter_packages, save_idf_path=EJPATHUTIL.textbook_code_element_idf_path)
    ci_tfidf = chapter_tf_idf(chapter_cis, save_idf_path=EJPATHUTIL.textbook_code_element_idf_path)
    api_tfidf = chapter_tf_idf(chapter_apis, save_idf_path=EJPATHUTIL.textbook_code_element_idf_path)

    with open(EJPATHUTIL.textbook_code_element_path, "r", encoding="utf-8") as inf, open(EJPATHUTIL.textbook_filtered_code_element_path, "w", encoding="utf-8") as outf:
        for line in inf:
            splits = line.strip().split("\t")
            chapter = splits[0]
            section = splits[1]
            packages = json.loads(splits[2])
            cis = json.loads(splits[3])
            apis = json.loads(splits[4])
            new_packages = dict()
            new_cis = dict()
            new_apis = dict()
            for p in packages:
                new_packages[p] = package_tfidf[p][chapter]
            for ci in cis:
                new_cis[ci] = ci_tfidf[ci][chapter]
            for api in apis:
                new_apis[api] = api_tfidf[api][chapter]
            outf.write("{}\t{}\t{}\t{}\t{}\n".format(chapter, section, json.dumps(new_packages), json.dumps(new_cis), json.dumps(new_apis)))

if __name__ == "__main__":
    write_back()