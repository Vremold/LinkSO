import sys
import os
import csv

import pymysql

from so_config import PATHUTIL, MYSQL_INFO

class MySqlDumper(object):
    def __init__(self):
        self.conn = pymysql.connect(
            host=MYSQL_INFO.host,
            user=MYSQL_INFO.user,
            passwd=MYSQL_INFO.passwd,
            port=MYSQL_INFO.port,
            db=MYSQL_INFO.db,
            charset=MYSQL_INFO.charset
        )

    def dump_java_question(self, save_filepath):
        cur = self.conn.cursor()
        outf = open(save_filepath, "a+", encoding="utf-8")
        csv_writer = csv.writer(outf)
        csv_writer.writerow(["Qid", "AAid", "Qtitle", "Qbody", "Qtags"])
        while True:
            print("[Dumping Questions] Dumped Questions: {}".format(self.dumped_questions))

            sql = "select * from `JavaPostQuestion` where Qid >= %d and Qid < %d" % (self.dumped_questions * self.step, self.dumped_questions * self.step + self.step)
            cur.execute(sql)
            data = cur.fetchall()
            self.dumped_questions += 1
            if not data:
                print("Finish dumping java questions....")
                break
            for sample in data:
                csv_writer.writerow(sample)
        outf.close()
        cur.close()
    
    def dump_java_answer(self, save_filepath, save_question_filepath):
        cur = self.conn.cursor()
        outf = open(save_filepath, "a+", encoding="utf-8")
        csv_writer = csv.writer(outf)
        csv_writer.writerow(["Qid", "AAid", "Qtitle", "Qbody", "Qtags", "Aid", "Abody"])
        with open(save_question_filepath, "r", encoding="utf-8") as inf:
            next(inf)
            csv_reader = csv.reader(inf)
            for line in csv_reader:
                qid = int(line[0])
                try:
                    aaid = int(line[1])
                except:
                    sql = "select Id, Body from Posts where ParentId = %d and PostTypeId = 2 order by score DESC limit 1" % (qid)
                else:
                    sql = "select Id, Body from Posts where Id = %d" % (aaid)
                
                finally:
                    cur.execute(sql)
                    for sample in cur.fetchall():
                        line.extend(sample)
                        # print(line)
                        # sys.exit(0)
                        csv_writer.writerow(line)
        outf.close()
        cur.close()


def test(question_filepath):
    with open(question_filepath, "r", encoding="utf-8") as inf:
        next(inf)
        csv_reader = csv.reader(inf)
        for line in csv_reader:
            try:
                x = int(line[1])
            except:
                print(line)
                break

if __name__ == "__main__":
    question_dst_file = os.path.join(PATHUTIL.cache_dir, "dumped_so_question.csv")
    so_dst_file = os.path.join(PATHUTIL.cache_dir, "dumped_so.csv")
    md = MySqlDumper()

    # step 1
    md.dump_java_question(question_dst_file)
    # step 2
    md.dump_java_answer(so_dst_file, question_dst_file)