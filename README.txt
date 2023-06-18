![Snake animation](https://github.com/jayfeng20/Automated_SQL_Audit_Tool/blob/output/github-contribution-grid-snake.svg)

Overall architecture:

[.php] files -> original php files that have all the classes, functions and queries
[python_scripts] -> custom folder that contains code needed for complete audition
[query.py] -> Query object file
[populate.py] -> script to populate an entire database with POPULATE procedure already imported to MYSQL
[audit_results] -> contains the audit results
[auto_construct_tests.py] -> python auto_construct_tests.py XXX.php to modify the file 
[generate_datetime.py] -> simply generate a SQL datetime object which can be used for function parameter
[generate_report.py] -> contains functions needed for generating reports, and, at the end of the file,
scripts that use those functions to generate reports




0th step, make sure you're in the root directory of your project

First, the original .php files that contain sql queries
have to have:
[1]. One class declaration
[2]. At least one function declaration within that class
[3]. Those functions have to have at least one return statement 
and the functions have to have ActiveRecord SQL queries

Then, you can use 
    > python root/.../auto_construct_tests.py root/.../OG_file.php
which does a few things:
[1]. Set up environment
[2]. Modify output objects ready for parsing
[3]. Construct an instance of the class object and 
a function call for every function within it

!!!!! LIMITATIONS:
[1]. Functions DO NOT have default parameters,
please refer to the OG file to locate the type
of function parameters, and manually input them.
[2]. Next step can only be executed ONE function
at a time, so please comment out all the functions
that you're testing right now, along with their 
[var_dump] statements.

Second, when the .php file is ready, execute the following command:
> python root\...\generate_report.py root\...\OG_file.php

The report will then be generated to 
path = r"ROOT\query_tests\audit_results.txt"
which is the default path.


