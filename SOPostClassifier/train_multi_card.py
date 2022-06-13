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
from transformers import RobertaTokenizer, RobertaModel

"""
    Task: spliting stackoverflow posts into two categories, 
        one contains software development knowledge which we are concerned, 
        the other will be discarded in the next steps
    Method: neural network
        Bert + Dense
"""

truncate_length = 512
batch_size = 16
pretrained_model = os.path.join("./pretrained/roberta-large")
model_file = "./build/bert_model.mdl"
loss_outf = open("./log/train_bert_loss.log", "w", encoding="utf-8")
accu_outf = open("./log/train_bert_accu.log", "w", encoding="utf-8")

CONTEXT_PAD = 0

class BERT_MODEL(nn.Module):
    def __init__(self, pretrained_model):
        super().__init__()
        self.bert = RobertaModel.from_pretrained(pretrained_model)
        self.predict = nn.Sequential(
            nn.Linear(1024, 1),
        )
        self.sigmod = nn.Sigmoid()
        self.loss = nn.BCELoss()
    
    def forward(self, tokens, labels=None, is_train=True):
        mask = tokens != CONTEXT_PAD
        bert_output = self.bert(input_ids=tokens, attention_mask=mask)[0]
        output = self.predict(bert_output[:, -1, :])
        logits = self.sigmod(output)

        if is_train:
            return self.loss(logits, labels)
        return logits

def train(train_dataset, valid_dataset, batch_size, epoches, lr):
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    valid_dataloader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=True)

    model = BERT_MODEL(pretrained_model).cuda()
    if torch.cuda.device_count() > 1:
        print("Let's use", torch.cuda.device_count(), "GPUs!")
        model = nn.DataParallel(model)

    # config learning rate of model
    para_dict = dict(model.named_parameters())
    paras_new = []
    for k, v in para_dict.items():
        if 'bert' in k:
            paras_new += [{'params': [v], 'lr': lr}]
        else:
            paras_new += [{'params': [v], 'lr': lr * 100}]
    optimizer = optim.Adam(params=paras_new)

    model.train()
    loss = None
    best_accu = 0
    for epoch in range(0, epoches):
        for batch in tqdm(train_dataloader):
            loss = model(batch[0].cuda(), batch[1].cuda(), is_train=True) 
            optimizer.zero_grad()
            if torch.cuda.device_count() > 1:
                loss.sum().backward()
            else:
                loss.backward()
            optimizer.step()
            if torch.cuda.device_count() > 1:
                loss_outf.write("%f\n" % loss.mean().cpu().detach().numpy())
            else:
                loss_outf.write("%f\n" % loss.cpu().detach().numpy())
        valid_accu, valid_precision, valid_recall = valid(model, valid_dataloader)
        print("[Epoch %d] Valid Accu: %f, Valid Precision: %f, Valid Recall: %f\n" % (epoch, valid_accu, valid_precision, valid_recall))
        accu_outf.write("%d\t%f\t%f\t%f\n" % (epoch, valid_accu, valid_precision, valid_recall))
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
    return (TP + TN) / total_samples, TP / (TP + FP), TP / (TP + FN)
    pass

def load_data(src_file, tokenizer, is_train=True):
    Xs = []
    ys = []
    with open(src_file, "r", encoding="utf-8") as inf:
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            label = int(line[2])

            tokens = tokenizer.tokenize(line[0].lower() + line[1].lower())
            tokens = tokenizer.convert_tokens_to_ids(tokens)
            tokens = tokenizer.build_inputs_with_special_tokens(tokens)

            Xs.append(tokens)
            ys.append([label])
    return Xs, ys

def save_model(model, save_path):
    torch.save(model.state_dict(), save_path)
    pass

if __name__ == "__main__":
    tokenizer = RobertaTokenizer.from_pretrained(pretrained_model)
    train_x, train_y = load_data(src_file="./data/train", tokenizer=tokenizer)
    valid_x, valid_y = load_data(src_file="./data/validate", tokenizer=tokenizer)
    # print(valid_y)
    
    train_x = [item[:512] + [CONTEXT_PAD] * (512 - len(item)) for item in train_x]
    valid_x = [item[:512] + [CONTEXT_PAD] * (512 - len(item)) for item in valid_x]

    train_dataset = torch.utils.data.TensorDataset(torch.tensor(train_x), torch.FloatTensor(train_y))
    valid_dataset = torch.utils.data.TensorDataset(torch.tensor(valid_x), torch.FloatTensor(valid_y))
    train(train_dataset, valid_dataset, batch_size=batch_size, epoches=10, lr=1e-5)
