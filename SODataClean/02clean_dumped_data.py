import os
import sys
import time
import pickle
import json
import csv
import re

from config import PATHUTIL

class DataCleaner():
    def __init__(self):
        self.special_tokens = {
            "&#xA;": "",
            "&gt;": ">",
            "&lt;": "<"
        }

    def remove_special_tokens(self, text:str):
        for special_token in self.special_tokens:
            text = text.replace(special_token, self.special_tokens[special_token])
        return text
    
    def remove_code_block(self, text:str):
        code_blocks = []
        for match in re.finditer(r"<pre><code>([\s\S]*?)</code></pre>", text, re.M):
            code_blocks.append(match.group(1))
        text = re.sub(r"<pre><code>[\s\S]*?</code></pre>", "--CODE--", text)
        return text, code_blocks
    
    def get_duplicate_infomation(self, text:str):
        is_duplicate = False
        duplicate_to = None
        match = re.search(r"<blockquote>[\s\S]*?Possible Duplicate:[\s\S]*?<a href=([\s\S]*?)>[\s\S]*?</blockquote>", text)
        if match:
            is_duplicate = True
            duplicate_to = match.group(1)
            return is_duplicate, duplicate_to, re.sub(r"<blockquote>[\s\S]*?Possible Duplicate:[\s\S]*?<a href=([\s\S]*?)>[\s\S]*?</blockquote>", "", text)
        return is_duplicate, duplicate_to, text
    
    def remove_link_tags(self, text):
        text = re.sub(r"<a[\s\S]*?href=(.*?)\s[\s\S]*?>([\s\S]*?)</a>", r"[\2](\1)", text)
        return text
    
    def remove_html_tags(self, text):
        return re.sub(r"<[\s\S]*?>", "", text)

    def clean_data(self, text):
        text = self.remove_special_tokens(text)
        text, code_blocks = self.remove_code_block(text)
        is_duplicate, duplicate_to, text = self.get_duplicate_infomation(text)
        text = self.remove_link_tags(text)
        text = self.remove_html_tags(text)
        return text, json.dumps(code_blocks, ensure_ascii=False), is_duplicate, duplicate_to
    
if __name__ == "__main__":
    dc = DataCleaner()
    src_so_filepath = os.path.join(PATHUTIL.cache_dir, "dumped_so.csv")
    dst_so_filepath = PATHUTIL.raw_so_path
    dst_duplicate_so_filepath = PATHUTIL.raw_duplicate_so_path
    with open(src_so_filepath, "r", encoding="utf-8") as inf, open(dst_so_filepath, "w", encoding="utf-8") as outf, open(dst_duplicate_so_filepath, "w", encoding="utf-8") as duplicate_outf:
        next(inf)
        outf.write("Qid,AAid,Qtitle,Qbody,Qcode,Qtags,Aid,Abody,Acode\n")
        duplicate_outf.write("Qid,AAid,Qtitle,Qbody,Qcode,Qtags,Aid,Abody,Acode,DuplicateTo\n")
        csv_reader = csv.reader(inf)
        csv_writer = csv.writer(outf)
        duplicate_csv_writer = csv.writer(duplicate_outf)
        for line in csv_reader:
            question_text, question_code, is_duplicate, duplicate_to = dc.clean_data(line[3])
            answer_text, answer_code, _, _ = dc.clean_data(line[6])
            if not is_duplicate:
                csv_writer.writerow([line[0], line[1], line[2], question_text, question_code, line[4], line[5], answer_text, answer_code])
            else:
                duplicate_csv_writer.writerow([line[0], line[1], line[2], question_text, question_code, line[4], line[5], answer_text, answer_code, duplicate_to])