import os
import sys
import json

from config import CJ2PATHUTIL

def extract_summary_for_section(textbook_dir, save_filepath):
    outf = open(save_filepath, "w", encoding="utf-8")
    for chapter in os.listdir(textbook_dir):
        for section in os.listdir(os.path.join(textbook_dir, chapter)):
            with open(os.path.join(textbook_dir, chapter, section), "r", encoding="utf-8") as inf:
                outf.write("{}\t{}\t{}".format(chapter, section, inf.readline()))
    outf.close()
    pass


if __name__ == "__main__":
    extract_summary_for_section(CJ2PATHUTIL.textbook_dir, CJ2PATHUTIL.textbook_summary_path)