#ENTER TIME LINE
#GRAB TEST SUITE RESULTS FROM THAT TIME LINE
from CLI.Execution.DatabaseHandler import DatabaseHandler
import matplotlib.pyplot as plt

db_handler = DatabaseHandler()
connection = db_handler.connection()
table_name = 'table_name'
id = 'timeline'
id_type = 'created'
db_handler.get_data(connection, table_name, id, id_type)

#CLEAN DATA

#HOW many passes in time line?
test_suite_results = []
total_passes = 0
for test_suite_result in test_suite_results:
    total_passes += test_suite_result.getTotalPasses()

#HOW many failures in time line?
total_failures = 0
for test_suite_result in test_suite_results:
    total_failures += test_suite_result.getTotalPasses()

#HOW many errors in time line?
test_suite_results = []
total_errors = 0
for test_suite_result in test_suite_results:
    total_errors += test_suite_result.getTotalPasses()

