import os
import sys
import json
import re
import csv
import random

root_dir = "../../"
raw_data_dir = os.path.join(root_dir, "RawData")
raw_so_path = os.path.join(raw_data_dir, "so_posts.csv")
jdk_api_doc_path = os.path.join(root_dir, "JDKCrawler", "export", "apis.json")

class DatasetBuilder(object):
    def __init__(self, labeled_idx_file):
        with open(labeled_idx_file, "r", encoding="utf-8") as inf:
            labeled_idxs = json.load(inf)
        print(len(labeled_idxs))
        a = [1, 2, 3]
        random.shuffle(a)
        print(a)

        self.labeled_negative_idxs = [k for k, v in labeled_idxs.items() if v == 0]
        self.labeled_positive_idxs = [k for k, v in labeled_idxs.items() if v == 1]
        random.shuffle(self.labeled_negative_idxs)
        random.shuffle(self.labeled_positive_idxs)

        self.train_idxs = self.labeled_negative_idxs[:2700] + self.labeled_positive_idxs[:2700]
        self.validate_idxs = self.labeled_negative_idxs[2700:] + self.labeled_positive_idxs[2700:]

        random.shuffle(self.train_idxs)
        random.shuffle(self.validate_idxs)

    def preprocess(self, line:str):
        line = line.replace("--CODE--", "")
        return line
    
    def construct_dataset(self, dst_dir):
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        train_dst = open(os.path.join(dst_dir, "train"), "w", encoding="utf-8")
        validate_dst = open(os.path.join(dst_dir, "validate"), "w", encoding="utf-8")
        train_dst = csv.writer(train_dst)
        validate_dst = csv.writer(validate_dst)
        with open(raw_so_path, "r", encoding="utf-8") as inf:
            next(inf)
            csv_reader = csv.reader(inf)
            for line in csv_reader:
                if line[0] in self.train_idxs:
                    label = 1 if line[0] in self.labeled_positive_idxs else 0
                    train_dst.writerow([
                        line[2],
                        self.preprocess(line[3]),
                        label
                    ])
                elif line[0] in self.validate_idxs:
                    label = 1 if line[0] in self.labeled_positive_idxs else 0
                    validate_dst.writerow([
                        line[2],
                        self.preprocess(line[3]),
                        label
                    ])
        pass

if __name__ == "__main__":
    DatasetBuilder("./labeled.json").construct_dataset("./data")
