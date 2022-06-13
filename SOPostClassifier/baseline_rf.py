import csv
import os
import json
from baseline import TrainModule
from sklearn import metrics
from nltk import word_tokenize
import numpy as np

def accuracy(pred, gold):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    pred = np.array(pred)
    gold = np.array(gold)
    pred = pred.reshape(-1)
    gold = gold.reshape(-1)
    bsz = len(pred)
    for pred_item, gold_item in zip(pred, gold):
        if gold_item == 1.0 and pred_item >= 0.5:
            tp += 1
        elif gold_item == 0.0 and pred_item < 0.5:
            tn += 1
        elif gold_item == 0.0 and pred_item >= 0.5:
            fp += 1
        else:
            fn += 1
    return tp, fp, tn, fn, bsz

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

    model = TrainModule()
    model.train(train_x, train_y)
    output = model.predict(valid_x, valid_y)
    print(accuracy(output, valid_y))
    ypred = [1 if item >= 0.5 else 0 for item in output]

    print ('Recall: %.4f' % metrics.recall_score(valid_y, ypred))
    print ('F1-score: %.4f' %metrics.f1_score(valid_y, ypred))
    print ('Precesion: %.4f' %metrics.precision_score(valid_y, ypred))