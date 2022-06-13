import sys
import os
import json
import pickle

from gensim.models import KeyedVectors
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize

from match_config import MATCHPATHUTIL, WORD_EMBEDDING_CONFIG, MATCH_ALGORITHM_CONFIG

class SemanticMatcher:
    def __init__(self, textbook_semantics_filepath, word2vec_filepath):
        self.textbook_section_semantics = dict()
        self.textbook_chapter_semantics = dict()
        self.section_to_chapter = dict()
        self.wv = KeyedVectors.load_word2vec_format(word2vec_filepath, binary=False, limit=500000)
        self.__load_textbook_semantics(textbook_semantics_filepath)

    def __cos_sim(self, a, b):
        a = np.array(a)
        b = np.array(b)
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        cos = (np.dot(a, b) / (a_norm * b_norm) + 1) / 2
        return cos
    
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
                    self.textbook_chapter_semantics[chapter] = np.zeros(WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE)
                for i, item in enumerate(semantic):
                    self.textbook_chapter_semantics[chapter][i] += item
            
            for chapter in self.textbook_chapter_semantics:
                self.textbook_chapter_semantics[chapter] /= len(self.textbook_section_semantics[chapter])

    def _get_semantic(self, text):
        semantic = np.zeros(WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE)
        cnt = 0
        if isinstance(text, list):
            for para in text:
                for sent in sent_tokenize(para):
                    for word in word_tokenize(sent):
                        try:
                            vec = self.wv.get_vector(word)
                        except:
                            vec = np.zeros(WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE)
                        semantic += vec
                        cnt += 1
            return semantic / cnt
        else:
            for sent in sent_tokenize(text):
                for word in word_tokenize(sent):
                    try:
                        vec = self.wv.get_vector(word)
                    except:
                        vec = np.zeros(WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE)
                    semantic += vec
                    cnt += 1
            return semantic / cnt

    def match_so_in_chapter_uniform(self, soq_title, soq_body, soa_body):
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)
        chapter_scores = dict()

        for chapter in self.textbook_chapter_semantics:
            chapter_scores[chapter] = self.__cos_sim(so_semantic, self.textbook_chapter_semantics[chapter])
        
        return chapter_scores

    def match_so_in_chapter(self, soq_title, soq_body, soa_body, direct=False):
        soq_title_semantic = self._get_semantic(soq_title)
        soq_body_semantic = self._get_semantic(soq_body)
        soa_body_semantic = self._get_semantic(soa_body)

        # matching chapter
        chapter_scores = dict()
        for chapter in self.textbook_chapter_semantics:
            soq_title_score = self.__cos_sim(soq_title_semantic, self.textbook_chapter_semantics[chapter])
            soq_body_score = self.__cos_sim(soq_body_semantic, self.textbook_chapter_semantics[chapter])
            soa_body_score = self.__cos_sim(soa_body_semantic, self.textbook_chapter_semantics[chapter])

            chapter_scores[chapter] = MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_IN_TITLE_WEIGHT * soq_title_score + MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_IN_BODY_WEIGHT * soq_body_score + MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_IN_ANSWER_BODY_WEIGHT * soa_body_score
        
        return chapter_scores
    
    def match_so_in_section_uniform(self, soq_title, soq_body, soa_body, selected_chapter):
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)
        section_scores = dict()
        for section in self.textbook_section_semantics[selected_chapter]:
            if section == selected_chapter:
                continue
            section_scores[section] = self.__cos_sim(so_semantic, self.textbook_section_semantics[selected_chapter][section])
        return section_scores
    
    def match_so_in_section(self, soq_title, soq_body, soa_body, selected_chapter):
        soq_title_semantic = self._get_semantic(soq_title)
        soq_body_semantic = self._get_semantic(soq_body)
        soa_body_semantic = self._get_semantic(soa_body)

        section_scores = dict()
        for section in self.textbook_section_semantics[selected_chapter]:
            if section == selected_chapter:
                continue
            soq_title_score = self.__cos_sim(soq_title_semantic, self.textbook_section_semantics[selected_chapter][section])
            soq_body_score = self.__cos_sim(soq_body_semantic, self.textbook_section_semantics[selected_chapter][section])
            soa_body_score = self.__cos_sim(soa_body_semantic, self.textbook_section_semantics[selected_chapter][section])

            section_scores[section] = MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_IN_TITLE_WEIGHT * soq_title_score + MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_IN_BODY_WEIGHT * soq_body_score + MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_IN_ANSWER_BODY_WEIGHT * soa_body_score
        # section_scores = sorted(section_scores.items(), key=lambda x : x[1], reverse=True)
        
        return section_scores
    
    def match_so_in_section_directly(self, soq_title, soq_body, soa_body):
        so_semantic = self._get_semantic(soq_title + soq_body + soa_body)

        section_scores = dict()
        for chapter in self.textbook_section_semantics:
            for section in self.textbook_section_semantics[chapter]:
                section_scores[section] = self.__cos_sim(so_semantic, self.textbook_section_semantics[chapter][section])
        
        return section_scores, self.section_to_chapter
    