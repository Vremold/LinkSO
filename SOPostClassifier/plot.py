import os
import time
import sys

import matplotlib.pyplot as plt

src_loss_file = "./log/train_bert_loss.log"
src_accu_file = "./log/train_bert_accu.log"
out_file = "./log/bert.pdf"

x, train_accu, train_loss, valid_accu = [], [], [], []
with open(src_accu_file, "r", encoding="utf-8") as inf:
    for line in inf:
        splits = line.strip().split("\t")
        x.append(int(splits[0]))
        # train_accu.append(float(splits[1]))
        valid_accu.append(float(splits[2]))
with open(src_loss_file, "r", encoding="utf-8") as inf:
    for _ in range(len(x)):
        loss = 0
        for _ in range(338):
            loss += float(inf.readline().strip())
        train_loss.append(loss/338)

fig, ax1 = plt.subplots()
ax1.plot(x, train_loss, color="r", label="Train Loss")
ax2 = ax1.twinx()
# ax2.plot(x, train_accu, color="g", label="Train Accuracy")
ax2.plot(x, valid_accu, color="b", label="Valid Accuracy")
fig.legend()
plt.savefig(out_file)