import os
import sys
import json
import math

# lexical
from match_in_lexical import LexicalMatcher, LexicalMatcherTitle

# code
from match_in_code_element import CodeElementMatcher

# semantic
from match_in_word2vec_semantic import SemanticMatcher
from match_in_bert_semantic import BertSemanticMatcher

from match_config import MATCHPATHUTIL, MATCH_ALGORITHM_CONFIG


direct = False

class MatcherFromSOToTB(object):
    def __init__(self, lexical_choice, semantic_choice, debug=False):
        self.debug = debug
        if lexical_choice != "stringmatch" and lexical_choice != "mprank":
            raise "Not supported parameters"
        if semantic_choice != "sentence-bert" and semantic_choice != "word2vec":
            raise "Not supported parameters"
        
        # lexical
        if lexical_choice == "stringmatch":
            self.lxmatcher = LexicalMatcherTitle(MATCHPATHUTIL.textbook_dir)
        elif lexical_choice == "mprank":
            self.lxmatcher = LexicalMatcher(MATCHPATHUTIL.textbook_key_phrase_for_chapter_path, MATCHPATHUTIL.textbook_key_phrase_for_section_path, MATCHPATHUTIL.textbook_key_phrase_idf_path)

        # semantic
        if semantic_choice == "word2vec":
            self.smmatcher = SemanticMatcher(MATCHPATHUTIL.textbook_semantic_path, MATCHPATHUTIL.word2vec_vector_path)
        elif semantic_choice == "sentence-bert":
            self.smmatcher = BertSemanticMatcher(MATCHPATHUTIL.textbook_bert_semantic_path, model_name="sentence_bert")

        # code
        self.cematcher = CodeElementMatcher(
            # MATCHPATHUTIL.textbook_filtered_code_element_path,
            MATCHPATHUTIL.textbook_code_element_path,
            MATCHPATHUTIL.textbook_code_element_idf_path)
    
        self.CODE_MATCH_WEIGHT = MATCH_ALGORITHM_CONFIG.CODE_MATCH_WEIGHT
        self.LEXICAL_MATCH_WEIGHT = MATCH_ALGORITHM_CONFIG.LEXICAL_MATCH_WEIGHT
        self.SEMANTIC_MATCH_WEIGHT = MATCH_ALGORITHM_CONFIG.SEMANTIC_MATCH_WEIGHT

    def set_weights(self, lexical_match_weight, semantic_match_weight, code_match_weight):
        self.CODE_MATCH_WEIGHT = code_match_weight
        self.SEMANTIC_MATCH_WEIGHT = semantic_match_weight
        self.LEXICAL_MATCH_WEIGHT = lexical_match_weight
    
    def set_debug(self, debug):
        self.debug = debug
    
    def normalization(self, scores):
        exp_sum = 0
        for key in scores:
            exp_sum += math.exp(scores[key])
        for key in scores:
            scores[key] = math.exp(scores[key]) / exp_sum
        return scores
        pass
    
    def match_in_chapter(self, soq_title, soq_body, soa_body, soq_codes, soa_codes):
        chapter_scores = dict()

        # lexical
        lx_chapter_scores = self.lxmatcher.match_so_in_chapter(soq_title, soq_body, soa_body)

        # semantic
        sm_chapter_scores = self.smmatcher.match_so_in_chapter(soq_title, soq_body, soa_body, direct=direct)

        # code
        ce_chapter_scores = self.cematcher.match_so_in_chapter(soq_body, soq_codes, soa_body, soa_codes, direct=direct)

        lx_chapter_scores = self.normalization(lx_chapter_scores)
        sm_chapter_scores = self.normalization(sm_chapter_scores)
        ce_chapter_scores = self.normalization(ce_chapter_scores)
        
        if self.debug:
            return lx_chapter_scores, sm_chapter_scores, ce_chapter_scores

        for chapter in lx_chapter_scores:
            chapter_scores[chapter] = (0
                + self.CODE_MATCH_WEIGHT * ce_chapter_scores.get(chapter, 0)
                + self.LEXICAL_MATCH_WEIGHT * lx_chapter_scores.get(chapter, 0)
                + self.SEMANTIC_MATCH_WEIGHT * sm_chapter_scores.get(chapter, 0) 
            )
            
        return chapter_scores

    def match_in_section(self, soq_title, soq_body, soa_body, soq_codes, soa_codes, selected_chapter):
        section_scores = dict()
        
        # lexical 
        lx_section_scores = self.lxmatcher.match_so_in_section(soq_title, soq_body, soa_body, selected_chapter)

        # semantic
        sm_section_scores = self.smmatcher.match_so_in_section(soq_title, soq_body, soa_body, selected_chapter)

        # code
        ce_section_scores = self.cematcher.match_so_in_section(soq_body, soq_codes, soa_body, soa_codes, selected_chapter)

        lx_section_scores = self.normalization(lx_section_scores)
        sm_section_scores = self.normalization(sm_section_scores)
        ce_section_scores = self.normalization(ce_section_scores)

        if not self.check_dict_equal_key(lx_section_scores, sm_section_scores, ce_section_scores):
            print("enen???", selected_chapter)
            print(lx_section_scores)
            print(sm_section_scores)
            print(ce_section_scores)
            sys.exit(0)

        if self.debug:
            return lx_section_scores, sm_section_scores, ce_section_scores

        for section in lx_section_scores:
            section_scores[section] = (0
                + self.CODE_MATCH_WEIGHT * ce_section_scores.get(section, 0)
                + self.LEXICAL_MATCH_WEIGHT * lx_section_scores.get(section, 0)
                + self.SEMANTIC_MATCH_WEIGHT * sm_section_scores.get(section, 0) 
            )
        return section_scores
    
    def match_in_section_directly(self, soq_title, soq_body, soa_body, soq_codes, soa_codes):
        section_scores = dict()
        
        # lexical 
        lx_section_scores, section_to_chapter1 = self.lxmatcher.match_so_in_section_directly(soq_title, soq_body, soa_body)

        # semantic
        sm_section_scores, section_to_chapter2 = self.smmatcher.match_so_in_section_directly(soq_title, soq_body, soa_body)

        # code
        # api_section_scores, section_to_chapter3 = self.apimatcher.match_so_in_section_directly(soq_codes, soa_codes)
        ce_section_scores, section_to_chapter3 = self.cematcher.match_so_in_section_directly(soq_body, soq_codes, soa_body, soa_codes)

        # if not self.check_dict_equal(section_to_chapter1, section_to_chapter2, section_to_chapter3):
        #     raise "不太对劲，section_to_chapter彼此不同"

        lx_section_scores = self.normalization(lx_section_scores)
        sm_section_scores = self.normalization(sm_section_scores)
        ce_section_scores = self.normalization(ce_section_scores)

        if self.debug:
            return lx_section_scores, sm_section_scores, ce_section_scores, section_to_chapter1

        for section in lx_section_scores:
            section_scores[section] = (0
                + self.CODE_MATCH_WEIGHT * ce_chapter_scores.get(section, 0)
                + self.LEXICAL_MATCH_WEIGHT * lx_section_scores.get(section, 0)
                + self.SEMANTIC_MATCH_WEIGHT * sm_section_scores.get(section, 0) 
            )
    
        return section_scores, section_to_chapter1

    def check_dict_equal(self, *args):
        if len(args) == 0:
            return True
        
        length = len(args[0])
        for d in args:
            if not isinstance(d, dict):
                return False
            if length != len(d):
                return False
        for k in args[0]:
            for d in args[1:]:
                if k not in d or args[0][k] != d[k]:
                    return False
        return True
    
    def check_dict_equal_key(self, dic1, dic2, dic3):
        if len(dic1) != len(dic2) or len(dic1) != len(dic3):
            # print(len(dic1), len(dic2), len(dic3))
            return False
        for k in dic1:
            if k not in dic2 or k not in dic3:
                return False
        return True