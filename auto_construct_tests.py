import re
import sys

# Check if the PHP file path is provided as a command-line argument
if len(sys.argv) < 2:
    print("Please provide the path to the PHP file as a command-line argument.")
    exit()

# Get the PHP file path from the command-line argument
php_file_path = sys.argv[1]

# Read the PHP file
with open(php_file_path, "r") as file:
    php_code = file.read()


# Exclude the class declarations within /* */ block comments and replace them with <COMMENT BLOCK>
comment_block_pattern = r"\/\*[\s\S]*?\*\/"
comment_blocks = comment_blocks = re.findall(comment_block_pattern, php_code)
php_code = re.sub(comment_block_pattern, "<COMMENT BLOCK>", php_code)

# Extract the class name from the PHP file
class_declaration_pattern = r"[cC]lass (\w+)"

class_name_match = re.search(class_declaration_pattern, php_code)
if class_name_match:
    php_class_name = class_name_match.group(1)
    php_code = re.sub(php_class_name, php_class_name + "_test", php_code)
    php_class_name += "_test"
else:
    print("Could not find the class name.")
    exit()

# Generate the object name based on the class name
php_object_name = php_class_name[0].lower() + php_class_name[1:]

# Define the dump lines to be added
dump_lines = """
    var_dump("Queries run:" . $this->db->last_query());
    var_dump($this->db->query('SHOW PROFILES')->result_array());
   
"""

# Define the env setup
env_lines = """
\n
define('ENVIRONMENT', getenv('APPSETTING_ENVIRONMENT'));
define('APPPATH', realpath('application') . '\\\\');
define('VIEWPATH', APPPATH . 'views' . '\\\\');
define('BASEPATH', realpath('system') . '\\\\');
ob_start();
require_once BASEPATH . 'core/CodeIgniter.php';
ob_end_clean(); 
\n
"""

# find <? php
insert_position = php_code.find("<?php") + len("<?php")

# prepend env_lines
php_code = php_code[:insert_position] + env_lines + php_code[insert_position:]

# split php_code for easier process
lines = php_code.split("\n")

# process return statements
modified_lines = []
for line in lines:
    # Match return statements
    match = re.match(r"^\s*(return[^;]+;)", line)
    if match:
        modified_lines.append(dump_lines)
        modified_lines.append(line)
    else:
        modified_lines.append(line)

php_code = "\n".join(modified_lines)
lines = php_code.split("\n")

modified_php_code = []
# extract all function names
functions = []
function_name_regex = r"\s*(?:public\s+)?function\s+(\w+)\s*\([^)]*\)"
set_profile = "$this->db->query('SET profiling = 1');"
after_function = False
for line in lines:
    # Match return statements
    match = re.match(function_name_regex, line)

    if after_function:
        modified_php_code.append(line)
        modified_php_code.append(set_profile)
        after_function = False
    else:
        modified_php_code.append(line)
    if match:
        m = re.search(function_name_regex, line)
        functions.append(m.group(1))
        after_function = True


php_code = "\n".join(modified_php_code)


# insert comment blocks back
for comment_block in comment_blocks:
    php_code = php_code.replace("<COMMENT BLOCK>", comment_block, 1)

# Construct the class object
php_code = php_code + "\n${} = new {}();\n".format(php_object_name, php_class_name)

# Add file name
filename = "$filename = $_SERVER['PHP_SELF'];\nvar_dump($filename);\n"
php_code += f"{filename}"
php_code += "var_dump('File_name: ' . substr($filename,14));\n"

# contruct function calls
for fn in functions:
    php_code += f"var_dump('Function_name: ' . '{fn}');\n"
    php_code += f"var_dump(${php_object_name}->{fn}('" "'));\n"


# Write the updated PHP code back to the file
with open(php_file_path, "w") as file:
    file.write(php_code)
