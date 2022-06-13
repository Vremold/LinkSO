import os

class EJPATHUTIL(object):
    root_dir = "/media/dell/disk/wujw/linkso"
    raw_data_dir = os.path.join(root_dir, "RawData", "EffectiveJava")
    data_dir = os.path.join(root_dir, "TextbookFeature", "EffectiveJava")
    build_dir = os.path.join(root_dir, "build")
    cache_dir = os.path.join(root_dir, "TBDataClean", "EffectiveJava", "cache")

    so_path = os.path.join(root_dir, "SODataClean", "so_posts.csv")

    jdk_api_doc_path = os.path.join(root_dir, "JDKCrawler", "export", "apis.json")
    
    raw_textbook_path = os.path.join(raw_data_dir, "ej.txt")
    raw_textbook_code_dir = os.path.join(raw_data_dir, "ejcode")
    raw_textbook_contents_path = os.path.join(raw_data_dir, "contents.json")

    textbook_dir = os.path.join(data_dir, "textbook")
    textbook_code_dir = os.path.join(data_dir, "textbook_code")
    textbook_api_path = os.path.join(data_dir, "apis.txt")
    textbook_filtered_api_path = os.path.join(data_dir, "filtered_apis.txt")
    textbook_code_element_path = os.path.join(data_dir, "code_elements.txt")
    textbook_filtered_code_element_path = os.path.join(data_dir, "filtered_code_elements.txt")
    textbook_code_element_idf_path = os.path.join(data_dir, "code_elements_idf.json")
    
    textbook_summary_path = os.path.join(data_dir, "summaries.txt")
    textbook_semantic_path = os.path.join(data_dir, "semantics.txt")
    textbook_key_phrase_for_chapter_path = os.path.join(data_dir, "chapter_keyphrases.txt")
    textbook_key_phrase_for_section_path = os.path.join(data_dir, "section_keyphrases.txt")
    textbook_key_phrase_idf_path = os.path.join(data_dir, "keyphrase_idf.json")

    # word2vec 
    word2vec_model_path = os.path.join(build_dir, "word2vec.model")
    word2vec_vector_path = os.path.join(build_dir, "word2vec.vec")


class MPRANK_CONFIG:
    NP_GRAMMER = "NP: {<ADJ>*<NOUN|PROPN>+}"
    MAX_NP_WORD_COUNT = 3
    DEFAULT_STOPWORDS = ["many", "much", "small", "big", "little", "few", "more", "most", "necessary", "free", "unnecessary", "extensible", "valuable", "american", "industrial", "similar", "particular", "special", "specific", "simple", "first", "second", "third", "different", "same", "several", "robust", "actual", ]


class WORD_EMBEDDING_CONFIG:
    WORD_EMBEDDING_SIZE = 1024
    MIN_COUNT = 5
    WINDOW = 5