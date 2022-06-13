import os
import sys
import json
import csv

from so_config import PATHUTIL

def apply_model_results(test_result_path, src_so_path, dst_so_path):
    selected_qids = set()
    with open(test_result_path, "r", encoding="utf-8") as inf:
        for line in inf:
            obj = json.loads(line)
            for item in obj:
                if item[1] == 1:
                    selected_qids.add(item[0])
    with open(src_so_path, "r", encoding="utf-8") as inf, open(dst_so_path, "w", encoding="utf-8") as outf:
        outf.write(inf.readline())
        csv_reader = csv.reader(inf)
        csv_writer = csv.writer(outf)
        for line in csv_reader:
            if int(line[0]) in selected_qids:
                csv_writer.writerow(line)

if __name__ == "__main__":
    test_result_path = "../SOPostClassifierEx/test_result.json"
    ## filter suitable data according to predicted result
    apply_model_results(test_result_path, PATHUTIL.raw_so_path, PATHUTIL.so_path)