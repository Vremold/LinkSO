import os
import sys
import json
import csv
import re

from so_config import PATHUTIL

raw_duplicate_so_path = PATHUTIL.raw_duplicate_so_path
so_path = PATHUTIL.so_path
id_posts = dict()

def extract_duplicate_to(hyperlink):
    match = re.search(r"/questions/(\d+)", hyperlink)
    if not match:
        print(hyperlink)
    return int(match.group(1))

def match_duplicate(raw_duplicate_so_path, so_path, dst_so_path):
    with open(so_path, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            qid = int(line[0])
            id_posts[qid] = line

    with open(raw_duplicate_so_path, "r", encoding="utf-8") as inf, open(dst_so_path, "w", encoding="utf-8") as outf:
        next(inf)
        csv_reader = csv.reader(inf)
        csv_writer = csv.writer(outf)
        cnt = 0
        for line in csv_reader:
            duplicate_to = extract_duplicate_to(line[-1])
            if "1395551" in line[-1]:
                print(duplicate_to)
            if duplicate_to in id_posts:
                cnt += 1
                csv_writer.writerow(line[:-1] + id_posts[duplicate_to])
        print(cnt)

def test(so_path):
    with open(so_path, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            qid = int(line[0])
            if qid == 1395551:
                print(line)
                break

if __name__ == "__main__":
    match_duplicate(PATHUTIL.raw_duplicate_so_path, PATHUTIL.so_path, PATHUTIL.duplicate_so_path)
    # test(PATHUTIL.so_path)

            