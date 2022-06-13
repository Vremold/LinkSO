import os

textbook_dir = "./textbook"
section_to_chapter = dict()

for chapter in os.listdir(textbook_dir):
    for section in os.listdir(os.path.join(textbook_dir, chapter)):
        if section in section_to_chapter and section != "Summary":
            print("wrng")
            print(chapter, section)
            print(section_to_chapter[section], section)
        elif section != "Summary":
            section_to_chapter[section] = chapter
