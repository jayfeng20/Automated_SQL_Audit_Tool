import pymysql

"""
After loading the two procedures described in
https://github.com/kedarvj/mysql-random-data-generator.
Run this script to populate all tables in a ien database
"""

# Connect to the local MySQL database
conn = pymysql.connect(
    host="localhost", user="USERNAME", password="PWD", database="DBNAME"
)


# Create a cursor
cursor = conn.cursor()


# Get the table names from the database
query = "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s"
cursor.execute(query, ("connectcare"))
tables = cursor.fetchall()


# switch = 0 - truncate mode (clear table data) | switch = 1 - populate mode
switch = 1

# Need populate_fk procedure to populate these tables
fk_tables = []


# Iterate over the tables
for table in tables:
    table_name = table[0]
    if switch == 0:
        # remove table data
        print(f"{table_name} data clearing initialized")
        query = f"TRUNCATE TABLE {table_name}"
        cursor.execute(query)
        print(f"{table_name} data cleared.")

    elif switch == 1:
        print(f"populating {table_name}...")
        try:
            query = f"CALL populate('connectcare', '{table_name}', 100000, 'N')"
            cursor.execute(query)
            conn.commit()
            print(f"{table_name} population completed.")
        except:
            print(f"{table_name} data clearing initialized")
            query = f"TRUNCATE TABLE {table_name}"
            cursor.execute(query)
            print(f"{table_name} data cleared.")
            query = f"CALL populate_fk('connectcare', '{table_name}', 100000, 'N')"
            cursor.execute(query)
            conn.commit()
            print(f"{table_name} population completed.")
            fk_tables.append(table_name)

# print(fk_tables)

# Close the cursor and connection
cursor.close()
conn.close()
