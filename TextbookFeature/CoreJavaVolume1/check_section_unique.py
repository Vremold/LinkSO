import os

textbook_dir = "./textbook"
section_titles = set()

for chapter in os.listdir(textbook_dir):
    for section in os.listdir(os.path.join(textbook_dir, chapter)):
        if section in section_titles:
            print("wrng")
        section_titles.add(section)