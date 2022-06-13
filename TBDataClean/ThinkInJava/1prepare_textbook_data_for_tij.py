"""
    目标：从think in java 4 edition中抽取文本，按照章、节、段落组织好
    数据源：
        1、chapters依赖人的手动注入
        2、目录文件需要手动从pdf中拷贝
"""

import os
import json
import sys
import re
import copy

from config import TIJPATHUTIL

chapters = [
    "Preface",
    "Introduction",
    "Introduction to Objects",
    "Everything Is an Object",
    "Operators",
    "Controlling Execution",
    "Initialization & Cleanup",
    "Access Control",
    "Reusing Classes",
    "Polymorphism",
    "Interfaces",
    "Inner Classes",
    "Holding Your Objects",
    "Error Handling with Exceptions",
    "Strings",
    "Type Information",
    "Generics",
    "Arrays",
    "Containers in Depth",
    "I/O",
    "Enumerated Types",
    "Annotations",
    "Concurrency",
    "Graphical User Interfaces",
    "A: Supplements",
    "B: Resources",
    "Index"
]

SENT_END_SYMBOLS = [".", "?", "!", "...", "\"", "”", ":", ";", "}", "~"]

class Strategy():
    def __init__(self):
        pass
    
    def judge_raw_line_valid_in_tij(self, line):
        if not line:
            return False
        line = re.sub("\n", "##n##", line)
        line = "".join([x for x in line if x.isprintable()])
        line = re.sub("##n##", "\n", line)

        if "Thinking in Java                       Bruce Eckel" in line: # 页脚
            return False, line
        
        if line[0] != " " and len(line) > 70: # 页脚
            return False, line
        
        if re.match(r"    \d", line): # 脚注
            return False, line
        
        return True, line

    def judge_code_block_start_in_tij(self, line):
        if line.strip().startswith("//:"):
            return True
        return False
    
    def judge_code_block_end_in_tij(self, line):
        if (line.strip().endswith("///:~")):
            return True
        return False

class TextbookClear():
    def __init__(self, raw_textbook_file, content_file, dst_dir, dst_code_dir):
        self.raw_textbook_file = raw_textbook_file
        self.dst_dir = dst_dir
        self.cache_dir = TIJPATHUTIL.cache_dir
        self.dst_code_dir = dst_code_dir
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        
        self.__init_contents(content_file)
        self.strategy = Strategy()
    
    def __init_contents(self, content_file):
        with open(content_file, "r", encoding="utf-8") as inf:
            raw_contents = json.load(inf)
        
        # 匹配原始txt文本时专用
        self.expected_chapters = list(raw_contents.keys())
        self.expected_chapter_to_sections = dict()
        self.expected_section_to_subsections = dict()
        for chapter in raw_contents:
            if chapter not in self.expected_chapter_to_sections:
                self.expected_chapter_to_sections[chapter] = list()
            for section in raw_contents[chapter]:
                self.expected_chapter_to_sections[chapter].append(section)
                if section not in self.expected_section_to_subsections:
                    self.expected_section_to_subsections[section] = list()
                for subsection in raw_contents[chapter][section]:
                    self.expected_section_to_subsections[section].append(subsection)
            
        # 处理后续文件夹相关事宜专用
        self.used_chapter_to_sections = dict()
        for chapter in self.expected_chapter_to_sections:
            used_chapter = chapter.replace("/", "")
            if used_chapter not in self.used_chapter_to_sections:
                self.used_chapter_to_sections[used_chapter] = list()
                self.used_chapter_to_sections[used_chapter].append(used_chapter)
            for section in self.expected_chapter_to_sections[chapter]:
                self.used_chapter_to_sections[used_chapter].append(section.replace("/", ""))
        
        self.used_section_to_subsections = dict()
        for section in self.expected_section_to_subsections:
            used_section = section.replace("/", "")
            if used_section not in self.used_section_to_subsections:
                self.used_section_to_subsections[used_section] = list()
            for subs in self.expected_section_to_subsections[section]:
                self.used_section_to_subsections[used_section].append(subs)
    
    def __handle_wrong_path(self, path):
        return path.replace("/", "")
    
    def clean_cache(self, indir):
        for filename in os.listdir(indir):
            if os.path.isdir(os.path.join(indir, filename)):
                self.clean_cache(os.path.join(indir, filename))
            else:
                os.remove(os.path.join(indir, filename))
    
    # 将原始的教材text文本分成章节
    def extract_content_in_raw_textbook(self):
        def write_content():
            write_chapter = curr_chapter.replace("/", "")
            write_section = curr_section.replace("/", "")
            dst_dir = os.path.join(self.cache_dir, write_chapter)
            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)
            with open(os.path.join(dst_dir, write_section), "w", encoding="utf-8") as outf:
                outf.write(text)
        
        curr_chapter = ""
        expected_chapter_id = 0
        curr_section = ""
        expected_section_id = 0
        text = ""
        with open(self.raw_textbook_file, "r", encoding="utf-8") as inf:
            for line in inf:
                is_valid, line = self.strategy.judge_raw_line_valid_in_tij(line)
                if not is_valid:
                    continue
                if line[0] == " " or line[0] == "\n":
                    text += line
                    continue
                # 匹配完整的chapter标题
                if line.strip() in self.expected_chapters:
                    # 保证章的出现顺序
                    if self.expected_chapters[expected_chapter_id] == line.strip():
                        if text:
                            write_content()
                        
                        text = ""
                        curr_chapter = line.strip()
                        expected_chapter_id = self.expected_chapters.index(curr_chapter) + 1
                        curr_section = curr_chapter
                        expected_section_id = 0
                        continue

                # 匹配不完整的chapter标题
                if expected_chapter_id < len(self.expected_chapters) and self.expected_chapters[expected_chapter_id].startswith(line.strip()):
                    print("Detect chapter title {} in: {}\n".format(self.expected_chapters[expected_chapter_id], line))
                    if text:
                        write_content()
                    
                    text = ""
                    curr_chapter = self.expected_chapters[expected_chapter_id]
                    expected_chapter_id += 1
                    curr_section = curr_chapter
                    expected_section_id = 0
                    continue

                # 匹配完整的节标题
                if line.strip() in self.expected_chapter_to_sections[curr_chapter]:
                    # 保证节的出现顺序
                    if self.expected_chapter_to_sections[curr_chapter][expected_section_id] == line.strip():

                        if text:
                            write_content()
                        
                        text = ""
                        curr_section = line.strip()
                        expected_section_id = self.expected_chapter_to_sections[curr_chapter].index(curr_section) + 1
                        continue
                
                # 匹配不完整的节标题
                if expected_section_id < len(self.expected_chapter_to_sections[curr_chapter]) and self.expected_chapter_to_sections[curr_chapter][expected_section_id].startswith(line.strip()):
                    print("Detect section title {} in: {}\n".format(self.expected_chapter_to_sections[curr_chapter][expected_section_id], line))
                    if text:
                        write_content()

                    text = ""
                    curr_section = self.expected_chapter_to_sections[curr_chapter][expected_section_id]
                    expected_section_id += 1
                    continue

                text += line

    def clean_and_read_single_file(self, filepath, subsections):
        paras = list()
        inf = open(filepath, "r", encoding="utf-8")
        lines = inf.readlines()
        inf.close()

        line_id = 0
        while line_id < len(lines):
            # skip empty lines
            if not lines[line_id].strip():
                line_id += 1
                continue
            
            # find until encounting next empty line
            next_line_id = line_id + 1
            while next_line_id < len(lines) and lines[next_line_id].strip():
                next_line_id += 1
            
            # note that line[next_line_id] is empty line or next_line_id exceed the max index
            if lines[next_line_id - 1].strip().replace("/", "") in subsections:
                para_text = "  "
                for i in range(line_id, next_line_id - 1):
                    para_text += re.sub(r" +", " ", lines[i].strip()) + " "
                paras.append(para_text)
                paras.append(lines[next_line_id - 1].strip().replace("/", ""))

                line_id = next_line_id
            # a complete paragraph
            elif lines[next_line_id - 1].strip()[-1] in SENT_END_SYMBOLS:
                para_text = "  "
                for i in range(line_id, next_line_id):
                    para_text += re.sub(r" +", " ", lines[i].strip()) + " "
                paras.append(para_text)
                line_id = next_line_id
            # a incomplete paragraph
            # note that: We only allow one paragraph to be divided into no more than two fragments
            else:
                # skip empty row
                while next_line_id < len(lines) and not lines[next_line_id].strip():
                    next_line_id += 1
                # find next line before encounting a empty row
                while next_line_id < len(lines) and lines[next_line_id].strip():
                    next_line_id += 1
                
                if lines[next_line_id - 1].strip().replace("/", "") in subsections:
                    para_text = "  "
                    for i in range(line_id, next_line_id - 1):
                        para_text += re.sub(r" +", " ", lines[i].strip()) + " "
                    paras.append(para_text)
                    paras.append(lines[next_line_id - 1].strip().replace("/", ""))
                else:
                    para_text = "  "
                    for i in range(line_id, next_line_id):
                        para_text += re.sub(r" +", " ", lines[i].strip()) + " "
                    paras.append(para_text)
                line_id = next_line_id
        return paras
    
    def __remove_code_block(self, paras):
        max_length = len(paras)
        para_id = 0
        ret = list()
        codes = list()
        while para_id < max_length:
            if self.strategy.judge_code_block_start_in_tij(paras[para_id]):
                ed_para_id = para_id
                code = list()
                while ed_para_id < max_length and not self.strategy.judge_code_block_end_in_tij(paras[ed_para_id]):
                    code.append(paras[ed_para_id])
                    ed_para_id += 1
                code.append(paras[ed_para_id])
                codes.append(" ".join(code))
                para_id = ed_para_id + 1
            else:
                ret.append(paras[para_id])
                para_id += 1
        return ret, codes

    def clean_extracted_data(self):
        for chapter in os.listdir(self.cache_dir):
            if not os.path.isdir(os.path.join(self.cache_dir, chapter)):
                continue
            real_chapter_sections = os.listdir(os.path.join(self.cache_dir, chapter))
            for i in range(len(self.used_chapter_to_sections[chapter])):
                section = self.used_chapter_to_sections[chapter][i]
                if section not in real_chapter_sections:
                    continue

                print("[clean_extracted_data] Processing File: {}".format(os.path.join(self.cache_dir, chapter, section)))
                paras = self.clean_and_read_single_file(os.path.join(self.cache_dir, chapter, section), self.used_section_to_subsections.get(section, []))
                paras, codes = self.__remove_code_block(paras)

                save_dst_dir = os.path.join(self.dst_dir, chapter)
                if not os.path.exists(save_dst_dir):
                    os.mkdir(save_dst_dir)
                with open(os.path.join(save_dst_dir, section), "w", encoding="utf-8") as outf:
                    outf.writelines([para + "\n" for para in paras])
                
                save_code_dst_dir = os.path.join(self.dst_code_dir, chapter)
                if not os.path.exists(save_code_dst_dir):
                    os.mkdir(save_code_dst_dir)
                with open(os.path.join(save_code_dst_dir, section), "w", encoding="utf-8") as outf:
                    outf.writelines([code + "\n" for code in codes])

    
    def extract(self):
        # self.extract_content_in_raw_textbook()
        self.clean_extracted_data()
        # self.clean_cache(self.cache_dir)

if __name__ == "__main__":
    te = TextbookClear(TIJPATHUTIL.raw_textbook_path, TIJPATHUTIL.raw_textbook_contents_path, TIJPATHUTIL.textbook_dir, TIJPATHUTIL.textbook_code_dir)
    te.extract()