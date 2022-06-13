import os

class MYSQL_INFO(object):
    host = "127.0.0.1"
    user = "root"
    passwd = "root"
    port = 3306
    db = "sotorrent"
    charset = "utf8"

class PATHUTIL(object):
    root_dir = "/home/dell/linkso"
    raw_data_dir = os.path.join(root_dir, "RawData")
    data_dir = os.path.join(root_dir, "SODataClean")

    # SO file
    raw_so_path = os.path.join(raw_data_dir, "so_posts.csv")
    raw_duplicate_so_path = os.path.join(raw_data_dir, "so_posts_duplicate.csv")
    so_path = os.path.join(data_dir, "so_posts.csv")
    duplicate_so_path = os.path.join(data_dir, "so_posts_duplicate.csv")

    # cache dir
    cache_dir = os.path.join(root_dir, "SODataClean", "cache")
