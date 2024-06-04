from FrameworkObjects.Framework import Framework
from Execution.TestExecutionEngine import TestExecutionEngine
from FrameworkObjects.TestSuite import TestSuite
from FrameworkObjects.TestMode import TestMode
from FrameworkObjects.TestRunner import TestRunner
from Execution.DatabaseHandler import DatabaseHandler
from flask_socketio import SocketIO, emit
import re
import os
import xml.etree.ElementTree as ET
import json
from flask import Flask
from flask import request
from flask_cors import CORS
from flask import jsonify

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

#REQUEST
#1. Create a framework
#2. View framework
#3. Add Test Suite
#4. Reload Test Suite
#5. View Test Suites
#6. Run Suite

#COLLECTION OF DATA
#Rather than constantly having a back and forth connection between the backend and database there will be a function for loading data 

#proj1 = framework("Test 1", "Test Dir 1", "Test Description 1")
#proj2 = framework("Test 2", "Test Dir 2", "Test Description 2")
#frameworks.append(proj1)
#frameworks.append(proj2)

#def DefineJob(self, framework_job):
    #schedular.add_job(RunSuiteWithParams(framework_job.getFrameworkName(), framework_job.getTestModeName(), framework_job.getTestSuites()), 'cron', hour=17)

def DiscoverFramework(directory):
    unittest_pattern = re.compile(r'import unittest')
    test_suites = []
    test_runners=[]
    for root, dirs, files in os.walk(directory):
        print(f"Looking in: {root}")
        for file in files:
            full_path = os.path.join(root, file)
            print(f"Checking file: {full_path}")
            if file.startswith('test') and file.endswith('.py'):
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        if unittest_pattern.search(content):
                            print("File contains 'import unittest':", file)
                            suite_names = re.findall(r'class (\w+)\s*\(\s*unittest.TestCase\s*\):', content)
                            if suite_names:
                                print(f"Test Suites found in file {file}: {suite_names}")
                                for suite_name in suite_names:
                                    test_suites.append((file, suite_name))
                            else:
                                print(f"No test suites were found in {file}")
                        else:
                            print(f"File does not contain 'import unittest': {file}")
                except IOError as e:
                    print(f"Error opening file {file}: {e}")
            else:
                print("Not a test file")
            
            if file.endswith('test_runner.py'):
                print(f"Test Runner found: {full_path}\n")
                test_runners.append((file, full_path))
                continue
    return test_suites, test_runners

@app.route('/framework/create', methods=['POST'])
def CreateNewFramework():
    data = request.files
    if 'configFile' not in data:
        return jsonify({"error": "No file found"}), 400
    
    file = data['configFile']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        #Establish Database Connection
        db_controller = DatabaseHandler()
        db_connection = db_controller.connection()
        #Prompt for configuration file
        try:
            config = parseConfigXML(file)
            required_fields = ['name', 'target']
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
            framework_description = config['configuration']['framework'].get('description', None)
            test_report_directory = config['configuration']['framework'].get('test_report_directory', None)
            test_report_email = config['configuration']['framework'].get('test_report_email', None)
            #Check framework existence
            exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
            if exists:
                print("Framework already exsists")
                return jsonify({f"error":"A Framework with the name '{framework_name}' already exists. Please choose a another name"}), 400
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
            
            print("Framework Created!")
            #print(new_framework.getDetails())
            db_controller.closeConnection(db_connection)
            return jsonify({"success": True, "message": "Framework created successfully"})
        except:
            print("Error Parsing XML file")
            return jsonify({"error": "error parsing the json request"})
    else:
        return jsonify({"error": "File Upload Failed"}), 400
    
@app.route('/framework/create_from_form', methods=['POST'])
def CreateNewFrameworkFromForm():
    data = request.get_json()
    framework_name = data.get('name')
    target_directory = data.get('target_directory')
    description = data.get('description')
    test_report_directory = data.get('test_report_directory')
    test_report_email = data.get('test_report_email')
    #Establish Database Connection
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    #Prompt for configuration file
    try:
        #Check framework existence
        exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
        if exists:
            print("Framework already exsists")
            return jsonify({f"error":"A Framework with the name '{framework_name}' already exists. Please choose a another name"}), 400
        #Upload framework details to the database
        data_values = [framework_name, target_directory, description, test_report_directory, test_report_email]
        field_names = ['framework_name', 'framework_target', 'framework_description', 'test_report_directory', 'test_report_email']
        table_name = 'frameworks'
        db_controller.insert_data(db_connection, table_name, field_names, data_values)
        #Discover framework
        test_suites, test_runners = DiscoverFramework(target_directory)
        #Check for test suites
        if test_suites:
            for filename, suite in test_suites:
                data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
                framework_id = data[0][0]
                location = target_directory + '/' + filename
                data_values = [filename, 'N/A', location, framework_id]
                field_names = ['test_suite_name', 'test_suite_description', 'test_script_location', 'framework_id']
                table_name = 'test_suites'
                db_controller.insert_data(db_connection, table_name, field_names, data_values) 
                print(f"Uploaded test suite {suite}")
        else:
            print(f"No test suites discovered within {framework_name}")

        if test_runners:
            print(f"TEST RUNNERS: {test_runners}")
            for filename, test_runner in test_runners:
                data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
                framework_id = data[0][0]
                location = target_directory + '/' + filename
                data_values = [filename, location, framework_id]
                field_names = ['name', 'location', 'framework_id']
                table_name = 'test_runners'
                db_controller.insert_data(db_connection, table_name, field_names, data_values) 
                print(f"Uploaded test runner {test_runner}")
        else:
            print(f"No test runners discovered within {framework_name}")

        print("Framework Created!")
        db_controller.closeConnection(db_connection)
        return jsonify({"success": True, "message": "Framework created successfully"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": {e}})
    
@app.route('/framework/update', methods=['POST'])
def UpdateFramework():
    #Establish database connection
    framework_id = request.form.get('framework_id')
    if framework_id is None:
        data = request.get_json()
        framework_id = data.get('framework_id')
    data = request.files
    if 'configFile' in request.files:
        file = request.files['configFile']
        try:
            config = parseConfigXML(file)
        except ET.ParseError as e:
            return jsonify({"error parsing the config file: {e}"}), 400
        framework_name = config['configuration']['framework']['name']
        framework_description = config['configuration']['framework'].get('description', None)
        framework_test_report_directory = config['configuration']['framework'].get('test_report_directory', None)
        framework_test_report_email = config['configuration']['framework'].get('test_report_email', None)
    else:
        framework_name = request.json.get('name', None) or request.form.get('name', None)
        framework_description = request.json.get('description', None) or request.form.get('description', None)
        framework_test_report_directory = request.json.get('test_report_directory', None) or request.form.get('test_report_directory', None)
        framework_test_report_email = request.json.get('test_report_email', None) or request.form.get('test_report_email', None)
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    framework_data = db_controller.get_data(db_connection, 'frameworks', framework_id, 'framework_id')
    if not framework_data:
        return jsonify({"error": "Framework not found for", "framework_id": framework_id}), 404
    for data in framework_data:
        id = data[0]
        name = data[1]
        target = data[2]
        description = data[3]
        test_report_directory = data[5]
        test_report_email = data[6]
    
    changed_fields = {}
    if name != framework_name:
        changed_fields['framework_name'] = framework_name
    if description != framework_description:
        changed_fields['framework_description'] = framework_description
    if test_report_directory != framework_test_report_directory:
        changed_fields['test_report_directory'] = framework_test_report_directory
    if test_report_email != framework_test_report_email:
        changed_fields['test_report_email'] = framework_test_report_email
    
    if not changed_fields:
        return jsonify({"message": "There were no changes detected"}), 200
    
    for field, new_value in changed_fields.items():
        db_controller.update_data(db_connection, 'frameworks', id, field, new_value)
    db_controller.closeConnection(db_connection)
    return jsonify({"success": "Framework updated successfully"}), 200

@app.route('/framework/add_test_suite', methods=['POST'])
def AddTestSuite():
    data = request.files
    if 'configFile' not in data:
        return jsonify({"error": "No file found"}), 400
    
    file = data['configFile']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        db_controller = DatabaseHandler()
        db_connection = db_controller.connection()
        config = parseConfigXML(file)
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
            return jsonify({"error": f"A Framework with the name '{framework_name}' does not exist. Please choose a another name"}), 400
        
        data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
        framework_id = data[0][0]
        test_suite_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_suites', test_suite_name, 'test_suite_name', framework_id)
        if test_suite_exists:
            print(f"A Test Suite with the name '{test_suite_name}' already exists within the framework '{framework_name}. Please choose a another name")
            return jsonify({"error": f"A Test Suite with the name '{test_suite_name}' already exists within the framework '{framework_name}. Please choose a another name"}), 400
        data_values = [test_suite_name, test_suite_description, test_suite_location, framework_id]
        field_names = ['test_suite_name', 'test_suite_definition', 'test_script_location', 'framework_id']
        table_name = 'test_suites'
        db_controller.insert_data(db_connection, table_name, field_names, data_values)
        print("Test Suite Created!")
        db_controller.closeConnection(db_connection)
        return jsonify({"success": True, "message": "Test Suite created successfully"})
    else:
        return jsonify({"error": "File Upload Failed"}), 400

@app.route('/framework/add_test_mode', methods=['POST'])
def AddTestMode():
    #Establish database connection
    data = request.files
    if 'configFile' in request.files:
        file = request.files['configFile']
        try:
            config = parseConfigXML(file)
        except ET.ParseError as e:
            return jsonify({"error parsing the config file: {e}"}), 400
        framework_name = config['configuration']['test_mode']['framework_name']
        test_mode_name = config['configuration']['test_mode']['test_mode_name']
        host_ip_address = config['configuration']['test_mode']['host_ip_address']
        test_mode_username = config['configuration']['test_mode']['username']
        rsa_key_path = config['configuration']['test_mode']['rsa_key_path']
        test_mode_test_path = config['configuration']['test_mode']['test_path']
        test_mode_requirements_path = config['configuration']['test_mode']['requirements_path']
        test_mode_env_vars = config['configuration']['test_mode']['env_vars']
        test_mode_test_runner_name = config['configuration']['test_mode'].get('test_runner_name', None)
        test_mode_init_file_path = config['configuration']['test_mode'].get('init_file_path', None)
    else:
        framework_name = request.json.get('framework_name', None) or request.form.get('framework_name', None)
        test_mode_name = request.json.get('name', None) or request.form.get('name', None)
        host_ip_address = request.json.get('host_ip_address', None) or request.form.get('host_ip_address', None)
        test_mode_username = request.json.get('username', None) or request.form.get('username', None)
        rsa_key_path = request.json.get('rsa_key_path', None) or request.form.get('rsa_key_path', None)
        test_mode_test_path = request.json.get('test_path', None) or request.form.get('test_path', None)
        test_mode_requirements_path = request.json.get('python_dependencies_file_path', None) or request.form.get('python_dependencies_file_path', None)
        test_mode_env_vars = request.json.get('environment_variables', None) or request.form.get('environment_variables', None)
        test_mode_test_runner_name = request.json.get('test_runner', None) or request.form.get('test_runner', None)
        test_mode_init_file_path = request.json.get('init_file_path', None) or request.form.get('init_file_path', None)
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    exists = db_controller.CheckExistence(db_connection, 'frameworks', framework_name, 'framework_name')
    if exists == False:
        print(f"A Framework with the name '{framework_name}' does not exist. Please choose a another name")
        return jsonify({"error": f"A Framework with the name '{framework_name}' does not exist. Please choose a another name"}), 400
    data = db_controller.get_data(db_connection, 'frameworks', framework_name, 'framework_name')
    framework_id = data[0][0]
    test_mode_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_modes', test_mode_name, 'test_mode_name', framework_id)
    if test_mode_exists:
        print(f"A Test Mode with the name '{test_mode_name}' already exists within the framework '{framework_name}. Please choose a another name")
        return jsonify({"error": f"A Test Mode with the name '{test_mode_name}' already exists within the framework '{framework_name}. Please choose a another name"}), 400
    test_runner_id = None
    if test_mode_test_runner_name:
        test_runner_exists = db_controller.CheckExistenceAdvanced(db_connection, 'test_runners', test_mode_test_runner_name, 'name', framework_id)
        if test_runner_exists:
            test_runner_data = db_controller.get_data_for_id(db_connection, 'test_runners', test_mode_test_runner_name, 'name', framework_id)
            test_runner_id = test_runner_data[0][0]
        else:
            print(f"A Test Runner with the name '{test_mode_test_runner_name}' does not exist within the framework '{framework_name}. Please choose a another name")
            return
    data_values = [test_mode_name, host_ip_address, test_mode_username, rsa_key_path, test_mode_test_path, test_mode_requirements_path, test_mode_env_vars, framework_id, test_runner_id, test_mode_init_file_path]
    field_names = ['test_mode_name', 'host', 'username', 'key_path', 'test_path', 'requirements_path', 'env_vars_path', 'framework_id', 'test_runner_id', 'init_file_path']
    table_name = 'test_modes'
    db_controller.insert_data(db_connection, table_name, field_names, data_values)
    print("Test Mode Created!")
    db_controller.closeConnection(db_connection)
    return jsonify({"success": True, "message": "Test Mode created successfully"})

    
@app.route('/framework/update_test_mode', methods=['POST'])
def UpdateTestMode():
    #Establish database connection
    test_mode_id = request.form.get('test_mode_id')
    if test_mode_id is None:
        data = request.get_json()
        test_mode_id = data.get('test_mode_id')
    data = request.files
    if 'configFile' in request.files:
        file = request.files['configFile']
        try:
            config = parseConfigXML(file)
        except ET.ParseError as e:
            return jsonify({"error parsing the config file: {e}"}), 400
        test_mode_name = config['configuration']['test_mode']['test_mode_name']
        host_ip_address = config['configuration']['test_mode']['host_ip_address']
        test_mode_username = config['configuration']['test_mode']['username']
        rsa_key_path = config['configuration']['test_mode']['rsa_key_path']
        test_mode_test_path = config['configuration']['test_mode']['test_path']
        test_mode_requirements_path = config['configuration']['test_mode']['requirements_path']
        test_mode_env_vars = config['configuration']['test_mode']['env_vars']
        test_mode_test_runner_name = config['configuration']['test_mode'].get('test_runner_name', None)
        test_mode_init_file_path = config['configuration']['test_mode'].get('init_file_path', None)
    else:
        test_mode_name = request.json.get('name', None) or request.form.get('name', None)
        host_ip_address = request.json.get('host_ip_address', None) or request.form.get('host_ip_address', None)
        test_mode_username = request.json.get('username', None) or request.form.get('username', None)
        rsa_key_path = request.json.get('rsa_key_path', None) or request.form.get('rsa_key_path', None)
        test_mode_test_path = request.json.get('test_path', None) or request.form.get('test_path', None)
        test_mode_requirements_path = request.json.get('python_dependencies_file_path', None) or request.form.get('python_dependencies_file_path', None)
        test_mode_env_vars = request.json.get('environment_variables', None) or request.form.get('environment_variables', None)
        test_mode_test_runner_name = request.json.get('test_runner', None) or request.form.get('test_runner', None)
        test_mode_init_file_path = request.json.get('init_file_path', None) or request.form.get('init_file_path', None)
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    test_mode_data = db_controller.get_data(db_connection, 'test_modes', test_mode_id, 'test_mode_id')
    if not test_mode_data:
        return jsonify({"error": "Test Mode not found for", "test_mode_id": framework_id}), 404
    for data in test_mode_data:
        id = data[0]
        name = data[1]
        host = data[2]
        username = data[3]
        key_path = data[4]
        test_path = data[5]
        requirements_path = data[6]
        env_vars_path = data[7]
        framework_id = data[8]
        test_runner_id = data[10]
        init_file_path = [11]
    
    changed_fields = {}
    if test_mode_name != name:
        changed_fields['test_mode_name'] = test_mode_name
    if host_ip_address != host:
        changed_fields['host'] = host_ip_address
    if  test_mode_username != username:
        changed_fields['username'] = test_mode_username
    if rsa_key_path != key_path:
        changed_fields['key_path'] = rsa_key_path
    if test_mode_test_path != test_path:
        changed_fields['test_path'] = test_mode_test_path
    if test_mode_requirements_path != requirements_path:
        changed_fields['requirements_path'] = test_mode_requirements_path
    if test_mode_env_vars != env_vars_path:
        changed_fields['env_vars_path'] = test_mode_env_vars
    test_runner_data = db_controller.get_data(db_connection, 'test_runners', test_runner_id, 'id')
    if test_runner_data:
        for data in test_runner_data:
            test_runner_name = data[1]
            if test_mode_test_runner_name != test_runner_name:
               new_test_runner_data = db_controller.get_data_for_id(db_connection, 'test_runners', test_mode_test_runner_name, 'name', framework_id)
               new_test_runner_id = new_test_runner_data[0]
               changed_fields['test_runner_id'] = new_test_runner_id
    if test_mode_init_file_path != init_file_path:
        changed_fields['init_file_path'] = test_mode_init_file_path
    
    if not changed_fields:
        return jsonify({"message": "There were no changes detected"}), 200
    

    for field, new_value in changed_fields.items():
        print(f"Field: {field}, VALUE: {new_value}")
        db_controller.update_data(db_connection, 'test_modes', id, field, new_value)
    db_controller.closeConnection(db_connection)
    return jsonify({"success": "Test Mode updated successfully"}), 200

@app.route('/framework/run', methods=['POST'])
def RunSuite():
    frameworks = loadframeworks()
    data = request.get_json()
    framework_name = data.get('framework_name')
    test_suites = data.get('test_suites')
    print(f"TEST SUITES: {test_suites}")
    if isinstance(test_suites, str):
        test_suites = test_suites.split(',')
    print(test_suites)
    test_mode = data.get('test_mode_name')
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
    framework_id = framework.getID()
    print("Creating Test Execution Engine....")
    engine = TestExecutionEngine()
    test_mode = framework.getTestMode(test_mode)
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
            if not suite:
                print("Please choose a valid test suite for this framework")
                print("Exiting....")
                return
            else:
                print(suite.getDetails())
                engine.addTestSuite(suite)
    engine.RunEngine(framework, output_callback=output)
    return jsonify({"success": True, "message": "Test Suite Execution Started"})

def output(line):
    socketio.emit('test_output', {'data': line})

@app.route('/framework/load_framework_names', methods=['GET'])
def loadframeworknames():
    frameworks = []
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    print("Loading your UniTest frameworks....")
    #Load framework instances
    framework_data = db_controller.get_all(db_connection, 'frameworks')
    for data in framework_data:
        id = data[0]
        name = data[1]
        framework_dict = {'framework_id': id, 'name': name}
        frameworks.append(framework_dict)

    db_controller.closeConnection(db_connection)
    response = {'status': 'success', 'frameworks': frameworks}
    return jsonify(response)

@app.route('/framework/load_framework', methods=['GET'])
def loadframework():
    framework_id = request.args.get('framework_id')
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    print("Loading your UniTest frameworks....")
    #Load framework instances
    framework_data = db_controller.get_data(db_connection, 'frameworks', framework_id, 'framework_id')
    for data in framework_data:
        id = data[0]
        name = data[1]
        target = data[2]
        description = data[3]
        test_report_directory = data[5]
        test_report_email = data[6]
    
     #Load Test Suite instances for given framework
    test_suites = []
    test_suite_data = db_controller.get_data(db_connection, 'test_suites', id, 'framework_id')
    for data in test_suite_data:
        test_suite_id = data[0]
        test_suite_name = data[1]
        test_suite = {'test_suite_id': test_suite_id, 'test_suite_name': test_suite_name}
        test_suites.append(test_suite)
    
    #Load Test Mode instances for given framework
    test_modes = []
    test_mode_data = db_controller.get_data(db_connection, 'test_modes', id, 'framework_id')
    for data in test_mode_data:
        test_mode_id = data[0]
        test_mode_name = data[1]
        test_mode = {'test_mode_id': test_mode_id, 'test_mode_name': test_mode_name}
        test_modes.append(test_mode)

    results = loadresults(id)
    framework_dict = {'framework_id': id, 'name': name, 'target': target, 'description': description, 'test_report_directory': test_report_directory, 'test_report_email': test_report_email, 'test_suites': test_suites, 'test_modes': test_modes, 'results': results}
    db_controller.closeConnection(db_connection)
    response = {'status': 'success', 'framework': framework_dict}
    return jsonify(response)

@app.route('/test_suite/load_test_suite', methods=['GET'])
def loadTestSuite():
    test_suite_id = request.args.get('test_suite_id')
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    print("Loading your UniTest frameworks....")
    #Load framework instances
    test_suite_data = db_controller.get_data(db_connection, 'test_suites', test_suite_id, 'test_suite_id')
    for data in test_suite_data:
        test_suite_id = data[0]
        test_suite_name = data[1]
        test_suite_description = data[2]
        test_script_dir = data[3]
        framework_id = data[5]
    test_suite_result_data = db_controller.get_data(db_connection, 'test_suite_results', test_suite_id, 'test_suite_id')
    test_suite_results = []
    for data in test_suite_result_data:
        test_suite_results_id = data[0]
        date = data[2]
        test_suite_result = {'test_suite_results_id': test_suite_results_id,  'date': date}
        test_suite_results.append(test_suite_result)
    test_suite = {'framework_id': framework_id, 'test_suite_id': test_suite_id, 'test_suite_name': test_suite_name, 'test_suite_description': test_suite_description, 'test_script_dir': test_script_dir, 'test_suite_results': test_suite_results}
    db_controller.closeConnection(db_connection)
    response = {'status': 'success', 'test_suite': test_suite}
    return jsonify(response)

@app.route('/test_mode/load_test_mode', methods=['GET'])
def loadTestMode():
    test_mode_id = request.args.get('test_mode_id')
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    #Load framework instances
    test_mode_data = db_controller.get_data(db_connection, 'test_modes', test_mode_id, 'test_mode_id')
    for data in test_mode_data:
        test_mode_id = data[0]
        test_mode_name = data[1]
        test_mode_host = data[2]
        test_mode_username = data[3]
        test_mode_key_path = data[4]
        test_mode_test_path = data[5]
        test_mode_requirements_path = data[6]
        test_mode_env_vars_path = data[7]
        created_at = data[9]
        test_runner_id = data[10]
        init_file_path = data[11]
    test_runner_data = db_controller.get_data(db_connection, 'test_runners', test_runner_id, 'id')
    if test_runner_data:
        for data in test_runner_data:
            test_runner_name = data[1]
    else:
        test_runner_name = None
    test_mode = {'test_mode_id': test_mode_id, 'test_mode_name': test_mode_name, 'test_mode_host': test_mode_host, 'test_mode_username': test_mode_username, 'test_mode_key_path': test_mode_key_path, 'test_mode_test_path': test_mode_test_path,'test_mode_requirements_path': test_mode_requirements_path, 'test_mode_env_vars_path': test_mode_env_vars_path, 'test_runner': test_runner_name, 'init_file_path': init_file_path, 'created_at': created_at}
    db_controller.closeConnection(db_connection)
    response = {'status': 'success', 'test_mode': test_mode}
    return jsonify(response)

@app.route('/test_suite_result/load_test_suite_result', methods=['GET'])
def loadTestSuiteResult():
    test_suite_result_id = request.args.get('test_suite_result_id')
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    test_suite_result_data = db_controller.get_data(db_connection, 'test_suite_results', test_suite_result_id, 'id')
    for data in test_suite_result_data:
        test_suite_results_id = data[0]
        test_suite_name = data[1]
        date = data[2]
        passed = data[3]
        failed = data[4]
        error = data[5]
        execution_time = data[6]
        test_suite_id = data[8]
    test_results_data = db_controller.get_data(db_connection, 'test_results', test_suite_results_id, 'test_suite_results_id')
    test_results = []
    for data in test_results_data:
        test_name = data[1]
        status = data[2]
        error_messages = data[3]
        test_result_execution_time = data[4]
        test_result = { 'test_result_name': test_name, 'test_result_status': status, 'test_result_error_messages': error_messages, 'test_result_execution_time': test_result_execution_time}
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
            coverage_result = {'function_coverage': function_coverage, 'line_coverage': line_coverage, 'branch_coverage': branch_coverage, 'covered_functions': covered_functions, 'uncovered_functions': uncovered_functions}
            coverage_results.append(coverage_result)
    test_suite_result = {'test_suite_results_id': test_suite_results_id, 'test_suite_name': test_suite_name, 'test_suite_id': test_suite_id, 'date': date, 'passed': passed, 'failed': failed, 'error': error, 'execution_time': execution_time, 'test_results': test_results, 'coverage_results': coverage_results}
    db_controller.closeConnection(db_connection)
    response = {'status': 'success', 'test_suite_result': test_suite_result}
    return jsonify(response)

@app.route('/framework/load_results', methods=['POST'])
def loadresults(framework_id):
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    reports = []
    report_data = db_controller.get_data(db_connection, 'reports', framework_id, 'framework_id')
    for data in report_data:
        id = data[0]
        date = data[1]
        report = {'report_id': id, 'date': date}
        reports.append(report)
    db_controller.closeConnection(db_connection)
    return reports

@app.route('/framework/load_report', methods=['GET'])
def loadreport():
    report_id = request.args.get('report_id')
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    report_data = db_controller.get_data(db_connection, 'reports', report_id, 'id')
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
            test_summary = {'number_of_test_suites': number_of_test_suites, 'number_of_test_cases': number_of_test_cases, 'passes': passes, 'failures': failures,'errors': errors, 'success_rate': success_rate}
        
        #Load test environment data for report
        environment_data = db_controller.get_data(db_connection, 'environment_details', id, 'report_id')
        for data in environment_data:
            os_type = data[2]
            os_version = data[3]
            ip_address = data[4]
            test_directory = data[5]
            python_version = data[6]
            environment_details = {'os_type': os_type, 'os_version': os_version, 'ip_address': ip_address, 'test_directory': test_directory, 'python_version': python_version}

        #Load test execution data for report
        execution_data = db_controller.get_data(db_connection, 'execution_details', id, 'report_id')
        for data in execution_data:
            test_suites_executed_json = data[2]
            start_time = data[3]
            end_time = data[4]
            total_time = data[5]
            test_suites_executed = json.loads(test_suites_executed_json)
            execution_details = {'test_suites_executed': test_suites_executed, 'start_time': start_time, 'end_time': end_time, 'total_time': total_time}

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
                test_result = {'test_name': test_name, 'status': status, 'error_messages': error_messages, 'execution_time': test_result_execution_time}
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
                    coverage_result = {'function_coverage':function_coverage, 'line_coverage': line_coverage, 'branch_coverage': branch_coverage,'covered_functions': covered_functions,'uncovered_functions': uncovered_functions}
                    coverage_results.append(coverage_result)
            test_suite_result = {'test_suite_name': test_suite_name,'date': date,'passed': passed,'failed': failed,'error': error,'execution_time': execution_time,'test_results': test_results,'coverage_results': coverage_results}
            test_suite_results.append(test_suite_result)
        report = {'report_id': id, 'date': date, 'test_summary': test_summary, 'environment_details': environment_details,'execution_details': execution_details,'test_suite_results': test_suite_results,'framework_id': framework_id}
    db_controller.closeConnection(db_connection)
    response = {'status': 'success', 'report': report}
    return jsonify(response)

def parseXMLtoDict(element):
    print("Inside parsexmltoDict")
    if not list(element):
        return element.text
    
    child_dict = {}
    for child in element:
        child_value = parseXMLtoDict(child)

        if child.tag in child_dict:
            if type(child_dict[child.tag]) is list:
                child_dict[child.tag].append(child_value)
            else:
                child_dict[child.tag] = [child_dict[child.tag], child_value]
        else:
            child_dict[child.tag] = child_value
    return child_dict

def parseConfigXML(file_path):
    print("Inside parse config")
    try:
        print("Inside parse config try except")
        tree = ET.parse(file_path)
        root = tree.getroot()
        return {root.tag: parseXMLtoDict(root)}
    except:
        print("Error parsing xml file")
        return "Error parsing xml file"

@socketio.on('connect')
def test_connect():
    print('Client connected')
    emit('test_output', {'data': 'Connection Established'})

def loadframeworks():
    db_controller = DatabaseHandler()
    db_connection = db_controller.connection()
    print("Loading your UniTest frameworks....")
    #Load framework instances
    frameworks = []
    framework_data = db_controller.get_all(db_connection, 'frameworks')
    for data in framework_data:
        framework_id = data[0]
        name = data[1]
        target = data[2]
        description = data[3]
        reports = []            
        test_report_directory = data[5]
        test_report_email = data[6]
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
    return frameworks

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)



    

    

        


