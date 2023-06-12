"""
This file is the same with the CodeElementExtractor.py in the root directory.
But due to the bad code organization, I have to copy this file to this directory for further use.
"""
import os
import json
import re

class CodeElementExtractor(object):
    def __init__(self, refer_api_doc):
        self.refer_packages = dict()
        self.refer_cis = dict()
        with open(refer_api_doc, "r", encoding="utf-8") as inf:
            for line in inf:
                obj = json.loads(line)
                package_name = obj[1]
                ci_name = obj[2]
                api_name = obj[3]
                if api_name == "Method":
                    continue
                if package_name not in self.refer_packages:
                    self.refer_packages[package_name] = set()
                self.refer_packages[package_name].add(ci_name)
                if ci_name not in self.refer_cis:
                    self.refer_cis[ci_name] = set()
                self.refer_cis[ci_name].add(api_name[:api_name.index("(")])
    
    def extract_element_in_text_without_restrict_on_ci(self, text:str, restrict=True):
        contained_packages = dict()
        contained_cis = dict()
        contained_apis = dict()

        for pn in self.refer_packages:
            pn_count = text.count(pn)
            if pn_count > 0:
                contained_packages[pn] = pn_count
        
        for ci in self.refer_cis:
            found_cis = re.findall(r"[^a-zA-Z]" + re.escape(ci) + r"[^a-zA-Z]", text)
            if found_cis:
                contained_cis[ci] = len(found_cis)
        for ci in contained_cis:
            for api in self.refer_cis[ci]:
                mathches = re.findall(r"[^a-zA-Z]" + re.escape(api) + r"\s*?\([\s\S]*?\)", text)
                if mathches:
                    # contained_apis[api] = (ci, len(mathches))
                    contained_apis[api] = len(mathches)
        return contained_packages, contained_cis, contained_apis
    
    def extract_element_in_text(self, text:str, restrict=True):
        contained_packages = dict()
        contained_cis = dict()
        contained_apis = dict()

        for pn in self.refer_packages:
            pn_count = text.count(pn)
            if pn_count > 0:
                contained_packages[pn] = pn_count
        
        for cp in contained_packages:
            for ci in self.refer_packages[cp]:
                found_cis = re.findall(r"[^a-zA-Z]" + re.escape(ci) + r"[^a-zA-Z]", text)
                if found_cis:
                    contained_cis[ci] = len(found_cis)
        
        for ci in contained_cis:
            for api in self.refer_cis[ci]:
                mathches = re.findall(re.escape(api) + r"\([ 1-9a-zA-Z_,]*?\)", text)
                if mathches:
                    contained_apis[api] = (ci, len(mathches))
        return contained_packages, contained_cis, contained_apis