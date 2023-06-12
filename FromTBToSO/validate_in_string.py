import os
import sys
import csv
import json
import pickle
import math
import numpy as np

suffix_str = "_string"

def load_containing_string_so_posts(cache_file="./cache/cached_so_posts{}.pkl".format(suffix_str)):
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as inf:
            return pickle.load(inf)
    
    results = list()
    with open("../SODataClean/so_posts.csv", "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf)
        # Qid,AAid,Qtitle,Qbody,Qcode,Qtags,Aid,Abody,Acode
        for line in csv_reader:
            if len(line) < 6:
                continue
            if "string" in line[5]:
                results.append(line)
    
    with open(cache_file, "wb") as outf:
        pickle.dump(results, outf)
    return results

'''So Bert Semantic'''
from sentence_transformers import SentenceTransformer, util
class SoBertSemanticExtractor(object):
    def __init__(self):
        self.bm = SentenceTransformer("sentence-transformers/msmarco-distilbert-cos-v5")
    
    def bert_semantic(self, soq_title, soq_body, soa_body):
        return self.bm.encode(soq_title+soq_body+soa_body)

    def get_so_semantic(self, cache_file="./cache/cached_so_semantics{}.pkl".format(suffix_str)):
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as inf:
                return pickle.load(inf)
        sos = load_containing_string_so_posts()
        results = dict()
        for so in sos:
            soq_id = int(so[0])
            soq_title = so[2]
            soq_body = so[3]
            soa_body = so[7]
            so_semantic = self.bert_semantic(soq_title, soq_body, soa_body)
            
            results[soq_id] = so_semantic
        
        with open(cache_file, "wb") as outf:
            pickle.dump(results, outf)
        return results

'''So Code Element Feature'''
from CodeElememtExtactor import CodeElementExtractor
from match_config import MATCHPATHUTIL
class SoCodeElementExtractor(object):
    def __init__(self, textbook_code_element_idf_path=MATCHPATHUTIL.textbook_code_element_idf_path):
        self.cee = CodeElementExtractor(MATCHPATHUTIL.jdk_api_doc_path)

        with open(textbook_code_element_idf_path, "r", encoding="utf-8") as inf:
            self.package_idf = json.loads(inf.readline())
            self.ci_idf = json.loads(inf.readline())
            self.api_idf = json.loads(inf.readline())
    
    def code_element(self, soq_body, soq_codes, soa_body, soa_codes):
        so_texts = "{} {} {} {}".format(soq_body, " ".join(soq_codes), soa_body, " ".join(soa_codes))
        contained_packages, contained_cis, contained_apis = self.cee.extract_element_in_text_without_restrict_on_ci(so_texts)
        
        package_tf = dict()
        ci_tf = dict()
        api_tf = dict()

        for p in contained_packages:
            package_tf[p] = contained_packages[p] / sum(contained_packages.values())
        for ci in contained_cis:
            ci_tf[ci] = contained_cis[ci] / sum(contained_cis.values())
        for api in contained_apis:
            api_tf[api] = contained_apis[api] / sum(contained_apis.values())

        package_tfidf = dict()
        ci_tfidf = dict()
        api_tfidf = dict()

        for p in package_tf:
            package_tfidf[p] = package_tf[p] * self.package_idf.get(p, 1)
        for ci in ci_tf:
            ci_tfidf[ci] = ci_tf[ci] * self.ci_idf.get(ci, 1)
        for api in api_tf:
            api_tfidf[api] = api_tf[api] * self.api_idf.get(api, 1)
        
        return package_tfidf, ci_tfidf, api_tfidf

    def get_so_code_element(self, cache_file="./cache/cached_so_code_element{}.pkl".format(suffix_str)):
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as inf:
                return pickle.load(inf)
        
        sos = load_containing_string_so_posts()
        results = dict()
        for so in sos:
            soq_id = int(so[0])
            print("Now processing SO:", soq_id)
            soq_body = so[3]
            soq_codes = so[4]
            soa_body = so[7]
            soa_codes = so[8]
            package_tfidf, ci_tfidf, api_tfidf = self.code_element(soq_body, soq_codes, soa_body, soa_codes)
        
            results[soq_id] = (package_tfidf, ci_tfidf, api_tfidf)
        
        with open(cache_file, "wb") as outf:
            pickle.dump(results, outf)
        
        return results

class TextbookMatcher(object):
    def __init__(self):
        self.socee = SoCodeElementExtractor()
        self.sose = SoBertSemanticExtractor()
        pass
    
    def __cosine_similarity_between_two_dict(self, dic1, dic2):
        dis1, dis2 = 0, 0
        for v in dic1.values():
            # print(v)
            dis1 += v * v
        for v in dic2.values():
            dis2 += v * v
        
        cos = 0
        for k in dic1:
            if k in dic2:
                cos += dic1[k] * dic2[k]
        coss = cos / (math.sqrt(dis1) * math.sqrt(dis1) + 0.000000001)
        return (coss + 1) / 2

    def __cos_sim(self, a, b):
        a = np.array(a)
        b = np.array(b)
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        cos = (np.dot(a, b) / (a_norm * b_norm) + 1) / 2
        return cos

    def match_in_textbook(self, textbook_code_element_path, textbook_semantics_filepath, chapter="Strings", section="Regular expressions"):
        # Code element feature
        
        p_feature = dict()
        ci_feature = dict()
        api_feature = dict()
        with open(textbook_code_element_path, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.strip().split("\t")
                if splits[0] == chapter and splits[1] == section:
                    packages = json.loads(splits[2])
                    cis = json.loads(splits[3])
                    apis = json.loads(splits[4])
                    p_feature = packages
                    ci_feature = cis
                    api_feature = {key: val[1] for key, val in apis.items()}
                    break
        
        # Bert semantic
        semantic_feature = None
        with open(textbook_semantics_filepath, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.strip().split("\t")
                if chapter == splits[0] and section == splits[1]:
                    semantic_feature = np.array(json.loads(splits[2]))
                    break
        
        # Match with stack overflow
        so_ces = self.socee.get_so_code_element()
        so_ss = self.sose.get_so_semantic()

        so_scores = dict()
        for soq_id in so_ss:
            print("Now procssing SO:", soq_id)
            semantic_f = so_ss[soq_id]
            (package_f, ci_f, api_f) = so_ces[soq_id]
            so_scores[soq_id] = 0.9 * self.__cos_sim(semantic_feature, semantic_f) + (
                self.__cosine_similarity_between_two_dict(package_f, p_feature) +
                self.__cosine_similarity_between_two_dict(ci_f, ci_feature) + 
                self.__cosine_similarity_between_two_dict(api_f, api_feature)
            ) / 3 * 0.1

        so_scores = sorted(so_scores.items(), key=lambda x : x[1], reverse=True)
        print(so_scores[:4])
        with open("./cache/validate_string_think_in_java.pkl", "wb") as outf:
            pickle.dump(so_scores, outf)    



if __name__ == "__main__":
    # Think In Java
    # Regular Expression: [(14683811, 3.517720420542995), (36407757, 3.2875230782646936), (19128108, 3.1993824967154234)]
    ## Overloading ‘+’ vs. StringBuilder: [(19129066, 2.9905501168271753), (33074000, 2.924056290835614), (38196808, 2.904173528138416)]
    textbook_code_element_path = "/media/dell/disk/wujw/linkso/TextbookFeature/ThinkInJava/code_elements.txt"
    textbook_semantic_path = "/media/dell/disk/wujw/linkso/TextbookFeature/ThinkInJava/bert_semantics.txt"
    chapter = "Strings"
    section = "Overloading ‘+’ vs. StringBuilder"
    TextbookMatcher().match_in_textbook(textbook_code_element_path, textbook_semantic_path, chapter, section)
    

    # Core Java Volume 1
    # [(9989414, 3.6251817498518255), (44089700, 3.6149568655290585), (25327393, 3.596580309950686)]
    # textbook_code_element_path = "/media/dell/disk/wujw/linkso/TextbookFeature/CoreJavaVolume1/code_elements.txt"
    # textbook_semantic_path = "/media/dell/disk/wujw/linkso/TextbookFeature/CoreJavaVolume1/bert_semantics.txt"
    # chapter = "Fundamental Programming Structures in Java"
    # section = "Strings"
    # TextbookMatcher().match_in_textbook(textbook_code_element_path, textbook_semantic_path, chapter, section)