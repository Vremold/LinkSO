import os

TEXTBOOK = "ThinkInJava"

class MATCHPATHUTIL(object):
    root_dir = "/home/dell/linkso"
    feature_dir = os.path.join(root_dir, "TextbookFeature", TEXTBOOK)
    build_dir = os.path.join(root_dir, "build")

    # jdk api reference
    jdk_api_doc_path = os.path.join(root_dir, "JDKCrawler", "export", "apis.json")

    # raw textbook 
    textbook_dir = os.path.join(feature_dir, "textbook")

    # word2vec 
    word2vec_model_path = os.path.join(build_dir, TEXTBOOK, "word2vec.model")
    word2vec_vector_path = os.path.join(build_dir, TEXTBOOK, "word2vec.vec")

    # api
    textbook_api_path = os.path.join(feature_dir, "apis.txt")
    textbook_filtered_api_path = os.path.join(feature_dir, "filtered_apis.txt")

    # code element
    textbook_code_element_path = os.path.join(feature_dir, "code_elements.txt")
    textbook_filtered_code_element_path = os.path.join(feature_dir, "filtered_code_elements.txt")
    textbook_code_element_idf_path = os.path.join(feature_dir, "code_elements_idf.json")

    # key phrases
    textbook_key_phrase_for_chapter_path = os.path.join(feature_dir, "chapter_keyphrases.txt")
    textbook_key_phrase_for_section_path = os.path.join(feature_dir, "section_keyphrases.txt")
    textbook_key_phrase_idf_path = os.path.join(feature_dir, "keyphrase_idf.json")

    # semantics
    textbook_bert_semantic_path = os.path.join(feature_dir, "bert_semantics.txt") 
    textbook_semantic_path = os.path.join(feature_dir, "semantics.txt")
    
class MPRANK_CONFIG:
    NP_GRAMMER = "NP: {<ADJ>*<NOUN|PROPN>+}"
    MAX_NP_WORD_COUNT = 3
    DEFAULT_STOPWORDS = ["many", "much", "small", "big", "little", "few", "more", "most", "necessary", "free", "unnecessary", "extensible", "valuable", "american", "industrial", "similar", "particular", "special", "specific", "simple", "first", "second", "third", "different", "same", "several", "robust", "actual", ]

class WORD_EMBEDDING_CONFIG:
    WORD_EMBEDDING_SIZE = 1024
    BERT_WORD_EMBEDDING_SIZE = 768
    MIN_COUNT = 5
    WINDOW = 5

class MATCH_ALGORITHM_CONFIG:
    EXCLUDED_CHAPTERS = {
        "A: Supplements",
        "B: Resources",
        "Preface",
        "The Java Programming Environment",
        "An Introduction to Java"
    }

    EXCLUDED_SECTIONS = {
        "Summary",
        "Exercises",
        "A History of Java User Interface Toolkits",
        "Connection Management in Web and Enterprise Applications"
    }

    # ?????????????????????????????????????????????????????????????????????????????????????????????
    LEXICAL_KP_SCORE_BOTTOMLINE = 0.01
    TOP_KEYPHRASE_LIMIT = 10
    
    # ????????????????????????????????????
    SEMANTIC_MATCH_IN_TITLE_WEIGHT = 0.4
    SEMANTIC_MATCH_IN_BODY_WEIGHT = 0.3
    SEMANTIC_MATCH_IN_ANSWER_BODY_WEIGHT = 0.3

    # ???????????????????????????
    LEXICAL_MATCH_WEIGHT = 0.4
    SEMANTIC_MATCH_WEIGHT = 0.3
    TITLE_LEXICAL_MATCH_WEIGHT = 0.2
    CODE_MATCH_WEIGHT = 0.1