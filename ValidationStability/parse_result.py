import os
import sys
import json

textbook = "corejava2"

def count_overlap(list1, list2, dim):
    return 1 if set(list1[:dim]).intersection(list2[:dim]) else 0

with open(textbook+".txt", "r", encoding="utf-8") as inf:
    right1 = 0
    right2 = 0
    right3 = 0
    right4 = 0
    right5 = 0
    samples = 0
    for line in inf:
        samples += 1
        pred1 = json.loads(line.split("\t")[0])
        pred2 = json.loads(line.split("\t")[1])
        
        right1 += count_overlap(pred1, pred2, 1)
        right2 += count_overlap(pred1, pred2, 2)
        right3 += count_overlap(pred1, pred2, 3)
        right4 += count_overlap(pred1, pred2, 4)
        right5 += count_overlap(pred1, pred2, 5)
    
    print(right1)
    print(right2)
    print(right3)
    print(right4)
    print(right5)
    print(samples)