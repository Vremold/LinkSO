import sys
import os
import json
import pickle

import numpy as np
from sentence_transformers import SentenceTransformer, util
# from bert_serving import BertClient

from match_config import MATCHPATHUTIL, WORD_EMBEDDING_CONFIG, MATCH_ALGORITHM_CONFIG

# bc = BertClient(check_length=False)
# bm = SentenceTransformer("sentence-transformers/msmarco-distilbert-cos-v5")
bc = SentenceTransformer("sentence-transformers/msmarco-distilbert-cos-v5")
bm = bc

class BertSemanticMatcher:
    def __init__(self, textbook_semantics_filepath, model_name):
        if model_name != "bert" and model_name != "sentence_bert":
            raise "bert model not supported!"
        self.model_name = model_name
        self.textbook_section_semantics = dict()
        self.textbook_chapter_semantics = dict()
        self.section_to_chapter = dict()
        self.__load_textbook_semantics(textbook_semantics_filepath)

    def __load_textbook_semantics(self, textbook_semantics_filepath):
        with open(textbook_semantics_filepath, "r", encoding="utf-8") as inf:
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
                semantic = np.array(json.loads(splits[2]))
                
                if chapter not in self.textbook_section_semantics:
                    self.textbook_section_semantics[chapter] = dict()
                if section not in self.textbook_section_semantics[chapter]:
                    self.textbook_section_semantics[chapter][section] = semantic
                if section not in self.section_to_chapter:
                    self.section_to_chapter[section] = chapter
                if chapter not in self.textbook_chapter_semantics:
                    self.textbook_chapter_semantics[chapter] = np.zeros(WORD_EMBEDDING_CONFIG.BERT_WORD_EMBEDDING_SIZE)
                for i, item in enumerate(semantic):
                    self.textbook_chapter_semantics[chapter][i] += item
            
            for chapter in self.textbook_chapter_semantics:
                self.textbook_chapter_semantics[chapter] /= len(self.textbook_section_semantics[chapter])

    def __cos_sim(self, a, b):
        a = np.array(a)
        b = np.array(b)
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        cos = (np.dot(a, b) / (a_norm * b_norm) + 1) / 2
        return cos

    def _get_semantic(self, text):
        if self.model_name == "bert":
            if isinstance(text, list):
                para_cnt = 0
                embed = np.zeros(WORD_EMBEDDING_CONFIG.BERT_WORD_EMBEDDING_SIZE)
                for para in text:
                    para_cnt += 1
                    embed += np.average(self.bc.encode(sent_tokenize(para)), axis=0)
                return embed / para_cnt
            elif isinstance(text, str):
                return np.average(bc.encode(sent_tokenize(text)), axis=0)
        elif self.model_name == "sentence_bert":
            if isinstance(text, list):
                return np.average(bm.encode(text), axis=0)
            elif isinstance(text, str):
                return bm.encode(text)

    def match_so_in_chapter_direct(self, soq_title, soq_body, soa_body):
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)
        
        chapter_scores = dict()
        for chapter in self.textbook_section_semantics:
            for section in self.textbook_section_semantics[chapter]:
                tmp = self.__cos_sim(so_semantic, self.textbook_section_semantics[chapter][section])
                if chapter not in chapter_scores or chapter_scores[chapter] < tmp:
                    chapter_scores[chapter] = tmp
        
        return chapter_scores
    
    def match_so_in_chapter(self, soq_title, soq_body, soa_body, direct=False):
        if direct:
            return self.match_so_in_chapter_direct(soq_title, soq_body, soa_body)
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)
        chapter_scores = dict()

        for chapter in self.textbook_chapter_semantics:
            chapter_scores[chapter] = self.__cos_sim(so_semantic, self.textbook_chapter_semantics[chapter])
        
        return chapter_scores
    
    def match_so_in_section(self, soq_title, soq_body, soa_body, selected_chapter):
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)
        section_scores = dict()
        for section in self.textbook_section_semantics[selected_chapter]:
            if section == selected_chapter:
                continue
            section_scores[section] = self.__cos_sim(so_semantic, self.textbook_section_semantics[selected_chapter][section])
        return section_scores
    
    def match_so_in_section_directly(self, soq_title, soq_body, soa_body):
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)
        
        section_scores = dict()
        for chapter in self.textbook_section_semantics:
            for section in self.textbook_section_semantics[chapter]:
                section_scores[section] = self.__cos_sim(so_semantic, self.textbook_section_semantics[chapter][section])
        
        return section_scores, self.section_to_chapter