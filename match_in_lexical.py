import os
import sys
import json
import re 

from fuzzywuzzy import fuzz

from match_config import MPRANK_CONFIG, MATCH_ALGORITHM_CONFIG, MATCHPATHUTIL

class LexicalMatcherTitle(object):
    def __init__(self, textbook_dir):
        # ATTENTION: section 在不同章里面应该保持不同
        self.section_to_chapter = dict()
        self.section_titles = set()

        for chapter in os.listdir(textbook_dir):
            if chapter in MATCH_ALGORITHM_CONFIG.EXCLUDED_CHAPTERS:
                    continue
            for section in os.listdir(os.path.join(textbook_dir, chapter)):
                if section == chapter:
                    continue
                if section in MATCH_ALGORITHM_CONFIG.EXCLUDED_SECTIONS:
                    continue
                if section not in self.section_to_chapter:
                    self.section_to_chapter[section] = chapter
                self.section_titles.add(section)
    
    def count_scores(self, qtitle):
        section_scores = dict()
        chapter_scores = dict()
        for st in self.section_titles:
            section_scores[st] = fuzz.partial_ratio(st, qtitle)
            chapter = self.section_to_chapter[st]

            # max
            if chapter not in chapter_scores:
                chapter_scores[chapter] = 0
            chapter_scores[chapter] = max(chapter_scores[chapter], section_scores[st])

        return chapter_scores, section_scores
    
    def match_so_in_chapter(self, qtitle, soq_body, soa_body):
        chapter_scores, _ = self.count_scores(qtitle)
        return chapter_scores
    
    def match_so_in_section(self, qtitle, soq_body, soa_body, selected_chapter):
        _, section_scores = self.count_scores(qtitle)
        ret = dict()
        for st in section_scores:
            if self.section_to_chapter[st] == selected_chapter:
                ret[st] = section_scores[st]
        return ret

    def match_so_in_section_directly(self, qtitle, soq_body, soa_body):
        _, section_scores = self.count_scores(qtitle)
        return section_scores, self.section_to_chapter
    

class LexicalMatcher:
    def __init__(self, textbook_chapter_phrases_filepath, textbook_section_phrases_filepath, keyphrase_idf_filepath, debug=False):
        self.debug = debug
        with open(keyphrase_idf_filepath, "r", encoding="utf-8") as inf:
            self.kw_idf = json.load(inf)
        self.textbook_chapter_keyphrases = dict()
        self.textbook_section_keyphrases = dict()
        with open(textbook_chapter_phrases_filepath, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.split("\t")
                chapter = splits[0]

                # 初始化时，将不需要匹配的章节扣除在外
                if chapter in MATCH_ALGORITHM_CONFIG.EXCLUDED_CHAPTERS:
                    continue

                if chapter not in self.textbook_chapter_keyphrases:
                    self.textbook_chapter_keyphrases[chapter] = dict()

                kps = json.loads(splits[1])
                kp_score = {kp : imp * self.kw_idf.get(kp, 1) for [kp, imp] in kps}
                kp_score = sorted(kp_score.items(), key=lambda x : x[1], reverse=True)[:MATCH_ALGORITHM_CONFIG.TOP_KEYPHRASE_LIMIT]
                for kp in kp_score:
                    self.textbook_chapter_keyphrases[chapter][kp[0]] = kp[1]
        
        with open(textbook_section_phrases_filepath, "r", encoding="utf-8") as inf:
            for line in inf:
                splits = line.split("\t")
                chapter = splits[0]
                section = splits[1]

                # 初始化时，将不需要匹配的章节扣除在外
                if chapter in MATCH_ALGORITHM_CONFIG.EXCLUDED_CHAPTERS:
                    continue
                if section == chapter:
                    continue
                if section in MATCH_ALGORITHM_CONFIG.EXCLUDED_SECTIONS:
                    continue
                if chapter not in self.textbook_section_keyphrases:
                    self.textbook_section_keyphrases[chapter] = dict()
                if section not in self.textbook_section_keyphrases[chapter]:
                    self.textbook_section_keyphrases[chapter][section] = dict()
                
                kps = json.loads(splits[2])
                kp_score = {kp : imp * self.kw_idf.get(kp, 1) for [kp, imp] in kps}
                kp_score = sorted(kp_score.items(), key=lambda x : x[1], reverse=True)[:MATCH_ALGORITHM_CONFIG.TOP_KEYPHRASE_LIMIT]

                for kp in kp_score:
                    self.textbook_section_keyphrases[chapter][section][kp[0]] = kp[1]

    def fuzzy_match(self, kws, text):
        if isinstance(kws, dict):
            kws = kws.keys()
        score = 0
        for kw in kws:
            score += fuzz.partial_ratio(kw, text)
        return score / 100 / len(kws)

    def __nps_incount(self, nps, textbook_kps):
        cnt = 0
        for np in nps:
            if np in textbook_kps:
                cnt += 1
        return cnt
    
    # 根据tb中的关键词在so中的模糊匹配得到
    def match_so_in_chapter_fuzzy(self, so_title, soq_body, soa_body):
        so_text = soa_body + soq_body
        chapter_scores = dict()
        for chapter in self.textbook_chapter_keyphrases:
            chapter_scores[chapter] = self.fuzzy_match(self.textbook_chapter_keyphrases[chapter], so_text)
        
        return chapter_scores
    
    # 根据tb中的关键词在so中出现频率
    def match_so_in_chapter(self, so_title, soq_body, soa_body):
        so_text = soa_body + soq_body
        chapter_scores = dict()
        for chapter in self.textbook_chapter_keyphrases:
            if chapter not in chapter_scores:
                chapter_scores[chapter] = 0
            for np in self.textbook_chapter_keyphrases[chapter]:
                match = re.findall(r"[^a-zA-Z]" + re.escape(np) + r"[^a-zA-Z]", so_text.lower())
                if match:
                    chapter_scores[chapter] += len(match)

        return chapter_scores
    

    def match_so_in_section_fuzzy(self, so_title, soq_body, soa_body, selected_chapter):
        so_text = soa_body + soq_body
        section_scores = dict()
        section_scores = dict()
        for section in self.textbook_section_keyphrases[selected_chapter]:
            if section == selected_chapter:
                continue
            section_scores[section] = self.fuzzy_match(
                self.textbook_section_keyphrases[selected_chapter][section], 
                so_text)
        return section_scores
    
    def match_so_in_section(self, so_title, soq_body, soa_body, selected_chapter):
        so_text = soa_body + soq_body
        section_scores = dict()
        for section in self.textbook_section_keyphrases[selected_chapter]:
            if section == selected_chapter:
                continue
            if section not in section_scores:
                section_scores[section] = 0
            for np in self.textbook_section_keyphrases[selected_chapter][section]:
                match = re.findall(r"[^a-zA-Z]" + re.escape(np) + r"[^a-zA-Z]", so_text.lower())
                if match:
                    section_scores[section] += len(match)

        return section_scores