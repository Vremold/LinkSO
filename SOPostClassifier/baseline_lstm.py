import os
from tqdm import tqdm
import sys
import json
import csv

import numpy as np
import torch.nn as nn 
import torch.optim as optim
import torch
from torch.utils.data import DataLoader
from nltk import word_tokenize
from nltk.corpus import stopwords

stop_words = stopwords.words('english')
stop_words += ['!', ',' ,'.' ,'?' ,'-s' ,'-ly' ,'</s> ', 's']

"""
    Task: spliting stackoverflow posts into two categories, 
        one contains software development knowledge which we are concerned, 
        the other will be discarded in the next steps
    Method: neural network
        Bert + Dense
"""

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

num_embeddings = 0
embedding_size = 200
lstm_hidden_size = 128
# lstm_hidden_size2 = 64
truncate_length = 200
batch_size = 32
vocab_file = "./build/vocab.json"
model_file = "./build/lstm_model.mdl"
loss_outf = open("./log/train_lstm_loss.log", "w", encoding="utf-8")
accu_outf = open("./log/train_lstm_accu.log", "w", encoding="utf-8")

CONTEXT_PAD = 0

class LSTM_MODEL(nn.Module):
    def __init__(self, num_embeddings, embedding_size, lstm_hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings, embedding_size)
        self.lstm = nn.LSTM(embedding_size, lstm_hidden_size, batch_first=True, bidirectional=True, num_layers=1)
        self.lstm_hidden_size = lstm_hidden_size
        self.predict = nn.Sequential(
            nn.Linear(lstm_hidden_size * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        self.sigmod = nn.Sigmoid()
        self.loss = nn.BCELoss()
    
    def forward(self, batch, labels, is_train=True):
        lstm_input = self.embedding(batch)
        lstm_output, (h_n, c_n) = self.lstm(lstm_input)
        output = self.predict(lstm_output[:, -1, :])
        logits = self.sigmod(output)

        if is_train:
            return self.loss(logits, labels)
        return logits

def train(train_dataset, valid_dataset, batch_size, epoches, lr):
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    valid_dataloader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=True)

    model = LSTM_MODEL(num_embeddings, embedding_size, lstm_hidden_size).cuda()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    model.train()
    loss = None
    best_accu = 0
    for epoch in range(0, epoches):
        for batch in tqdm(train_dataloader):
            loss = model(batch[0].cuda(), batch[1].cuda(), is_train=True) 
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            loss_outf.write("%f\n" % loss.cpu().detach().numpy())
        valid_accu, valid_precision, valid_recall = valid(model, valid_dataloader)
        # train_accu, train_precision, train_recall = valid(model, train_dataloader)
        print("[Epoch %d] Train losss: %f, Valid Accu: %f, Valid Precision: %f, Valid Recall: %f\n" % (epoch, loss.cpu().detach().numpy(), valid_accu, valid_precision, valid_recall))
        accu_outf.write("%d\t%f\t%f\t%f\t%f\n" % (epoch,loss.cpu().detach().numpy(), valid_accu, valid_precision, valid_recall))
        if valid_accu > best_accu:
            best_accu = valid_accu
            save_model(model, model_file)
        model.train()
    pass

def accuracy(pred, gold):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
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

def valid(model, dataloader):
    total_samples = 0
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    with torch.no_grad():
        for batch in tqdm(dataloader):
            pred = model(batch[0].cuda(), batch[1].cuda(), is_train=False)
            tp, fp, tn, fn, bsz = accuracy(pred, batch[1])
            total_samples += bsz
            TP += tp
            FP += fp
            TN += tn
            FN += fn
    return (TP + TN) / total_samples, TP / (TP + FP + 0.000000001), TP / (TP + FN + 0.000000001)
    pass

def load_data(src_file, vocab):
    Xs = []
    ys = []
    with open(src_file, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf, delimiter=",")
        for line in csv_reader:
            label = int(line[2])
            words = word_tokenize(line[0].lower()) + word_tokenize(line[1].lower())
            # words = [word for word in words if word not in stop_words]
            words = words[:120]
            for word in words:
                if word not in vocab:
                    vocab[word] = len(vocab)
            Xs.append([vocab[word] for word in words])
            ys.append([label])
    
    return Xs, ys

def save_model(model, save_path):
    torch.save(model.state_dict(), save_path)
    pass

def save_vocab(vocab, save_path):
    with open(save_path, "w", encoding="utf-8") as outf:
        json.dump(vocab, outf)

if __name__ == "__main__":
    vocab = dict()
    vocab["<PAD>"] = 0
    vocab["<UNK>"] = 1

    train_x, train_y = load_data("./data/train", vocab)
    valid_x, valid_y = load_data("./data/validate", vocab)

    num_embeddings = len(vocab)
    save_vocab(vocab, vocab_file)
    
    train_x = [item[:truncate_length] + [CONTEXT_PAD] * (truncate_length - len(item)) for item in train_x]
    valid_x = [item[:truncate_length] + [CONTEXT_PAD] * (truncate_length - len(item)) for item in valid_x]

    train_dataset = torch.utils.data.TensorDataset(torch.tensor(train_x), torch.FloatTensor(train_y))
    valid_dataset = torch.utils.data.TensorDataset(torch.tensor(valid_x), torch.FloatTensor(valid_y))
    train(train_dataset, valid_dataset, batch_size=batch_size, epoches=15, lr=1e-5)
