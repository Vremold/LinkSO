"""
    目标：将从章节中抽取的源代码根据他们的命名匹配到找到的代码
    可选：因为我找到了TIJ教材的代码
"""

import os
import sys
import json
import pickle

sys.path.append("..")

from CodeAPIExtractor import CodeParser, APIExtractor
from config import TIJPATHUTIL

class CodeSnippetMatcherToGiven:
    def __init__(self, given_code_dir):
        self.given_codes = dict()
        self.__load_given_code(given_code_dir)
        pass

    def __load_given_code(self, given_code_dir):
        for package in os.listdir(given_code_dir):
            package_path = os.path.join(given_code_dir, package)
            if os.path.isdir(package_path):
                self.__load_given_code(package_path)
            if package.endswith(".java"):
                with open(package_path, "r", encoding="utf-8") as inf:
                    codename = next(inf)
                    codename = codename.strip().replace("//: ", "")
                    self.given_codes[codename] = inf.read()

    def match(self, textbook_code_dir):
        for chapter in os.listdir(textbook_code_dir):
            for section in os.listdir(os.path.join(textbook_code_dir, chapter)):
                code_filepath = os.path.join(textbook_code_dir, chapter, section)
                if not os.path.isfile(code_filepath):
                    continue
                inf = open(code_filepath, "r", encoding="utf-8")
                code_snippets = inf.readlines()
                inf.close()
                os.remove(code_filepath)

                for code_snippet in code_snippets:
                    name = code_snippet.strip().split(" ")[1]
                    if name in self.given_codes:
                        save_code_dir = os.path.join(textbook_code_dir, chapter, section)
                        if not os.path.exists(save_code_dir) or not os.path.isdir(save_code_dir):
                            os.mkdir(save_code_dir)
                        with open(os.path.join(save_code_dir, name.split("/")[-1]), "w", encoding="utf-8") as outf:
                            outf.write(self.given_codes[name])

class TextbookCodeAPIExtractor(object):
    def __init__(self, api_doc_file=TIJPATHUTIL.jdk_api_doc_path):
        self.code_parser = CodeParser()
        self.api_extractor = APIExtractor(TIJPATHUTIL.jdk_api_doc_path)

    def extract_api(self, textbook_dir, save_filepath):
        outf = open(save_filepath, "w", encoding="utf-8")
        for chapter in os.listdir(textbook_dir):
            for section in os.listdir(os.path.join(textbook_dir, chapter)):
                for code_filename in os.listdir(os.path.join(textbook_dir, chapter, section)):
                    if not code_filename.endswith(".java"):
                        continue
                    code_filepath = os.path.join(os.path.join(textbook_dir, chapter, section, code_filename))
                    with open(code_filepath, "r", encoding="utf-8") as inf:
                        code = inf.read()
                    
                    apis = list()
                    packages = list()
                    class_object_pairs, class_fields, class_method_dics, imports = self.code_parser.parse_code(code=code)
                    for class_field, class_method_dic in zip(class_fields, class_method_dics):
                        a_apis, a_packages = self.api_extractor.match_api(class_field, class_method_dic, imports)
                        apis.extend(a_apis)
                        packages.extend(a_packages)
                    
                    outf.write("{}\t{}\t{}\t{}\t{}\n".format(chapter, section, code_filename, json.dumps(apis, ensure_ascii=False), json.dumps(packages, ensure_ascii=False)))
        outf.close()

if __name__ == "__main__":
    # csmtg = CodeSnippetMatcherToGiven(TIJPATHUTIL.raw_textbook_code_dir)
    # csmtg.match(TIJPATHUTIL.textbook_code_dir)
    tcae = TextbookCodeAPIExtractor()
    tcae.extract_api(TIJPATHUTIL.textbook_code_dir, TIJPATHUTIL.textbook_api_path)