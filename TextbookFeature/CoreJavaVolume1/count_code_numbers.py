import os

src_dir = "textbook_code"
cnt = 0
lens = 0

def handle_dir(indir):
    global cnt, lens
    for filename in os.listdir(indir):
        filepath = os.path.join(indir, filename)
        if os.path.isdir(filepath):
            handle_dir(filepath)
        elif filename.endswith(".java"):
            with open(filepath, "r", encoding="utf-8") as inf:
                lines = inf.readlines()
                lens += len([line for line in lines if line.strip()])
            cnt += 1

handle_dir(src_dir)
print(cnt)
print(lens)
print(lens/cnt)
