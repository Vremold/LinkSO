import os
import sys
import json
import math

from .config import TIJPATHUTIL

def load_api():
    chapter_apis = dict()
    with open(TIJPATHUTIL.textbook_api_path, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.split("\t")
            chapter = splits[0]
            apis = json.loads(splits[-2])
            if chapter not in chapter_apis:
                chapter_apis[chapter] = list()
            chapter_apis[chapter].extend(apis)

    return chapter_apis


def tf_idf():
    chapter_apis = load_api()
    # print(chapter_apis)
    api_freq = dict()
    for chapter in chapter_apis:
        if chapter not in api_freq:
            api_freq[chapter] = dict()
        for api in chapter_apis[chapter]:
            if api not in api_freq[chapter]:
                api_freq[chapter][api] = 0
            api_freq[chapter][api] += 1

    apitf = dict()
    for chapter in api_freq:
        for api in api_freq[chapter]:
            if api not in apitf:
                apitf[api] = dict()
            apitf[api][chapter] = api_freq[chapter][api] / sum(api_freq[chapter].values())
    
    api_contains = dict()
    for api in apitf:
        if api not in api_contains:
            api_contains[api] = 0
        for chapter in api_freq:
            if api in api_freq[chapter]:
                api_contains[api] += 1
    
    apiidf = dict()
    D = len(api_freq)
    for api in apitf:
        apiidf[api] = math.log(max(D / (api_contains[api] + 1), 1))
    
    apitfidf = dict()
    for api in apitf:
        apitfidf[api] = dict()
        for chapter in apitf[api]:
            apitfidf[api][chapter] = apitf[api][chapter] * apiidf[api]
    
    return apitfidf

def write_back_api():
    apitfidf = tf_idf()
    with open(TIJPATHUTIL.textbook_api_path, "r", encoding="utf-8") as inf, open(TIJPATHUTIL.textbook_filtered_api_path, "w", encoding="utf-8") as outf:
        for line in inf:
            splits = line.split("\t")
            chapter = splits[0]
            section = splits[1]
            code_filename = splits[2]
            apis = json.loads(splits[3])
            new_apis = dict()
            for api in set(apis):
                new_apis[api] = apitfidf[api][chapter]
            outf.write("{}\t{}\t{}\t{}\n".format(chapter, section, code_filename, json.dumps(new_apis)))

if __name__ == "__main__":
    write_back_api()