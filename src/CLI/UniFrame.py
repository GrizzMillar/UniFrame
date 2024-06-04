from FrameworkObjects.Framework import Framework
from Execution.TestExecutionEngine import TestExecutionEngine
from FrameworkObjects.TestSuite import TestSuite
from FrameworkObjects.TestMode import TestMode
from FrameworkObjects.TestRunner import TestRunner
from Execution.DatabaseHandler import DatabaseHandler
from SelectOptionMenu import SelectOptionMenu
from Reporting.Results import TestResult, CoverageResult, TestSuiteResult, EnvironmentDetails, TestSummary, ExecutionDetails
from Reporting.Report import Report
from Reporting.ResultReporter import ResultReporter
import argparse
import re
import os
import xml.etree.ElementTree as ET
import json

#COMMANDS
#1. Create a framework
#2. View framework
#3. Add Test Suite
#4. Reload Test Suite
#5. View Test Suites
#6. Run Suite

#COLLECTION OD DATA
#Rather than constantly having a back and forth connection between the backend and database there will be a function for loading data 

#proj1 = framework("Test 1", "Test Dir 1", "Test Description 1")
#proj2 = framework("Test 2", "Test Dir 2", "Test Description 2")
frameworks = []
#frameworks.append(proj1)
#frameworks.append(proj2)

def main():
    decorator = '***********************************************************************************\n'
    decorator += '*********|******|*|****|*||*||||||*|||||||******||*********|****|*****||||||******\n'
    decorator += '*********|******|*|*|**|*||*|******|*****|*****|**|*******|*|**|*|****|***********\n'
    decorator += '*********|******|*|**|*|*||*|||||**|||||||****||||||*****|***||***|***||||********\n'
    decorator += '*********|******|*|***||*||*|******|*****|***|******|***|**********|**|***********\n'
    decorator += '**********||||||**|****|*||*|******|******|*|********|*|************|*||||||******\n'
    print(decorator)
    parser = argparse.ArgumentParser(description="Command Line Tool for UniTest")
    parser.add_argument("-create", action='store_true', help="Create a new framework")
    parser.add_argument("-add", choices=['test_suite', 'test_mode', 'test_runner'], help="Create a test suite or test mode")
    parser.add_argument("-framework_name", help="Specify the framework name for the test suite/test mode to be added to")
    parser.add_argument("-view", action='store_true', help="View frameworks")
    parser.add_argument("-run", nargs=2, metavar=('framework_NAME', 'TEST_MODE_NAME'), help="Run Suite")
    parser.add_argument("-suites", nargs='+', help="List of test suites to run. Use 'ALL' ro tun all suites", default=['ALL'])
    args = parser.parse_args()

    if args.create:
        CreateNewFramework()
    elif args.add:
        if args.add == 'test_suite':
            AddTestSuite()
        elif args.add == 'test_mode':
            AddTestMode()
        elif args.add == 'test_runner':
            AddTestRunner()
    elif args.view:
        application()
    elif args.run:
        framework_name, test_mode_name = args.run
        test_suites = args.suites
        RunSuite(framework_name, test_suites, test_mode_name)

def application():
    loadframeworks()
    menu_title = "Frameworks"
    start_index = 0
    framework_names = ['Exit'] + [framework.getName() for framework in frameworks]
    
    while True:
        framework_menu = SelectOptionMenu(menu_title, start_index, framework_names)
        choice = framework_menu.getUserInput()
        if choice == 0:
            print('Exiting...')
            break
        else:
            details = frameworks[choice-1].getDetails()
            print(details)
            framework_details_menu(frameworks[choice-1])

def framework_details_menu(framework):
    start_index = 0
    framework_options = ['Back', 'View Test Suites', 'View Test Runners', 'View Test Modes', 'View Results History', 'View Configuration Settings']
    while True:
        action_menu = SelectOptionMenu('What would you like to do?', start_index, framework_options)
        choice = action_menu.getUserInput()
        if choice == 0:
            break
        elif choice == 1:
            if len(framework.getTestSuites()) == 0:
                print("There are no recorded test suites in this framework")
                break
            while True:
                test_suite_names = ['back'] +[test_suite.getName() for test_suite in framework.getTestSuites()]
                test_suite_menu = SelectOptionMenu('What would you like to do?', start_index, test_suite_names)
                choice = test_suite_menu.getUserInput()
                if choice == 0:
                    break
                else:
                    test_suite = framework.getTestSuites()[choice-1]
                    details = test_suite.getDetails()
                    print(details)
                    while True:
                        test_suite_options = ['back', 'Update Test Suite', 'Delete Test Suite', 'View Results History']
                        test_suite_options_menu = SelectOptionMenu('What would you like to do?', start_index, test_suite_options)
                        test_suites_choice = test_suite_options_menu.getUserInput()
                        if test_suites_choice == 0:
                            break
                        elif test_suites_choice == 1:
                            #Establish database connection
                            db_controller = DatabaseHandler()
                            db_connection = db_controller.connection()
                            #Ask user for new config file
                            config_dir = str(input("Please provide the location of your test suite configuration file: "))
                            try:
                                config = parseConfigXML(config_dir)
                            except ET.ParseError as e:
                                print(f"Error parsing the configuration file: {e}")
                                return
                            except FileNotFoundError:
                                print(f"Configuration file not found at {config_dir}")
                                return
                            required_fields = ['framework_name', 'test_suite_name', 'test_suite_description', 'test_suite_location']
                            missing_fields = [field for field in required_fields if field not in config['configuration']['test_suite']]
                            if missing_fields:
                                print(f"Test Suite configuration failed as the following fields are missing:\n")
                                missing = ''
                                for field in missing_fields:
                                    missing += f"{field}\n"
                                print(missing)
                                return
                            empty_fields = []
                            values = {"framework_name": config['configuration']['test_suite']['framework_name'], "test_suite_name": config['configuration']['test_suite']['test_suite_name'], "test_suite_description": config['configuration']['test_suite']['test_suite_description'], "test_suite_location": config['configuration']['test_suite']['test_suite_location']}
                            for key, value in values.items():
                                if value is None: 
                                    empty_fields.append(key)
                            if empty_fields:
                                print(f"Test Suite configuration failed as the following fields are empty:\n")
                                empty = ''
                                for field in empty_fields:
                                    empty += f"{field}\n"
                                    print(empty)
                                return
                            
                            framework_exists = db_controller.CheckExistence(db_connection, 'frameworks', config['configuration']['test_suite']['framework_name'], 'framework_name')
                            if framework_exists == False:
                                print(f"A Framework with the name '{config['configuration']['test_suite']['framework_name']}' does not exist. Please choose a another name")
                                return
                            #Compare config files
                            coverage_files = config['configuration']['test_suite'].get('coverage_files', None)
                            if coverage_files:
                                if isinstance(coverage_files, dict):
                                    files = coverage_files.get('file', [])
                                    if isinstance(files, str):
                                        coverage_files_list = [files]
                                    else:
                                        coverage_files_list = files
                                else:
                                    print("Unexpected format for coverage files")
                                    return
                            else:
                                coverage_files_list = []
                            coverage_files_str = json.dumps(coverage_files_list)
                            new_test_suite = TestSuite(test_suite.getID(),config['configuration']['test_suite']['test_suite_name'], config['configuration']['test_suite']['test_suite_description'], config['configuration']['test_suite']['test_suite_location'])
                            for coverage_file in coverage_files_str:
                                new_test_suite.addCoverageFiles(coverage_file)
                            changed_fields = {}
                            if new_test_suite.getName() != test_suite.getName():
                                data = db_controller.get_data(db_connection, 'frameworks', config['configuration']['test_suite']['framework_name'], 'framework_name')
                                framework_id = data[0][0]
                                test_suite_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_suites', config['configuration']['test_suite']['test_suite_name'], 'test_suite_name', framework_id)
                                if test_suite_exists:
                                    print(f"A Test Suite with the name '{config['configuration']['test_suite']['test_suite_name']}' already exists within the framework '{config['configuration']['test_suite']['framework_name']}'. Please choose a another name")
                                    return
                                changed_fields['test_suite_name'] = new_test_suite.getName()
                            if new_test_suite.getDescription() != test_suite.getDescription():
                                changed_fields['test_suite_description'] = new_test_suite.getDescription()
                            if new_test_suite.getTestScript() != test_suite.getTestScript():
                                changed_fields['test_script_location'] = new_test_suite.getTestScript()
                            if new_test_suite.getCoverageFiles() != test_suite.getCoverageFiles():
                                if new_test_suite.getCoverageFiles() is None:
                                    changed_fields['coverage_files'] = None
                                else:
                                    changed_fields['coverage_files'] = coverage_files_str

                            if not changed_fields:
                                print("There are no changes detected")
                            else:
                                #GET TEST SUITE ID
                                for field, new_value in changed_fields.items():
                                    db_controller.update_data(db_connection, 'test_suites', test_suite.getID(), field, new_value)
                                db_controller.closeConnection(db_connection)
                                print("Test Suite updated!")
                        elif test_suites_choice == 2:
                            db_controller = DatabaseHandler()
                            db_connection = db_controller.connection()
                            confirmation = input(f"Are you sure you want to delete test suite {test_suite.getID()}? (yes/no): ").lower()
                            if confirmation not in ['yes', 'y']:
                                print("Deletion cancelled")
                            else:
                                db_controller.delete_data(db_connection, 'test_suites', test_suite.getID(), 'test_suite_id')
                                print('Test Suite Deleted')
                            db_controller.closeConnection(db_connection)
                        elif test_suites_choice == 3:
                            #Assign array of results titles for test suite
                            results = test_suite.getResultsHistory()
                            if not results:
                                print("There are no recorded results for this test suite")
                            else:
                                while True:                                   
                                    results_dates = ['back'] +[result.getDate() for result in results]
                                    results_selection = SelectOptionMenu('Choose a date', start_index, results_dates)
                                    results_selection_choice = results_selection.getUserInput()
                                    if results_selection_choice == 0:
                                        break
                                    else:
                                        test_suite_result = test_suite.getResult(results_selection_choice-1)
                                        print(test_suite_result.display())
        elif choice == 2:
            if len(framework.getTestRunners()) == 0:
                print("There are no recorded test runners in this framework")
                break
            while True:
                test_runner_names = ['back'] +[test_runner.getName() for test_runner in framework.getTestRunners()]
                test_runner_menu = SelectOptionMenu('Select a Test Runner to view?', start_index, test_runner_names)
                choice = test_runner_menu.getUserInput()
                if choice == 0:
                    break
                else:
                    test_runner = framework.getTestRunners()[choice-1]
                    details = test_runner.getDetails()
                    print(details)
        elif choice == 3:
            if len(framework.getTestModes()) == 0:
                print("There are no recorded test modes in this framework")
                break
                
            while True:
                test_mode_names = ['back'] +[test_mode.getTestModeName() for test_mode in framework.getTestModes()]
                test_mode_menu = SelectOptionMenu('What would you like to do?', start_index, test_mode_names)
                choice = test_mode_menu.getUserInput()
                if choice == 0:
                    break
                else:
                    test_mode = framework.getTestModes()[choice-1]
                    details = test_mode.getDetails()
                    print(details)
                    while True:
                        test_mode_options = ['back', 'Update Test Mode', 'Delete Test Mode']
                        test_mode_options_menu = SelectOptionMenu('What would you like to do?', start_index, test_mode_options)
                        choice = test_mode_options_menu.getUserInput()
                        if choice == 0:
                            break
                        elif choice == 1:
                            #Establish database connection
                            db_controller = DatabaseHandler()
                            db_connection = db_controller.connection()
                            #Ask user for new config file
                            config_dir = str(input("Please provide the location of your test suite configuration file: "))
                            try:
                                config = parseConfigXML(config_dir)
                            except ET.ParseError as e:
                                print(f"Error parsing the configuration file: {e}")
                                return
                            except FileNotFoundError:
                                print(f"Configuration file not found at {config_dir}")
                                return
                            required_fields = ['framework_name', 'test_mode_name', 'host_ip_address', 'username', 'rsa_key_path', 'test_path', 'requirements_path', 'env_vars']
                            missing_fields = [field for field in required_fields if field not in config['configuration']['test_mode']]
                            if missing_fields:
                                print(f"Test Mode configuration failed as the following fields are missing:\n")
                                missing = ''
                                for field in missing_fields:
                                    missing += f"{field}\n"
                                print(missing)
                                return
                            
                            empty_fields = []
                            values = {"framework_name": config['configuration']['test_mode']['framework_name'], "test_mode_name": config['configuration']['test_mode']['test_mode_name'], "host_ip_address": config['configuration']['test_mode']['host_ip_address'], "username": config['configuration']['test_mode']['username'], "rsa_key_path": config['configuration']['test_mode']['rsa_key_path'], "test_path": config['configuration']['test_mode']['test_path'], "requirements_path": config['configuration']['test_mode']['requirements_path'], "env_vars": config['configuration']['test_mode']['env_vars']}
                            for key, value in values.items():
                                if value is None:
                                    empty_fields.append(key)
                            if empty_fields:
                                print(f"Test Mode configuration failed as the following fields are empty:\n")
                                empty = ''
                                for field in empty_fields:
                                    empty += f"{field}\n"
                                print(empty)
                                return
                            framework_exists = db_controller.CheckExistence(db_connection, 'frameworks', config['configuration']['test_mode']['framework_name'], 'framework_name')
                            if framework_exists == False:
                                print(f"A Framework with the name '{config['configuration']['test_mode']['framework_name']}' does not exist. Please choose a another name")
                                return
                            #Compare config files
                            new_test_mode = TestMode(test_mode.getID(),config['configuration']['test_mode']['test_mode_name'], config['configuration']['test_mode']['host_ip_address'], config['configuration']['test_mode']['username'], config['configuration']['test_mode']['rsa_key_path'], config['configuration']['test_mode']['test_path'], config['configuration']['test_mode']['requirements_path'], config['configuration']['test_mode']['env_vars'], config['configuration']['test_mode'].get('test_runner_name', None))
                            changed_fields = {}
                            if new_test_mode.getTestModeName() != test_mode.getTestModeName():
                                data = db_controller.get_data(db_connection, 'frameworks', config['configuration']['test_mode']['framework_name'], 'framework_name')
                                framework_id = data[0][0]
                                test_mode_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_modes', config['configuration']['test_mode']['test_mode_name'], 'test_mode_name', framework_id)
                                if test_mode_exists:
                                    print(f"A Test Mode with the name '{config['configuration']['test_mode']['test_mode_name']}' already exists within the framework '{config['configuration']['test_mode']['framework_name']}. Please choose a another name")
                                    return
                                else:
                                    changed_fields['test_mode_name'] = new_test_mode.getTestModeName()
                            if new_test_mode.getHost() != test_mode.getHost():
                                changed_fields['host'] = new_test_mode.getHost()
                            if new_test_mode.getUsername() != test_mode.getUsername():
                                changed_fields['username'] = new_test_mode.getUsername()
                            if new_test_mode.getKeyPath() != test_mode.getKeyPath():
                                changed_fields['key_path'] = new_test_mode.getKeyPath()
                            if new_test_mode.getTestPath() != test_mode.getTestPath():
                                changed_fields['test_path'] = new_test_mode.getTestPath()
                            if new_test_mode.getRequirementsPath() != test_mode.getRequirementsPath():
                                changed_fields['requirements_path'] = new_test_mode.getRequirementsPath()
                            if new_test_mode.getEnvironmentVariablesPath() != test_mode.getEnvironmentVariablesPath():
                                changed_fields['env_vars_path'] = new_test_mode.getEnvironmentVariablesPath()
                            if new_test_mode.getTestRunner() != test_mode.getTestRunner():
                                if new_test_mode.getTestRunner() is None:
                                    changed_fields['test_runner_id'] = None
                                else:
                                    test_runner_id = None
                                    test_runner_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_runners', new_test_mode.getTestRunner(), 'name', framework.getID())
                                    if test_runner_exists:
                                        test_runner_data = db_controller.get_data_for_id(db_connection, 'test_runners', new_test_mode.getTestRunner(), 'name', framework.getID())
                                        test_runner_id = test_runner_data[0][0]
                                        changed_fields['test_runner_id'] = test_runner_id
                                    else:
                                        print(f"A Test Runner with the name '{new_test_mode.getTestRunner()}' does not exist within the framework '{framework.getName()}'. Please choose a another name")
                                        break
                            if not changed_fields:
                                print("There are no changes detected")
                            else:
                                for field, new_value in changed_fields.items():
                                    db_controller.update_data(db_connection, 'test_modes', test_mode.getID(), field, new_value)
                                db_controller.closeConnection(db_connection)
                                print("Test Mode updated!")
                        elif choice == 2:
                            db_controller = DatabaseHandler()
                            db_connection = db_controller.connection()
                            confirmation = input(f"Are you sure you want to delete test mode {test_mode.getID()}? (yes/no): ").lower()
                            if confirmation not in ['yes', 'y']:
                                print("Deletion cancelled")
                            else:
                                db_controller.delete_data(db_connection, 'test_modes', test_mode.getID(), 'test_mode_id')
                                print('Test mode Deleted')
                            db_controller.closeConnection(db_connection)
        elif choice == 4:
            if not framework.getReports():
                print("This framework has no recorded reports")
            else:
                while True:
                    report_names = ['back'] +[report.getDate() for report in framework.getReports()]
                    report_menu = SelectOptionMenu('Choose a report', start_index, report_names)
                    choice = report_menu.getUserInput()
                    if choice == 0:
                        break
                    else:
                        report = framework.getReports()[choice-1]
                        details = report.toString()
                        print(details)

        elif choice == 5:
            configuration_menu(framework)

def configuration_menu(framework):
    start_index = 0
    configuration_options = ['Back', 'View Configuration Settings', 'Update Configuration Settings']

    while True:
        action_menu = SelectOptionMenu('What would you like to do?', start_index, configuration_options)
        choice = action_menu.getUserInput()
        if choice == 0:
            break
        elif choice == 1:
            print("Print Configuration Settings")
        elif choice == 2:
            #IMPLEMENT LOGIC TO UPDATE TEST RUNNER HERE
            config_dir = str(input("Please provide the location of your framework configuration file: "))
            print(config_dir)

def DiscoverFramework(directory):
    unittest_pattern = re.compile(r'import unittest')
    test_suites = []
    test_runners = []
    for root, dirs, files in os.walk(directory):
        print(f"Looking in: {root}")
        for file in files:
            full_path = os.path.join(root, file)
            print(f"Checking file: {full_path}\n")
            if file.startswith('test') and file.endswith('.py'):
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        if unittest_pattern.search(content):
                            print(f"File contains 'import unittest':{file}\n")
                            suite_names = re.findall(r'class (\w+)\s*\(\s*unittest.TestCase\s*\):', content)
                            if suite_names:
                                print(f"Test Suites found in file {file}: {suite_names}\n")
                                for suite_name in suite_names:
                                    test_suites.append((file, suite_name))
                            else:
                                print(f"No test suites were found in {file}\n")
                        else:
                            print(f"File does not contain 'import unittest': {file}\n")
                except IOError as e:
                    print(f"Error opening file {file}: {e}\n")
            else:
                print("Not a test file\n")
            
            if file.endswith('test_runner.py'):
                print(f"Test Runner found: {full_path}\n")
                test_runners.append((file, full_path))
                continue
    return test_suites, test_runners

def CreateNewFramework():
    #Establish Database Connection
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    #Prompt for configuration file
    config_dir = str(input("Please provide the location of your framework configuration file: "))
    try:
        config = parseConfigXML(config_dir)
    except ET.ParseError as e:
        print(f"Error parsing the configuration file: {e}")
        return
    except FileNotFoundError:
        print(f"Configuration file not found at {config_dir}")
        return
    required_fields = ['name', 'target', 'description']
    missing_fields = [field for field in required_fields if field not in config['configuration']['framework']]
    if missing_fields:
        print(f"Framework configuration failed as the following fields are missing:\n")
        missing = ''
        for field in missing_fields:
            missing += f"{field}\n"
        print(missing)
        return
    empty_fields = []
    values = {"name": config['configuration']['framework']['name'], "target": config['configuration']['framework']['target'], "description": config['configuration']['framework']['description']}
    for key, value in values.items():
        if value is None: 
            empty_fields.append(key)
    if empty_fields:
        print(f"Framework configuration failed as the following fields are empty:\n")
        empty = ''
        for field in empty_fields:
            empty += f"{field}\n"
            print(empty)
        return
    framework_name = config['configuration']['framework']['name']
    framework_target = config['configuration']['framework']['target']
    framework_description = config['configuration']['framework']['description']
    test_report_directory = config['configuration']['framework'].get('test_report_directory', None)
    test_report_email = config['configuration']['framework'].get('test_report_email', None)
    #Check framework existence
    exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
    if exists:
        print(f"A Framework with the name '{framework_name}' already exists. Please choose a another name")
        return
    #Upload framework details to the database
    data_values = [framework_name, framework_target, framework_description, test_report_directory, test_report_email]
    field_names = ['framework_name', 'framework_target', 'framework_description', 'test_report_directory', 'test_report_email']
    table_name = 'frameworks'
    db_controller.insert_data(db_connection, table_name, field_names, data_values)

    #Discover framework
    test_suites, test_runners = DiscoverFramework(framework_target)
    #Check for test suites
    if test_suites:
        for filename, suite in test_suites:
            data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
            framework_id = data[0][0]
            location = framework_target + '/' + filename
            data_values = [filename, 'N/A', location, framework_id]
            field_names = ['test_suite_name', 'test_suite_description', 'test_script_location', 'framework_id']
            table_name = 'test_suites'
            db_controller.insert_data(db_connection, table_name, field_names, data_values) 
            print(f"Uploaded test suite {suite}")
    else:
        print(f"No test suites discovered within {framework_name}")

    if test_runners:
        for filename, test_runner in test_runners:
            data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
            framework_id = data[0][0]
            location = framework_target + '/' + filename
            data_values = [filename, location, framework_id]
            field_names = ['name', 'location', 'framework_id']
            table_name = 'test_runners'
            db_controller.insert_data(db_connection, table_name, field_names, data_values) 
            print(f"Uploaded test runner {test_runner}")
    else:
        print(f"No test runners discovered within {framework_name}")
    
    if config['configuration'] == 'standard':
        print("Standard Config")
        #Here the standard config json file will be used to upload standard settings to database
    else:
        print("Advanced Config")
        #Here the config file will grab all setting's to upload to the database
    print("Framework Created!")
    db_controller.closeConnection(db_connection)

def AddTestSuite():
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    config_dir = str(input("Please provide the location of your test suite configuration file: "))
    try:
        config = parseConfigXML(config_dir)
    except ET.ParseError as e:
        print(f"Error parsing the configuration file: {e}")
        return
    except FileNotFoundError:
        print(f"Configuration file not found at {config_dir}")
        return
    required_fields = ['framework_name', 'test_suite_name', 'test_suite_description', 'test_suite_location']
    missing_fields = [field for field in required_fields if field not in config['configuration']['test_suite']]
    if missing_fields:
        print(f"Test Suite configuration failed as the following fields are missing:\n")
        missing = ''
        for field in missing_fields:
            missing += f"{field}\n"
        print(missing)
        return
    empty_fields = []
    values = {"framework_name": config['configuration']['test_suite']['framework_name'], "test_suite_name": config['configuration']['test_suite']['test_suite_name'], "test_suite_description": config['configuration']['test_suite']['test_suite_description'], "test_suite_location": config['configuration']['test_suite']['test_suite_location']}
    for key, value in values.items():
        if value is None: 
            empty_fields.append(key)
    if empty_fields:
        print(f"Test Suite configuration failed as the following fields are empty:\n")
        empty = ''
        for field in empty_fields:
            empty += f"{field}\n"
            print(empty)
        return
    framework_name = config['configuration']['test_suite']['framework_name']
    test_suite_name = config['configuration']['test_suite']['test_suite_name']
    test_suite_description = config['configuration']['test_suite']['test_suite_description']
    test_suite_location = config['configuration']['test_suite']['test_suite_location']
    coverage_files = config['configuration']['test_suite'].get('coverage_files', None)
    if coverage_files:
        if isinstance(coverage_files, dict):
            files = coverage_files.get('file', [])
            if isinstance(files, str):
                coverage_files_list = [files]
            else:
                coverage_files_list = files
        else:
            print("Unexpected format for coverage files")
            return
    else:
        coverage_files_list = []
    
    coverage_files_str = json.dumps(coverage_files_list)
    framework_exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
    if framework_exists == False:
        print(f"A Framework with the name '{framework_name}' does not exist. Please choose a another name")
        return
    
    data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
    framework_id = data[0][0]
    test_suite_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_suites', test_suite_name, 'test_suite_name', framework_id)
    if test_suite_exists:
        print(f"A Test Suite with the name '{test_suite_name}' already exists within the framework '{framework_name}. Please choose a another name")
        return
    data_values = [test_suite_name, test_suite_description, test_suite_location, framework_id, coverage_files_str]
    field_names = ['test_suite_name', 'test_suite_description', 'test_script_location', 'framework_id', 'coverage_files']
    table_name = 'test_suites'
    db_controller.insert_data(db_connection, table_name, field_names, data_values)
    print("Test Suite Created!")
    db_controller.closeConnection(db_connection)

def AddTestRunner():
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    config_dir = str(input("Please provide the location of your test runner configuration file: "))
    try:
        config = parseConfigXML(config_dir)
    except ET.ParseError as e:
        print(f"Error parsing the configuration file: {e}")
        return
    except FileNotFoundError:
        print(f"Configuration file not found at {config_dir}")
        return
    required_fields = ['framework_name', 'test_runner_name', 'test_runner_location']
    missing_fields = [field for field in required_fields if field not in config['configuration']['test_runner']]
    if missing_fields:
        print(f"Test Runner configuration failed as the following fields are missing:\n")
        missing = ''
        for field in missing_fields:
            missing += f"{field}\n"
        print(missing)
        return
    empty_fields = []
    values = {"framework_name": config['configuration']['test_runner']['framework_name'], "test_runner_name": config['configuration']['test_runner']['test_runner_name'], "test_runner_location": config['configuration']['test_runner']['test_runner_location']}
    for key, value in values.items():
        if value is None: 
            empty_fields.append(key)
    if empty_fields:
        print(f"Test Runner configuration failed as the following fields are empty:\n")
        empty = ''
        for field in empty_fields:
            empty += f"{field}\n"
            print(empty)
        return
    framework_name = config['configuration']['test_runner']['framework_name']
    test_runner_name = config['configuration']['test_runner']['test_runner_name']
    test_runner_location = config['configuration']['test_runner']['test_runner_location']

    framework_exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
    if framework_exists == False:
        print(f"A Framework with the name '{framework_name}' does not exist. Please choose a another name")
        return
    
    data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
    framework_id = data[0][0]
    test_runner_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_runners', test_runner_name, 'name', framework_id)
    if test_runner_exists:
        print(f"A Test Runner with the name '{test_runner_name}' already exists within the framework '{framework_name}. Please choose a another name")
        return
    data_values = [test_runner_name, test_runner_location, framework_id]
    field_names = ['name', 'location', 'framework_id']
    table_name = 'test_runners'
    db_controller.insert_data(db_connection, table_name, field_names, data_values)
    print("Test Runner Created!")
    db_controller.closeConnection(db_connection)

def AddTestMode():
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    config_dir = str(input("Please provide the location of your test mode configuration file: "))
    #Attempt to Parse config file
    try:
        config = parseConfigXML(config_dir)
    except ET.ParseError as e:
        print(f"Error parsing the configuration file: {e}")
        return
    except FileNotFoundError:
        print(f"Configuration file not found at {config_dir}")
        return
    #Check for missing required fields
    required_fields = ['framework_name', 'test_mode_name', 'host_ip_address', 'username', 'rsa_key_path', 'test_path']
    missing_fields = [field for field in required_fields if field not in config['configuration']['test_mode']]
    if missing_fields:
        print(f"Test Mode configuration failed as the following fields are missing:\n")
        missing = ''
        for field in missing_fields:
            missing += f"{field}\n"
        print(missing)
        return
    #Check for any empty missing fields
    empty_fields = []
    values = {"test_mode_name": config['configuration']['test_mode']['test_mode_name'], "host_ip_address": config['configuration']['test_mode']['host_ip_address'], "username": config['configuration']['test_mode']['username'], "rsa_key_path": config['configuration']['test_mode']['rsa_key_path'], "test_path": config['configuration']['test_mode']['test_path']}
    for key, value in values.items():
        if value is None: 
            empty_fields.append(key)
    if empty_fields:
        print(f"Test Mode configuration failed as the following fields are empty:\n")
        empty = ''
        for field in empty_fields:
            empty += f"{field}\n"
            print(empty)
        return
    framework_name = config['configuration']['test_mode']['framework_name']
    test_mode_name = config['configuration']['test_mode']['test_mode_name']
    host_ip_address = config['configuration']['test_mode']['host_ip_address']
    username = config['configuration']['test_mode']['username']
    rsa_key_path = config['configuration']['test_mode']['rsa_key_path']
    test_path = config['configuration']['test_mode']['test_path']
    requirements_path = config['configuration']['test_mode']['requirements_path']
    env_vars = config['configuration']['test_mode']['env_vars']
    test_runner_name = config['configuration']['test_mode'].get('test_runner_name', None)
    init_file_path = config['configuration']['test_mode'].get('init_file_path', None)

    exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
    if exists == False:
        print(f"A Framework with the name '{framework_name}' does not exist. Please choose a another name")
        return
    data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
    framework_id = data[0][0]
    test_mode_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_modes', test_mode_name, 'test_mode_name', framework_id)
    if test_mode_exists:
        print(f"A Test Mode with the name '{test_mode_name}' already exists within the framework '{framework_name}. Please choose a another name")
        return
    
    test_runner_id = None
    if test_runner_name:
        test_runner_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_runners', test_runner_name, 'name', framework_id)
        if test_runner_exists:
            test_runner_data = db_controller.get_data_for_id(db_connection, 'test_runners', test_runner_name, 'name', framework_id)
            test_runner_id = test_runner_data[0][0]
        else:
            print(f"A Test Runner with the name '{test_runner_name}' does not exist within the framework '{framework_name}. Please choose a another name")
            return

    data_values = [test_mode_name, host_ip_address, username, rsa_key_path, test_path, requirements_path, env_vars, framework_id, test_runner_id, init_file_path]
    field_names = ['test_mode_name', 'host', 'username', 'key_path', 'test_path', 'requirements_path', 'env_vars_path', 'framework_id', 'test_runner_id', 'init_file_path']
    table_name = 'test_modes'
    db_controller.insert_data(db_connection, table_name, field_names, data_values)
    print("Test Mode Created!")
    db_controller.closeConnection(db_connection)

def RunSuite(framework_name, test_suites, test_mode_name):
    loadframeworks()
    framework = None
    for proj in frameworks:
        if proj.getName() == framework_name:
           framework = proj
           break
        else:
            framework = None
    if framework is None:
        print(f"{framework_name} does not exists, please enter a valid framework name")
        print("Exiting....")
        return
    print("Creating Test Execution Engine....")
    engine = TestExecutionEngine()
    test_mode = framework.getTestMode(test_mode_name)
    if test_mode is None:
        print("Please choose a valid test mode for this framework")
        print("Exiting....")
        return
    else:
        print(test_mode.getDetails())
        engine.setTestMode(test_mode)

    if 'ALL' in [suite.upper() for suite in test_suites]:
        if framework.getTestSuites() is not None:
            for test_suite in framework.getTestSuites():
                engine.addTestSuite(test_suite)
        else:
            print("There are no available test suites for this framework")
            print("Exiting....")
            return
    else:
        for test_suite in test_suites:
            suite = framework.getTestSuite(test_suite)
            if suite is None:
                print("Please choose a valid test suite for this framework")
                print("Exiting....")
                return
            else:
                print(suite.getDetails())
                engine.addTestSuite(suite)
    engine.RunEngine(framework)

def loadframeworks():
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    print("Loading your UniTest frameworks....")
    #Load framework instances
    framework_data = db_controller.get_all(db_connection, 'frameworks')
    for data in framework_data:
        framework_id = data[0]
        name = data[1]
        target = data[2]
        description = data[3]
        reports = []
        test_report_directory = data[5]
        test_report_email = data[6]
        report_data = db_controller.get_data(db_connection, 'reports',framework_id, 'framework_id')
        for data in report_data:
            test_summary = None
            environment_details = None
            execution_details = None
            test_suite_results = None
            id = data[0]
            date = data[1]
            framework_id = data[2]
            
            #Load test summary data for report
            test_summary_data = db_controller.get_data(db_connection, 'test_summary', id, 'report_id')
            for data in test_summary_data:
                number_of_test_suites = data[2]
                number_of_test_cases = data[3]
                passes = data[4]
                failures = data[5]
                errors = data[6]
                success_rate = data[7]
                test_summary = TestSummary(number_of_test_suites, number_of_test_cases, passes, failures, errors, success_rate)
            
            #Load test environment data for report
            environment_data = db_controller.get_data(db_connection, 'environment_details', id, 'report_id')
            for data in environment_data:
                os_type = data[2]
                os_version = data[3]
                ip_address = data[4]
                test_directory = data[5]
                python_version = data[6]
                environment_details = EnvironmentDetails(os_type, os_version, ip_address, test_directory, python_version)

            #Load test execution data for report
            execution_data = db_controller.get_data(db_connection, 'execution_details', id, 'report_id')
            for data in execution_data:
                test_suites_executed_json = data[2]
                start_time = data[3]
                end_time = data[4]
                total_time = data[5]
                test_suites_executed = json.loads(test_suites_executed_json)
                execution_details = ExecutionDetails(test_suites_executed, start_time, end_time, total_time)

            #Load test suite results data for report
            test_suite_results_data = db_controller.get_data(db_connection, 'test_suite_results', id, 'report_id')
            test_suite_results = []
            for data in test_suite_results_data:
                test_suite_results_id = data[0]
                test_suite_name = data[1]
                date = data[2]
                passed = data[3]
                failed = data[4]
                error = data[5]
                execution_time = data[6]
                test_results_data = db_controller.get_data(db_connection, 'test_results', test_suite_results_id, 'test_suite_results_id')
                test_results = []
                for data in test_results_data:
                    test_name = data[1]
                    status = data[2]
                    error_messages = data[3]
                    test_result_execution_time = data[4]
                    test_result = TestResult(test_name, status, error_messages, test_result_execution_time)
                    test_results.append(test_result)
                coverage_data = db_controller.get_data(db_connection, 'coverage_results', test_suite_results_id, 'test_suite_results_id')
                coverage_results = []
                if coverage_data is None:
                    coverage_results = []
                else: 
                    for data in coverage_data:
                        function_coverage = data[1]
                        line_coverage = data[2]
                        branch_coverage = data[3]
                        covered_functions = data[4]
                        uncovered_functions = data[5]
                        coverage_result = CoverageResult( function_coverage, line_coverage, branch_coverage, covered_functions, uncovered_functions)
                        coverage_results.append(coverage_result)
                test_suite_result = TestSuiteResult( test_suite_name, date, passed, failed, error, execution_time, test_results, coverage_results)
                test_suite_results.append(test_suite_result)
            report = Report( date, test_summary, environment_details, execution_details, test_suite_results, framework_id)
            reports.append(report)
        framework = Framework(framework_id, name, target, description, test_report_directory, test_report_email, reports)
        frameworks.append(framework)
    
     #Load Test Suite instances for given framework
    for framework in frameworks:
        id = framework.getID()
        test_suite_data = db_controller.get_data(db_connection, 'test_suites', id, 'framework_id')
        for data in test_suite_data:
            test_suite_id = data[0]
            test_suite_name = data[1]
            test_suite_description = data[2]
            test_script_dir = data[3]
            test_suite_coverage_files = data[6]
            test_suite = TestSuite(test_suite_id, test_suite_name, test_suite_description, test_script_dir)
            if test_suite_coverage_files is not None:
                test_suite_coverage_files_json = json.loads(test_suite_coverage_files)
                for file in test_suite_coverage_files_json:
                    test_suite.addCoverageFiles(file)
            test_suite_results = []
            reports = framework.getReports()
            for report in reports:
                test_suite_results = report.getTestSuiteResults()
                for test_suite_result in test_suite_results:
                    if test_suite_result.getTestSuiteName() == test_suite_name:
                        test_suite.addResult(test_suite_result)
            framework.addTestSuite(test_suite)

    #Load Test Mode instances for given framework
    for framework in frameworks:
        id = framework.getID()
        test_runner_data = db_controller.get_data(db_connection, 'test_runners', id, 'framework_id')
        for data in test_runner_data:
            test_runner_id = data[0]
            test_runner_name = data[1]
            test_runner_location = data[2]
            test_runner = TestRunner(test_runner_id, test_runner_name, test_runner_location)
            framework.addTestRunner(test_runner)

    #Load Test Mode instances for given framework
    for framework in frameworks:
        id = framework.getID()
        test_mode_data = db_controller.get_data(db_connection, 'test_modes', id, 'framework_id')
        for data in test_mode_data:
            test_mode_id = data[0]
            test_mode_name = data[1]
            host = data[2]
            username = data[3]
            key_path = data[4]
            test_path = data[5]
            requirements_path = data[6]
            env_vars_path = data[7]
            test_runner_id = data[10]
            test_runner = None
            test_runners = framework.getTestRunners()
            for runner in test_runners:
                if runner.getID() == test_runner_id:
                    test_runner = runner
            init_file_path = data[11]
            test_mode = TestMode(test_mode_id, test_mode_name, host, username, key_path, test_path, requirements_path, env_vars_path, test_runner)
            if init_file_path:
                test_mode.addInitialisationFile(init_file_path)
            framework.addTestMode(test_mode)
    db_controller.closeConnection(db_connection)

def parseXMLtoDict(element):
    if not list(element):
        return element.text
    
    child_dict = {}
    for child in element:
        child_value = parseXMLtoDict(child)

        if child.tag in child_dict:
            #if type(child_dict[child.tag]) is list:
            if isinstance(child_dict[child.tag], list):
                child_dict[child.tag].append(child_value)
            else:
                child_dict[child.tag] = [child_dict[child.tag], child_value]
        else:
            child_dict[child.tag] = child_value
    return child_dict

def parseConfigXML(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return {root.tag: parseXMLtoDict(root)}

if __name__ == "__main__":
    main()

