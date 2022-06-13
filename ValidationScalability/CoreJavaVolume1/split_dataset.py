import os
import sys
import random

src_filepath = "./labeled.csv"
dst_train_filepath = "./train.csv"
dst_validate_filepath = "./validate.csv"

random.seed(3)

with open(src_filepath, "r", encoding="utf-8") as inf:
    lines = inf.readlines()
train_idxs = random.sample(range(150), 50)
with open(dst_train_filepath, "w", encoding="utf-8") as outf1, open(dst_validate_filepath, "w", encoding="utf-8") as outf2:
    for i, line in enumerate(lines):
        if i in train_idxs:
            outf1.write(line)
        else:
            outf2.write(line)