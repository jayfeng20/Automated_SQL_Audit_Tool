import re
import pymysql

"""
Query object that is used to extract and analyze a sql query from audit_results.txt

Change SQL connection parameters accordingly.

[input_block] should be in the form of a string:
    [File Name]: fileName
    [Function Name]: functionName   
    [Query Duration]: XXXs
    [Query]: 
    Line 1: ...
    Line 2: ....
    Line 3: ...
    Line 4: ....

Field types initialized at construction:
[file_name]: str
[function_name]: str
[duration]: float
[q] stands for query: str
[conn]: pymysql conn object
[cur]: pymysql cursor object
[dict_list]: list of dictionary
"""


class Query:
    def __init__(
        self,
        input_block,
        host="localhost",
        user="USER",
        pwd="PWD",
        db="DB",
    ):
        self.file_name = re.search(r"(\[File Name\]:)(\w+.php)", input_block).group(2)
        self.function_name = re.search(
            r"(\[Function Name\]:)([\w_]+)", input_block
        ).group(2)
        self.duration = float(re.search(r"(\d+\.\d+)", input_block).group(1))
        start_index = re.search(r"\[Query\]:", input_block).end()
        lines = input_block[start_index:].strip().split("\n")
        # del lines[len(lines) - 1]
        self.q = ""
        for line in lines:
            line = line[7:]
            self.q += line + "\n"
        print(self.q)
        self.conn = pymysql.connect(host=host, user=user, password=pwd, db=db)
        self.cur = self.conn.cursor()
        self.dict_list = self.__explain_dict()

    # # explains the query and outputs all rows as a result of the EXPLAIN query, as a tuple
    # def explain(self):
    #     explain = "EXPLAIN" + self.q
    #     self.cur.execute(explain)
    #     output = self.cur.fetchall()
    #     return output

    # construct a dictionary/hashmap based on the output and store it as a field
    def __explain_dict(self):
        explain = "EXPLAIN" + self.q
        self.cur.execute(explain)
        explain = self.cur.fetchall()
        dict_list = []
        for row in explain:
            dic = {}
            dic["id"] = row[0]
            dic["select_type"] = row[1]
            dic["table"] = row[2]
            dic["partitions"] = row[3]
            dic["type"] = row[4]
            dic["possible_keys"] = row[5]
            dic["key"] = row[6]
            dic["key_len"] = row[7]
            dic["ref"] = row[8]
            dic["rows"] = row[9]
            dic["filtered"] = row[10]
            dic["Extra"] = row[11]
            dict_list.append(dic)
        return dict_list

    # close the connection
    def close(self):
        self.conn.close()
