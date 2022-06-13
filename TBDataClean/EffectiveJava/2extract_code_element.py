import sys
sys.path.append("..")
import os
import json

from CodeElememtExtactor import CodeElementExtractor
from config import EJPATHUTIL

class TextbookCodeElementExtractor(object):
    def __init__(self):
        self.cee = CodeElementExtractor(refer_api_doc=EJPATHUTIL.jdk_api_doc_path)
    
    def extract_code_element(self, textbook_dir, textbook_code_dir, save_filepath):
        outf = open(save_filepath, "w", encoding="utf-8") 
        for chapter in os.listdir(textbook_dir):
            for section in os.listdir(os.path.join(textbook_dir, chapter)):
                code_texts = ""
                code_dir = os.path.join(textbook_code_dir, chapter, section)
                code_texts = ""
                # code text
                if os.path.exists(code_dir):
                    for filename in os.listdir(code_dir):
                        with open(os.path.join(code_dir, filename), "r", encoding="utf-8") as inf:
                            code_texts += inf.read()
                # textbook text
                with open(os.path.join(textbook_dir, chapter, section), "r", encoding="utf-8") as inf:
                    raw_texts = inf.read()
                
                contained_packages, contained_cis, contained_apis = self.cee.extract_element_in_text(raw_texts + code_texts)
                outf.write("{}\t{}\t{}\t{}\t{}\n".format(
                    chapter, 
                    section, 
                    json.dumps(contained_packages),
                    json.dumps(contained_cis),
                    json.dumps(contained_apis)))

if __name__ == "__main__":
    tcee = TextbookCodeElementExtractor()
    tcee.extract_code_element(EJPATHUTIL.textbook_dir, EJPATHUTIL.textbook_code_dir, EJPATHUTIL.textbook_code_element_path)
