import generate_report as gr

path = r"ROOT\query_tests\python_scripts\audit_results.txt"

with open(path, "r") as file:
    old_content = file.read()

s = """
This text file contains audit results for SQL queries in application/models/*
Sample data: Each table has 100,000 rows.


[Query Performances]
"""

old_content = old_content.strip("\n")
old_content = old_content.strip("============================")
list = old_content.split("============================\n\n============================")
for block_str in list:
    q = gr.construct_query(block_str)
    report = gr.generate_report(q)
    gr.write_to_file(report, path)
