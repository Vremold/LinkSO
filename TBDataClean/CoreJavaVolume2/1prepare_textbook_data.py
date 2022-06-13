import os
import sys
import json
import re

from config import CJ2PATHUTIL

SENT_END_SYMBLE = [".", ";", "?", "}", "!", "...", '"']

class TextbookContentExtractor(object):
    def __init__(self, raw_textbook_file, content_file):
        self.raw_textbook_file = raw_textbook_file
        self.cache_dir = os.path.join(CJ2PATHUTIL.cache_dir)
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        
        self.__init_content(content_file)
        pass

    def __init_content(self, content_file):
        with open(content_file, "r", encoding="utf-8") as inf:
            raw_contents = json.load(inf)
        
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
    
    def __remove_unseen_chars(self, line:str) -> str:
        return "".join([x for x in line if x.isprintable()]) + "\n"

    
    def __extract_content_in_a_section(self, lines, line_idx, chapter_name, curr_chapter_id, section_name, curr_section_id):
        max_lines = len(lines)
        text = ""
        while line_idx < max_lines:
            line = self.__remove_unseen_chars(lines[line_idx])
            
            # encounter with the next chapter
            if line.strip().startswith("CHAPTER"):
                break
            
            # encounter with the next section
            if curr_section_id + 1 < len(self.expected_chapter_to_sections[chapter_name]) and \
                line.startswith("{}.{} {}".format(curr_chapter_id + 1, curr_section_id + 2, self.expected_chapter_to_sections[chapter_name][curr_section_id+1])):
                break
            
            text += line
            line_idx += 1
        
        if text:
            save_dir = os.path.join(self.cache_dir, chapter_name)
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            with open(os.path.join(save_dir, section_name.replace("/", "#")), "w", encoding="utf-8") as outf:
                outf.write(text)
        return line_idx
    
    def __extract_content_in_a_chapter(self, lines, line_idx, chapter_name, curr_chapter_id):
        max_lines = len(lines)
        # find the first section
        skip_introduction = False
        while line_idx < max_lines:
            line = self.__remove_unseen_chars(lines[line_idx])
            if line.startswith("{}.1 {}".format(curr_chapter_id + 1, self.expected_chapter_to_sections[chapter_name][0])):
                if not skip_introduction:
                    skip_introduction = True
                else:
                    break
            line_idx += 1
        
        # loop finding section
        expected_section_id = 0
        while line_idx < max_lines:
            line = self.__remove_unseen_chars(lines[line_idx])
            # meet the next chapter
            if line.strip().startswith("CHAPTER"):
                return line_idx
            
            # found section
            if line.startswith("{}.{} {}".format(curr_chapter_id + 1, expected_section_id + 1, self.expected_chapter_to_sections[chapter_name][expected_section_id])):
                section_name = self.expected_chapter_to_sections[chapter_name][expected_section_id]

                line_idx = self.__extract_content_in_a_section(lines, line_idx + 1, chapter_name, curr_chapter_id, section_name, expected_section_id)

                expected_section_id += 1
                # break
            else:
                line_idx += 1
        return line_idx
    
    def extract_content_in_raw_textbook(self):
        print("Calling extract_content_in_raw_textbook")
        curr_chapter = ""
        expected_chapter_id = 0

        with open(self.raw_textbook_file, "r", encoding="utf-8") as inf:
            lines = inf.readlines()
        
        max_lines = len(lines)
        line_idx = 0
        while line_idx < max_lines:
            line = self.__remove_unseen_chars(lines[line_idx])
            # found chapter
            if line.strip().startswith("CHAPTER"):
                chapter_name = self.expected_chapters[expected_chapter_id]
                print("found chapter:", chapter_name)
                # skip chapter title
                while not chapter_name.endswith(self.__remove_unseen_chars(lines[line_idx]).strip()):
                    line_idx += 1
                line_idx += 1

                line_idx = self.__extract_content_in_a_chapter(lines, line_idx, chapter_name, expected_chapter_id)
                expected_chapter_id += 1
                # break
            else:
                line_idx += 1

class CodeBlockExtractor(object):
    def __init__(self, content_file, dst_dir, dst_code_dir, raw_code_dir):
        self.dst_code_dir = dst_code_dir
        self.dst_dir = dst_dir
        self.given_codes = dict()
        self.cache_dir = CJ2PATHUTIL.cache_dir
        self.init_content(content_file)
        self.load_given_codes(raw_code_dir)
    
    def load_given_codes(self, raw_code_dir):
        for chapter in os.listdir(raw_code_dir):
            if "v2" not in chapter:
                continue
            chapter_idx = int(re.match(r"v2ch(\d+)", chapter).group(1)) - 1
            for seri in os.listdir(os.path.join(raw_code_dir, chapter)):
                if not os.path.isdir(os.path.join(raw_code_dir, chapter, seri)):
                    continue
                for code_filename in os.listdir(os.path.join(raw_code_dir, chapter, seri)):
                    if not code_filename.endswith(".java"):
                        continue
                    code_title = "{}/{}".format(seri, code_filename)

                    with open(os.path.join(raw_code_dir, chapter, seri, code_filename), "r", encoding="utf-8") as inf:
                        code = inf.readlines()
                    
                    if chapter_idx not in self.given_codes:
                        self.given_codes[chapter_idx] = dict()
                    self.given_codes[chapter_idx][code_title] = code
    
    def init_content(self, content_file):
        with open(content_file, "r", encoding="utf-8") as inf:
            raw_contents = json.load(inf)
        
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
    
    # def remove_code_blocks(self, filepath, chapter_idx, contained_code_titles):
    #     with open(filepath, "r", encoding="utf-8") as inf:
    #         lines = inf.readlines()

    #     for code_title in contained_code_titles:
    #         code_lines = self.given_codes[chapter_idx][code_title]

    #         line_idx = 0
    #         code_block_st_line_idx = 0
    #         code_block_ed_line_idx = 0
    #         while line_idx < len(lines):
    #             if lines[line_idx].startswith(code_title):
    #                 code_block_st_line_idx = line_idx - 1
    #                 i = line_idx + 1
    #                 j = 0
    #                 while j < len(code_lines):
    #                     line = lines[i].strip()
    #                     code_line = code_lines[j].strip()
    #                     if not code_line:
    #                         j += 1
    #                         continue
    #                     if not line:
    #                         i += 1
    #                         continue
    #                     if line == "Click here to view code image":
    #                         i += 1
    #                         continue
    #                     if re.match(r"\d+$", line):
    #                         i += 1
    #                         continue
    #                     if line == code_line:
    #                         i += 1
    #                         j += 1
    #                         continue
    #                     if re.match(r"\d+ "+re.escape(code_line), line)
    #             else:
    #                 line_idx += 1


    def handle_single_file(self, filepath, chapter_idx, section_idx, chapter_name, section_name):
        with open(filepath, "r", encoding="utf-8") as inf:
            text = inf.read()
        contained_code_titles = set()
        if chapter_idx not in self.given_codes:
            return
        for code_title in self.given_codes[chapter_idx]:
            if code_title in text:
                contained_code_titles.add(code_title)
                code_filename = code_title.split("/")[1]
                if not os.path.exists(os.path.join(self.dst_code_dir, chapter_name)):
                    os.mkdir(os.path.join(self.dst_code_dir, chapter_name))
                if not os.path.exists(os.path.join(self.dst_code_dir, chapter_name, section_name)):
                    os.mkdir(os.path.join(self.dst_code_dir, chapter_name, section_name))
                with open(os.path.join(self.dst_code_dir, chapter_name, section_name, code_filename), "w", encoding="utf-8") as outf:
                    outf.writelines([line for line in self.given_codes[chapter_idx][code_title]])
        
        # self.remove_code_blocks(filepath, chapter_idx, contained_code_titles)
    
    def extract_code_blocks(self):
        for chapter in os.listdir(self.cache_dir):
            chapter_idx = self.expected_chapters.index(chapter)
            for section in os.listdir(os.path.join(self.cache_dir, chapter)):
                filepath = os.path.join(self.cache_dir, chapter, section)
                section_idx = self.expected_chapter_to_sections[chapter].index(section.replace("#", "/"))
                
                self.handle_single_file(filepath, chapter_idx, section_idx, chapter, section)


class TextbookDataCleaner(object):
    def __init__(self, content_file, dst_dir, dst_code_dir, raw_code_dir):
        self.dst_code_dir = dst_code_dir
        self.dst_dir = dst_dir
        self.raw_code_dir = raw_code_dir
        self.cache_dir = CJ2PATHUTIL.cache_dir
        self.__init_content(content_file)
    
    def __init_content(self, content_file):
        with open(content_file, "r", encoding="utf-8") as inf:
            raw_contents = json.load(inf)
        
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

    
    def extract_paragraph(self, lines, line_idx, section_name, curr_chapter_id, curr_section_id, expected_subsection_id):
        para = []
        code_blocks = []
        para_st_line = line_idx
        para_ed_line = line_idx
        while para_ed_line < len(lines) and lines[para_ed_line].strip():
            if lines[para_ed_line].strip()[-1] in SENT_END_SYMBLE:
                para_ed_line += 1
                break
            para_ed_line += 1

        for idx in range(para_st_line, para_ed_line):
            if lines[idx].replace(" ", "").startswith("Clickheretoviewcodeimage"):
                continue
            para.append(lines[idx].strip())
        
        # next subsetion
        if para and section_name in self.expected_section_to_subsections and expected_subsection_id < len(self.expected_section_to_subsections[section_name.replace("#", "/")]) and "{}.{}.{} {}".format(curr_chapter_id + 1, curr_section_id + 1, expected_subsection_id + 1, self.expected_section_to_subsections[section_name.replace("#", "/")][expected_subsection_id]).startswith(para[0]):

            return para_ed_line, expected_subsection_id + 1, "{}\n  {}".format(para[0], " ".join(para[1:]))
        
        # useless C++ related information
        if para and para[0].startswith("C++ Note"):
            # print("[Return]", code_blocks)
            return para_ed_line, expected_subsection_id, ""
        

        return para_ed_line, expected_subsection_id, "  " + " ".join(para)
        
    def clear_a_single_file(self, filepath, chapter_name, section_name, curr_chapter_id, curr_section_id):
        with open(filepath, "r", encoding="utf-8") as inf:
            lines = inf.readlines()
        paras = list()

        max_lines = len(lines)
        line_idx = 0
        expected_subsection_id = 0
        while line_idx < max_lines:
            # skip empty lines ans meanless lines
            if not lines[line_idx] or lines[line_idx][0] == "\n":
                line_idx += 1
                continue
            if ("Clickheretoviewcodeimage" in lines[line_idx].replace(" ", "")):
                line_idx += 1
                continue

            line_idx, expected_subsection_id, para = self.extract_paragraph(lines, line_idx, section_name, curr_chapter_id, curr_section_id, expected_subsection_id)
            # print(line_idx, max_lines)
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
    
    def test_clean(self, ):
        chapter = "An Introduction to Java"
        section = "A Short History of Java"
        chapter_idx = self.expected_chapters.index(chapter)
        section_idx = self.expected_chapter_to_sections[chapter].index(section)
        # print("chapter idx: {}, section_idx: {}".format(chapter_idx, section_idx))
        filepath = os.path.join(self.cache_dir, chapter, section)
        paras = self.clear_a_single_file(filepath, chapter, section, chapter_idx, section_idx)
        print(paras)
        print(len(paras))

        # save_text_dir = os.path.join(self.dst_dir, chapter)
        # if not os.path.exists(save_text_dir):
        #     os.mkdir(save_text_dir)
        # save_code_dir = os.path.join(self.dst_code_dir, chapter)
        # if not os.path.exists(save_code_dir):
        #     os.mkdir(save_code_dir)
        # with open(os.path.join(save_text_dir, section), "w", encoding="utf-8") as outf:
        #     for para in paras:
        #         outf.write(para+"\n")
        # with open(os.path.join(save_code_dir, section), "w", encoding="utf-8") as outf:
        #     for cb in code_blocks:
        #         outf.writelines(cb)
        #         outf.write("\n") 
    
    def clear_textbook_data(self):
        for chapter in os.listdir(self.cache_dir):
            chapter_idx = self.expected_chapters.index(chapter)
            for section in os.listdir(os.path.join(self.cache_dir, chapter)):
                filepath = os.path.join(self.cache_dir, chapter, section)
                
                section_idx = self.expected_chapter_to_sections[chapter].index(section.replace("#", "/"))
                paras = self.clear_a_single_file(filepath, chapter, section, chapter_idx, section_idx)
                
                save_text_dir = os.path.join(self.dst_dir, chapter)
                if not os.path.exists(save_text_dir):
                    os.mkdir(save_text_dir)
                
                with open(os.path.join(save_text_dir, section), "w", encoding="utf-8") as outf:
                    for para in paras:
                        outf.write(para+"\n")             
        pass


if __name__ == "__main__":
    # tbc = TextbookContentExtractor(CJ2PATHUTIL.raw_textbook_path, CJ2PATHUTIL.raw_textbook_contents_path)
    # tbc.extract_content_in_raw_textbook()

    # cbe = CodeBlockExtractor(CJ2PATHUTIL.raw_textbook_contents_path, CJ2PATHUTIL.textbook_dir, CJ2PATHUTIL.textbook_code_dir, CJ2PATHUTIL.raw_textbook_code_dir)
    # cbe.extract_code_blocks()

    tbdc = TextbookDataCleaner(CJ2PATHUTIL.raw_textbook_contents_path, CJ2PATHUTIL.textbook_dir, CJ2PATHUTIL.textbook_code_dir, CJ2PATHUTIL.raw_textbook_code_dir)
    tbdc.clear_textbook_data()
    # tbdc.test_clean()
