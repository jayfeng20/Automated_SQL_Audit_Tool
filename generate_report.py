import sys
import subprocess
import re
import query


# path to audit_results file
path = r"ROOT\cc-portal\query_tests\python_scripts\audit_results.txt"


# Parses the output of running a auto_construct.py modified php file and returns it as a string
# in the form of
# ============================
# [File Name]:account_group.php
# [Function Name]:getGroupAccountList()
# [Query Duration]: 0.01407850s
# [Query]:
# Line 1: SELECT *
# Line 2: FROM `account_group` as `AG`
# Line 3: JOIN `account_group_mapping` as `AGM` ON `AG`.`id` = `AGM`.`account_group_id`
# Line 4: WHERE `AG`.`id` IN ('')"
# ============================
# which is ready to be turned into a [Query] object
def parse_output(output, path):
    if re.search("error", output) != None:
        print(output)
        return None

    block_str = "\n========================================================\n"
    # Extract the file name
    file_name_match = re.search(r"File_name: (\w+)", output)
    if file_name_match:
        file_name = file_name_match.group(1)
        block_str += "[File Name]:" + file_name + ".php\n"

    # Extract the function name
    function_name_match = re.search(r"Function_name: (\w+)", output)
    if function_name_match:
        function_name = function_name_match.group(1)
        block_str += "[Function Name]:" + function_name + "()\n"

    # Extract the query duration
    duration_match = re.search(r'(?s:.*)("(\d+\.\d+)")', output)
    if duration_match:
        duration = duration_match.group(1)[1:-1]
        block_str += f"[Query Duration]: {duration}s\n"

    # Extract the query

    start_index = re.search(r"(?s:.*)Queries run:", output).end()

    end_index = re.search(r"array\(", output[start_index:]).start() + start_index

    query = output[start_index:end_index]
    queries = query.split("\n")
    query = ""
    for i, q in enumerate(queries):
        if q.strip() == "":
            continue
        # if i == 0:
        #     start_index = re.search('"', q).end()
        #     q = q[start_index:]
        q = q.strip()
        query += f"Line {i+1}: " + q.strip('"') + "\n"

    block_str += "[Query]:\n" + query

    block_str += "========================================================\n"

    return block_str


# Constructs and returns a Query object
def construct_query(block_str):
    return query.Query(block_str)


# Takes in a query object and process it, then generate a report block
def generate_report(query):
    # General section
    report = ""
    report += "========================================================\n"
    report += "[File name]: " + query.file_name + "\n"
    report += "[Function name]: " + query.function_name + "\n"
    report += "[Duration]: " + str(query.duration) + "s\n"
    query_split_lines = query.q.split("\n")
    report += "[Raw query]:\n"
    for i, l in enumerate(query_split_lines):
        report += f"Line {i}: {l}\n"

    # EXPLAIN sectino
    report += "[Query execution result]:\n"
    for ele in query.dict_list:
        abbrev = ele["table"]
        table_name = find_full_table_name(query.q, abbrev)
        report += "\t" + f"[Table: {table_name}]:\n"
        for k, v in ele.items():
            report += "\t\t" + f"[{k}] => {v}\n"

    # Suggestion section
    report += "[Suggestions]:\n"
    report += make_suggestions(query.dict_list, query.q) + "\n"

    report += "========================================================\n"
    return report


def make_suggestions(dict_list, query_str):
    suggestions = ""
    for ele in dict_list:
        abbrev = ele["table"]
        table_name = find_full_table_name(query_str, abbrev)
        if table_name == "None":
            continue
        else:
            suggestions += "\t" + f"[Table: {table_name}]:\n"

            # Things that are good
            suggestions += "\t\t[Passed]:\n"
            # Case 1
            if ele["type"] in ["const", "eq_ref"]:
                suggestions += (
                    f"\t\t\tNo full scan on table {table_name} -> type: {ele['type']}\n"
                )
            # Case 2
            if ele["key"] != None and ele["possible_keys"] != None:
                if ele["key"] in ele["possible_keys"]:
                    suggestions += f"\t\t\tIndexed key {ele['key']} used for table {table_name} -> type: {ele['type']}\n"

            # Things that need improvements
            suggestions += "\t\t[Warning]:\n"
            if ele["type"] not in ["const", "eq_ref"]:
                suggestions += f"\t\t\tFUll SCAN detected on table {table_name} -> type: {ele['type']}\n"

    if suggestions == "":
        suggestions = "None"
    return suggestions


def find_full_table_name(query, abbrev):
    if abbrev == None:
        return "None"
    elif len(abbrev) > 3:
        return abbrev
    else:
        method_1 = re.search(f"(?s:.*)(`)([\w_]+)(`\s*[Aa][Ss]\s*`{abbrev}`)", query)
        method_2 = re.search(f"(?s:.*)(`)([\w_]+)(`\s*`{abbrev}`)", query)
        method_3 = re.search(f"(?s:.*)([\w_]+)([Aa][Ss]\s*`{abbrev})", query)
        if method_1 != None:
            return method_1.group(2)
        elif method_2 != None:
            return method_2.group(2)
        else:
            return method_3


# Write report to path file
def write_to_file(report, path):
    with open(path, "r") as file:
        old_content = file.read()
        start_index = old_content.rfind(
            "========================================================"
        ) + len("========================================================\n")
    if start_index == len("============================") * 2 - 1:
        start_index = old_content.find("[Query Performances]\n\n") + len(
            "[Query Performances]"
        )

    with open(path, "w") as file:
        new_content = old_content[:start_index] + report
        file.write(new_content)


####################################################################################


# # Check if the PHP file is provided as a command-line argument
# if len(sys.argv) < 2:
#     print("Please provide the PHP file as a command-line argument.")
#     sys.exit(1)

# # Execute the PHP file and capture the output
# php_file = sys.argv[1]
# process = subprocess.Popen(["php", php_file], stdout=subprocess.PIPE)
# output, _ = process.communicate()
# output = output.decode()

# # Call the function to parse the output
# block_str = parse_output(output, path)
# q = construct_query(block_str)
# report = generate_report(q)
# write_to_file(report, path)
