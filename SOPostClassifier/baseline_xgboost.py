import os
import json
import csv

from nltk import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import metrics
import xgboost as xgb

def load_data(src_file):
    Xs = []
    ys = []
    with open(src_file, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf, delimiter=",")
        for line in csv_reader:
            label = int(line[2])
            words = word_tokenize(line[0].lower()) + word_tokenize(line[1].lower())
            Xs.append(" ".join(words))
            ys.append(label)
    return Xs, ys


if __name__ == "__main__":
    train_x, train_y = load_data("./data/train")
    valid_x, valid_y = load_data("./data/validate")

    vectorizer = CountVectorizer()
    tf_idf_transformer = TfidfTransformer()
    tf_idf = tf_idf_transformer.fit_transform(vectorizer.fit_transform(train_x))
    x_train_weight = tf_idf.toarray()  # 训练集TF-IDF权重矩阵
    tf_idf = tf_idf_transformer.transform(vectorizer.transform(valid_x))
    x_test_weight = tf_idf.toarray()  # 测试集TF-IDF权重矩阵

    print(x_train_weight.shape)

    # dtrain = xgb.DMatrix(x_train_weight, label=train_y)
    # dtest = xgb.DMatrix(x_test_weight, label=valid_y)

    # params = {
    #     "booster":"gbtree",
    #     "objective": "binary:logistic",
    #     "eval_metric": "error",
    #     "n_estimators": 100,
    #     "max_depth":6,
    #     "lambda":10,
    #     "subsample":0.75,
    #     "colsample_bytree":0.75,
    #     "min_child_weight":2,
    #     "eta": 0.025,
    #     "seed":0,
    #     "nthread":8,
    #     "silent":1
    # }

    # # watchlist = [(dtrain,'train'), (dtest, "val")]
    # watchlist = [(dtrain,'train')]
    # bst = xgb.train(params, dtrain, num_boost_round=5, evals=watchlist)
    # #输出概率
    # ypred = bst.predict(dtest)
    # ypred = (ypred >= 0.5) * 1
    
    
    # print ('ACC: %.4f' % metrics.accuracy_score(valid_y, ypred))
    # print ('Recall: %.4f' % metrics.recall_score(valid_y, ypred))
    # print ('F1-score: %.4f' %metrics.f1_score(valid_y, ypred))
    # print ('Precesion: %.4f' %metrics.precision_score(valid_y, ypred))
