import os
import sys
import json
import math

from match_config import MATCHPATHUTIL, MATCH_ALGORITHM_CONFIG
from CodeAPIExtractor import CodeParser, APIExtractor
from CodeElememtExtactor import CodeElementExtractor

class CodeElementMatcher(object):
    def __init__(self, textbook_code_element_path, textbook_code_element_idf_path):
        self.cee = CodeElementExtractor(MATCHPATHUTIL.jdk_api_doc_path)
        self.chapter_code_elements = dict()
        self.section_code_elements = dict()
        self.section_to_chapter = dict()

        with open(textbook_code_element_idf_path, "r", encoding="utf-8") as inf:
            self.package_idf = json.loads(inf.readline())
            self.ci_idf = json.loads(inf.readline())
            self.api_idf = json.loads(inf.readline())
        
        with open(textbook_code_element_path, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.strip().split("\t")
                chapter = splits[0]
                section = splits[1]
                packages = json.loads(splits[2])
                cis = json.loads(splits[3])
                apis = json.loads(splits[4])

                # 初始化时，将不需要匹配的章节扣除在外
                if chapter in MATCH_ALGORITHM_CONFIG.EXCLUDED_CHAPTERS:
                    continue
                if section == chapter:
                    continue
                if section in MATCH_ALGORITHM_CONFIG.EXCLUDED_SECTIONS:
                    continue
                if chapter not in self.chapter_code_elements:
                    self.chapter_code_elements[chapter] = [dict(), dict(), dict()]
                    self.section_code_elements[chapter] = dict()
                if section not in self.section_code_elements[chapter]:
                    self.section_code_elements[chapter][section] = [dict(), dict(), dict()]
                if section not in self.section_to_chapter:
                    self.section_to_chapter[section] = chapter
                for p in packages:
                    if p not in self.chapter_code_elements[chapter][0]:
                        self.chapter_code_elements[chapter][0][p] = packages[p]
                    if p not in self.section_code_elements[chapter][section][0]:
                        self.section_code_elements[chapter][section][0][p] = packages[p]
                
                for ci in cis:
                    if ci not in self.chapter_code_elements[chapter][1]:
                        self.chapter_code_elements[chapter][1][ci] = cis[ci]
                    if ci not in self.section_code_elements[chapter][section][1]:
                        self.section_code_elements[chapter][section][1][ci] = cis[ci]
                
                for api in apis:
                    if api not in self.chapter_code_elements[chapter][2]:
                        self.chapter_code_elements[chapter][2][api] = apis[api][1]
                    if api not in self.section_code_elements[chapter][section][2]:
                        self.section_code_elements[chapter][section][2][api] = apis[api][1]
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

    def match_so_in_chapter_direct(self, soq_body, soq_codes, soa_body, soa_codes):
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
        
        chapter_scores = dict()
        # section_scores = dict()
        for chapter in self.section_code_elements:
            for section in self.section_code_elements[chapter]:
                package_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[chapter][section][0], package_tfidf)
                ci_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[chapter][section][1], ci_tfidf)
                api_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[chapter][section][2], api_tfidf)

                tmp = (package_scores + ci_scores + api_scores) / 3
                if chapter not in chapter_scores or chapter_scores[chapter] < tmp:
                    chapter_scores[chapter] = tmp
        return chapter_scores
    
    def match_so_in_chapter(self, soq_body, soq_codes, soa_body, soa_codes, direct=False):
        if direct:
            return self.match_so_in_chapter_direct(soq_body, soq_codes, soa_body, soa_codes)
        so_texts = "{} {} {} {}".format(soq_body, " ".join(soq_codes), soa_body, " ".join(soa_codes))
        contained_packages, contained_cis, contained_apis = self.cee.extract_element_in_text_without_restrict_on_ci(so_texts)
        # print(contained_packages, contained_cis, contained_apis, sep="\n")

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
        
        chapter_scores = dict()
        for chapter in self.chapter_code_elements:
            package_scores = self.__cosine_similarity_between_two_dict(self.chapter_code_elements[chapter][0], package_tfidf)
            ci_scores = self.__cosine_similarity_between_two_dict(self.chapter_code_elements[chapter][1], ci_tfidf)
            api_scores = self.__cosine_similarity_between_two_dict(self.chapter_code_elements[chapter][2], api_tfidf)

            # TODO: 这是一个可配置项，要不要匹配API
            chapter_scores[chapter] = (package_scores + ci_scores + api_scores) / 3
        
        return chapter_scores

    def match_so_in_section(self, soq_body, soq_codes, soa_body, soa_codes, selected_chapter):
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
        
        section_scores = dict()
        for section in self.section_code_elements[selected_chapter]:
            if section == selected_chapter:
                continue
            package_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[selected_chapter][section][0], package_tfidf)
            ci_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[selected_chapter][section][1], ci_tfidf)
            api_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[selected_chapter][section][2], api_tfidf)

            # TODO: 这是一个可配置项，要不要匹配API
            section_scores[section] = (package_scores + ci_scores + api_scores) / 3
        
        return section_scores

    def match_so_in_section_directly(self, soq_body, soq_codes, soa_body, soa_codes):
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
        
        section_scores = dict()
        for chapter in self.section_code_elements:
            for section in self.section_code_elements[chapter]:
                package_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[chapter][section][0], package_tfidf)
                ci_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[chapter][section][1], ci_tfidf)
                api_scores = self.__cosine_similarity_between_two_dict(self.section_code_elements[chapter][section][2], api_tfidf)

                # TODO: 这是一个可配置项，要不要匹配API
                section_scores[section] = (package_scores + ci_scores + api_scores) / 3
        
        return section_scores, self.section_to_chapter
