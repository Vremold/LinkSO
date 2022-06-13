import os
import sys
import json
import math

from match_config import MATCHPATHUTIL, MATCH_ALGORITHM_CONFIG
from CodeAPIExtractor import CodeParser, APIExtractor
from CodeElememtExtactor import CodeElementExtractor

class APIMatcher(object):
    def __init__(self, textbook_api_filepath):
        self.code_parser = CodeParser()
        self.api_extractor = APIExtractor(MATCHPATHUTIL.jdk_api_doc_path)
        self.section_apis = dict()
        self.chapter_apis = dict()
        self.section_to_chapter = dict()
        with open(textbook_api_filepath, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.split("\t")
                chapter = splits[0]
                section = splits[1]
                code_filename = splits[2]
                apis = json.loads(splits[3])
                if chapter in MATCH_ALGORITHM_CONFIG.EXCLUDED_CHAPTERS:
                    continue
                if section == chapter:
                    continue
                if chapter not in self.section_apis:
                    self.section_apis[chapter] = dict()
                if chapter not in self.chapter_apis:
                    self.chapter_apis[chapter] = dict()
                if section not in self.section_apis[chapter]:
                    self.section_apis[chapter][section] = dict()
                if section not in self.section_to_chapter:
                    self.section_to_chapter[section] = chapter
                for api in apis:
                    if api not in self.chapter_apis[chapter]:
                        self.chapter_apis[chapter][api] = apis[api]
                    if api not in self.section_apis[chapter][section]:
                        self.section_apis[chapter][section][api] = apis[api]
        pass

    def __extract_code_apis(self, soq_codes, soa_codes):
        apis = list()
        packages = list()
        for code in soq_codes + soa_codes:
            class_object_pairs, class_fields, class_method_dics, imports = self.code_parser.parse_code(code=code)
            for class_field, class_method_dic in zip(class_fields, class_method_dics):
                a_apis, a_packages = self.api_extractor.match_api(class_field, class_method_dic, imports)
                apis.extend(a_apis)
                packages.extend(a_packages)
        return apis, packages

    def match_so_in_chapter(self, soq_codes, soa_codes):
        so_apis, so_packages = self.__extract_code_apis(soq_codes, soa_codes)
        chapter_scores = dict()
        for chapter in self.chapter_apis:
            chapter_scores[chapter] = 0
            for api in so_apis:
                chapter_scores[chapter] += self.chapter_apis[chapter].get(api, 0)
        return chapter_scores
    
    def match_so_in_section(self, soq_codes, soa_codes, selected_chapter):
        so_apis, so_packages = self.__extract_code_apis(soq_codes, soa_codes)
        section_scores = dict()
        for section in self.section_apis[selected_chapter]:
            section_scores[section] = 0
            for api in so_apis:
                section_scores[section] += self.section_apis[selected_chapter][section].get(api, 0)
        return section_scores
    
    def match_so_in_section_directly(self, soq_codes, soa_codes):
        so_apis, so_packages = self.__extract_code_apis(soq_codes, soa_codes)

        section_scores = dict()
        for chapter in self.section_apis:
            for section in self.section_apis[chapter]:
                section_scores[section] = 0
                for api in so_apis:
                    section_scores[section] += self.section_apis[chapter][section].get(api, 0)
        return section_scores, self.section_to_chapter