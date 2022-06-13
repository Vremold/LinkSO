import os
import sys
import json
import re

from config import EJPATHUTIL

SENT_END_SYMBLE = [".", ";", "?", "}", "!", "...", '"']

class TextbookContentExtractor(object):
    def __init__(self, raw_textbook_file, content_file):
        self.raw_textbook_file = raw_textbook_file
        self.cache_dir = EJPATHUTIL.cache_dir
        self.item_idx = 1
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        
        with open(content_file, "r", encoding="utf-8") as inf:
            self.expected_chapter_to_items = json.load(inf)
            self.expected_chapters = list(self.expected_chapter_to_items.keys())

    def __remove_unseen_chars(self, line:str) -> str:
        return "".join([x for x in line if x.isprintable()])
    
    def remove_chapter_useless_lines(self, lines, chapter_name:str):
        lines = [self.__remove_unseen_chars(line) for line in lines]
        ret_lines = list()
        for line in lines:
            if re.match(r"\d+$", line):
                continue
            if re.match(r"CHAPTER \d+$", line):
                continue
            if line.startswith(chapter_name.upper()) or chapter_name.upper().startswith(line):
                continue
            if re.match(r"ITEM \d+: ", line):
                continue
            ret_lines.append(line)

        return ret_lines

    def extract_content_from_raw_textbook(self):
        with open(self.raw_textbook_file, "r", encoding="utf-8") as inf:
            text = inf.read()
        chapters = re.split(r"C H A P T E R\n\n\d+", text)[1:]
        for i, chapter_text in enumerate(chapters):
            chapter_name = self.expected_chapters[i]
            print("chapter_name:", chapter_name, sep="")
            save_chapter_dir = os.path.join(self.cache_dir, self.expected_chapters[i])
            if not os.path.exists(save_chapter_dir):
                os.mkdir(save_chapter_dir)
            
            chapter_lines = chapter_text.split("\n")
            chapter_lines = self.remove_chapter_useless_lines(chapter_lines, self.expected_chapters[i])

            line_idx = 0
            max_lines = len(chapter_lines)

            # skip chapter title line
            while line_idx < max_lines and chapter_lines[line_idx] != self.expected_chapters[i]:
                line_idx += 1
            line_idx += 1

            # chapter introduction text
            chapter_intro_lines = []
            while line_idx < max_lines and not chapter_lines[line_idx].startswith("Item {}:".format(self.item_idx)):
                chapter_intro_lines.append(chapter_lines[line_idx])
                line_idx += 1
            with open(os.path.join(save_chapter_dir, "Introduction"), "w", encoding="utf-8") as outf:
                outf.writelines([line + "\n" for line in chapter_intro_lines])
            
            
            for item_name in self.expected_chapter_to_items[self.expected_chapters[i]]:
                item_lines = []

                if line_idx < max_lines:
                    print(line_idx, chapter_lines[line_idx])
                else:
                    print(line_idx)

                # skip item name
                while line_idx < max_lines:
                    if not "Item {}: {}".format(self.item_idx, item_name).endswith(chapter_lines[line_idx]):
                        line_idx += 1
                    else:
                        line_idx += 1
                        break

                self.item_idx += 1

                while line_idx < max_lines and not chapter_lines[line_idx].startswith("Item {}:".format(self.item_idx)):
                    item_lines.append(chapter_lines[line_idx])
                    line_idx += 1
                with open(os.path.join(save_chapter_dir, item_name), "w", encoding="utf-8") as outf:
                    outf.writelines([line + "\n" for line in item_lines])

class TextbookDataCleaner(object):
    def __init__(self, content_file, dst_dir, dst_code_dir, raw_code_dir):
        self.dst_code_dir = dst_code_dir
        self.dst_dir = dst_dir
        self.raw_code_dir = raw_code_dir
        self.cache_dir = EJPATHUTIL.cache_dir

        with open(content_file, "r", encoding="utf-8") as inf:
            self.expected_chapter_to_items = json.load(inf)
            self.expected_chapters = list(self.expected_chapter_to_items.keys())
    
    def clear_textbook_data(self):
        for chapter in os.listdir(self.cache_dir):
            for item in os.listdir(os.path.join(self.cache_dir, chapter)):
                filepath = os.path.join(self.cache_dir, chapter, item)
                
                paras = self.clear_a_single_file(filepath, chapter, item)
                
                save_text_dir = os.path.join(self.dst_dir, chapter)
                if not os.path.exists(save_text_dir):
                    os.mkdir(save_text_dir)
                
                with open(os.path.join(save_text_dir, item), "w", encoding="utf-8") as outf:
                    for para in paras:
                        outf.write("  " + para + "\n") 

    def clear_a_single_file(self, filepath, chapter_name, item_name):
        with open(filepath, "r", encoding="utf-8") as inf:
            lines = inf.readlines()
        paras = list()

        max_lines = len(lines)
        line_idx = 0
        while line_idx < max_lines:
            # skip empty lines ans meanless lines
            if not lines[line_idx] or lines[line_idx][0] == "\n":
                line_idx += 1
                continue

            line_idx, para = self.extract_paragraph(lines, line_idx)
            if para:
                paras.append(para)
        
        ret_paras = list()
        para_idx = 0
        curr_para = ""
        while para_idx < len(paras):
            if paras[para_idx].strip()[-1] in [".", ";", "?", "}", "!", "...", '"']:
                curr_para += paras[para_idx] + " "
                ret_paras.append(curr_para)
                curr_para = ""
            else:
                curr_para += paras[para_idx] + " "
            para_idx += 1

        return ret_paras

    def extract_paragraph(self, lines, line_idx):
        para = []
        para_st_line = line_idx
        para_ed_line = line_idx
        while para_ed_line < len(lines) and lines[para_ed_line].strip():
            if lines[para_ed_line].strip()[-1] in SENT_END_SYMBLE:
                para_ed_line += 1
                break
            para_ed_line += 1

        for idx in range(para_st_line, para_ed_line):
            para.append(lines[idx].strip())
        
        return para_ed_line, " ".join(para)
       

class CodePreparar(object):
    def __init__(self, content_file, dst_dir, dst_code_dir, raw_code_dir):
        self.dst_code_dir = dst_code_dir
        self.dst_dir = dst_dir
        self.raw_code_dir = raw_code_dir
        self.cache_dir = EJPATHUTIL.cache_dir
        
        item_idx = 1
        self.item_idx2item = dict()
        with open(content_file, "r", encoding="utf-8") as inf:
            obj = json.load(inf)
            for chapter in obj:
                for item in obj[chapter]:
                    self.item_idx2item[item_idx] = [chapter, item]
                    item_idx += 1
    
    def flat_dir(self, input_dir, prefix):
        ret = dict()
        
        for filename in os.listdir(input_dir):
            if os.path.isdir(os.path.join(input_dir, filename)):
                ret.update(self.flat_dir(os.path.join(input_dir, filename), prefix + filename + "#"))
            else:
                with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as inf:
                    ret[prefix + filename] = inf.read()
        return ret
    
    def match_code_to_given(self):
        for sub_dir in os.listdir(self.raw_code_dir):
            for ssub_dir in os.listdir(os.path.join(self.raw_code_dir, sub_dir)):
                if os.path.isfile(os.path.join(self.raw_code_dir, sub_dir, ssub_dir)):
                    continue
                codes = self.flat_dir(os.path.join(self.raw_code_dir, sub_dir, ssub_dir), prefix="#")

                item_idx = int(re.match(r"item(\d+)", ssub_dir).group(1))
                chapter = self.item_idx2item[item_idx][0]
                item = self.item_idx2item[item_idx][1]

                save_code_chapter_dir = os.path.join(self.dst_code_dir, chapter)
                if not os.path.exists(save_code_chapter_dir):
                    os.mkdir(save_code_chapter_dir)
                save_code_item_dir = os.path.join(save_code_chapter_dir, item)
                if not os.path.exists(save_code_item_dir):
                    os.mkdir(save_code_item_dir)
                for filename in codes:
                    with open(os.path.join(save_code_item_dir, filename), "w", encoding="utf-8") as outf:
                        outf.write(codes[filename])

if __name__ == "__main__":
    # tbc = TextbookContentExtractor(EJPATHUTIL.raw_textbook_path, EJPATHUTIL.raw_textbook_contents_path)
    # tbc.extract_content_from_raw_textbook()

    cbe = CodePreparar(EJPATHUTIL.raw_textbook_contents_path, EJPATHUTIL.textbook_dir, EJPATHUTIL.textbook_code_dir, EJPATHUTIL.raw_textbook_code_dir)
    cbe.match_code_to_given()

    # tbdc = TextbookDataCleaner(EJPATHUTIL.raw_textbook_contents_path, EJPATHUTIL.textbook_dir, EJPATHUTIL.textbook_code_dir, EJPATHUTIL.raw_textbook_code_dir)
    # tbdc.clear_textbook_data()
    # tbdc.test_clean()