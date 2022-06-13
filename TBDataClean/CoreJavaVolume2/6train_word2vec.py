import os
import sys
import json
import multiprocessing
import csv

from nltk.tokenize import sent_tokenize, word_tokenize
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from gensim.models import KeyedVectors
import numpy as np

from config import WORD_EMBEDDING_CONFIG, CJ2PATHUTIL

SAVE_CORPUS = True

def load_so_corpus(so_filepath):
    so_corpus = []
    with open(so_filepath, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            Qtitle = line[2]
            Qbody = line[3]
            Abody = line[7]
            so_corpus.append(word_tokenize(Qtitle))
            for sent in sent_tokenize(Qbody):
                so_corpus.append(word_tokenize(sent))
            for sent in sent_tokenize(Abody):
                so_corpus.append(word_tokenize(sent))
    return so_corpus
    pass

def load_textbook_corpus(textbook_dir):
    textbook_corpus = []
    for chapter in os.listdir(textbook_dir):
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            section_filepath = os.path.join(textbook_dir, chapter, section)
            with open(section_filepath, "r", encoding="utf-8") as inf:
                for para in inf:
                    for sent in sent_tokenize(para):
                        textbook_corpus.append(word_tokenize(sent))
    return textbook_corpus
    pass


def train_word2vec_model(
    corpus, 
    save_model_filepath, 
    save_embed_filepath):
    model = Word2Vec(sentences=corpus, vector_size=WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE, window=WORD_EMBEDDING_CONFIG.WINDOW, min_count=WORD_EMBEDDING_CONFIG.MIN_COUNT, workers=multiprocessing.cpu_count(), epochs=30)
    model.save(save_model_filepath)
    model.wv.save_word2vec_format(save_embed_filepath, binary=False)
    pass

"""
default paras:
    textbook_summaries_filepath: "./Data/TextbookFeature/textbook_summaries"
    save_semantic_feature_filepath: "./Data/TextbookFeature/textbook_semantics"
    word2vec_filepath: "./Data/word2vec.vec"
"""
def generate_tb_semantic_feature(textbook_summaries_filepath, save_semantic_feature_filepath, word2vec_filepath):
    wv = KeyedVectors.load_word2vec_format(word2vec_filepath, binary=False)
    outf = open(save_semantic_feature_filepath, "w", encoding="utf-8")
    with open(textbook_summaries_filepath, "r", encoding="utf-8") as inf:
        for line in inf:
            splits = line.strip().split("\t")
            chapter = splits[0]
            section = splits[1]
            summary = splits[2]
            embed = np.zeros(shape=WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE)
            cnt = 0
            for sent in sent_tokenize(summary):
                for word in word_tokenize(sent):
                    try:
                        vec = wv.get_vector(word)
                    except:
                        vec = np.zeros(shape=WORD_EMBEDDING_CONFIG.WORD_EMBEDDING_SIZE)
                    embed += vec
                    cnt += 1
            embed /= cnt
            outf.write("{}\t{}\t{}\n".format(chapter, section, json.dumps(list(embed))))


if __name__ == "__main__":
    # test()
    print("loading so_corpus...")
    so_corpus = load_so_corpus(CJ2PATHUTIL.so_path)
    print("loading textbook_corpus...")
    textbook_corpus = load_textbook_corpus(CJ2PATHUTIL.textbook_dir)

    if SAVE_CORPUS:
        with open(os.path.join(CJ2PATHUTIL.cache_dir, "word2vec_corpus"), "w", encoding="utf-8") as outf:
            for sent in so_corpus + textbook_corpus:
                outf.write(json.dumps(sent))
                outf.write("\n")
    
    print("loading corpus finished!")
    train_word2vec_model(
        so_corpus + textbook_corpus, 
        CJ2PATHUTIL.word2vec_model_path,
        CJ2PATHUTIL.word2vec_vector_path)
    pass
    # corpus = []
    # with open(os.path.join(CJ2PATHUTIL, "word2vec_corpus"), "r", encoding="utf-8") as inf:
    #     for line in inf:
    #         corpus.append(json.loads(line))

    # print("loading corpus finished!")
    # train_word2vec_model(
    #     # so_question_corpus + so_answer_corpus + textbook_corpus, 
    #     corpus,
    #     CJ2PATHUTIL.word2vec_model_path,
    #     CJ2PATHUTIL.word2vec_vector_path)

    generate_tb_semantic_feature(CJ2PATHUTIL.textbook_summary_path, CJ2PATHUTIL.textbook_semantic_path, CJ2PATHUTIL.word2vec_vector_path)
    pass