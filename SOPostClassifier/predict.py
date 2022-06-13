import os
import sys
import time
import csv
import json
import argparse

from tqdm import tqdm
import torch.nn as nn
import torch.optim as optim
import torch

from transformers import RobertaTokenizer, RobertaModel
from nltk import word_tokenize

import numpy as np

from train import BERT_MODEL
from train import CONTEXT_PAD, truncate_length, batch_size, pretrained_model, model_file

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

parser = argparse.ArgumentParser()
parser.add_argument("--skip", type=int, default=0, help="The number you want to skip when reading the file")
parser.add_argument("--readnum", type=int, default=100000, help="the number of lines you want to read in a time")
args = parser.parse_args()

def preprocess(line:str):
    return line.replace("--CODE--", "")

def load_test_data(src_file, tokenizer, skip_number=0, read_number=100000):
    Xs = []
    Xidxs = []
    with open(src_file, "r", encoding="utf-8") as inf:
        next(inf)
        for _ in range(skip_number):
            next(inf)
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            if read_number <= 0:
                break
            read_number -= 1
            tokens = tokenizer.tokenize(line[2].lower() + preprocess(line[3]).lower() if len(line) >= 4 else line[2].lower())
            tokens = tokenizer.convert_tokens_to_ids(tokens)
            tokens = tokenizer.build_inputs_with_special_tokens(tokens)
            Xs.append(tokens)
            Xidxs.append(int(line[0]))
    return Xidxs, Xs
    pass

def test(model, test_dataset):
    test_dataloader = torch.utils.data.DataLoader(test_dataset, shuffle=True, batch_size=batch_size)
    result = []
    with torch.no_grad():
        for batch in tqdm(test_dataloader):
            pred = model(batch[1].cuda(), is_train=False)
            # pred = torch.argmax(pred, dim=1)
            pred = pred.reshape(-1)
            pred_idx = batch[0]
            for i, predication in zip(pred_idx, pred):
                result.append((int(i), 1 if predication >= 0.5 else 0))
    return result
    pass

if __name__ == "__main__":
    print("running with args", args.skip)
    test_result_path = os.path.join("./test_result.json")
    
    ## apply the trained bert-based model to predict
    tokenizer = RobertaTokenizer.from_pretrained(pretrained_model)
    test_idxs, test_x = load_test_data("/media/dell/disk/wujw/linkso/RawData/so_posts.csv", tokenizer=tokenizer, skip_number=args.skip, read_number=args.readnum)

    test_x = [item[:truncate_length] + [CONTEXT_PAD] * (truncate_length - len(item)) for item in test_x]
    test_dataset = torch.utils.data.TensorDataset(torch.tensor(test_idxs), torch.tensor(test_x))

    model = BERT_MODEL(pretrained_model).cuda()
    model.load_state_dict(torch.load(model_file))

    pred = test(model, test_dataset)
    with open(test_result_path, "a+", encoding="utf-8") as inf:
        inf.write(json.dumps(pred, ensure_ascii=False) + "\n")