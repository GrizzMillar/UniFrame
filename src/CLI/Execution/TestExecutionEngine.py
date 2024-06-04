from FrameworkObjects.TestRunner import TestRunner
from FrameworkObjects.TestSuite import TestSuite
from Reporting.Results import TestResult
from Reporting.Results import CoverageResult
from Reporting.Results import TestSuiteResult, EnvironmentDetails, TestSummary, ExecutionDetails
from Reporting.ResultReporter import ResultReporter
from Execution.EnvironmentManager import EnvironmentManager
import subprocess
import json
from datetime import datetime

class TestExecutionEngine:
    def __init__(self):
        self.test_suites = []
        self.test_mode = None
        self.current_connection = None
        self.results_reporter = ResultReporter()
        self.environment_manager = EnvironmentManager()
    
    def getEnvironmentManager(self):
        return self.environment_manager
    
    def loadTestSuite(self, test_suite):
        self.current_test = test_suite

    def setTestMode(self, test_mode):
        self.test_mode = test_mode

    def addTestSuite(self, test_suite):
        self.test_suites.append(test_suite)

    def configureTestEnvironment(self, output_callback=None):
        test_scripts = []
        for suite in self.test_suites:
            test_scripts.append(suite.getTestScript())
        result = self.environment_manager.setUpEnvironment(self.test_mode, test_scripts, output_callback)
        if result is None:
            return None
        return True
    
    def tearDownEnvironment(self, output_callback=None):
        test_scripts = []
        for suite in self.test_suites:
            test_scripts.append(suite.getName())
        self.environment_manager.tearDownEnvironment(self.test_mode, test_scripts, output_callback)
        
    def executeRemoteTest(self, output_callback=None):
        print("****************************************Executing Test Suites.....****************************************\n")
        ssh = self.getEnvironmentManager().getSSHClient()
        test_path = self.test_mode.getTestPath()
        env_vars = self.test_mode.getEnvironmentVariablesPath()
        test_scripts = []
        for suite in self.test_suites:
            test_scripts.append(suite.getName())
        test_suites_argument = " ".join([script[0:-3] for script in test_scripts])
        if self.test_mode.getTestRunner() is None:
           command = f'cd {test_path} && python3 MasterTestRunner.py {test_suites_argument} --env {env_vars}'
        else:
            test_runner = self.test_mode.getTestRunner().getName()
            command = f'cd {test_path} && python3 TestRunnerWrapper.py {test_suites_argument} --runner_module {test_runner} --env {env_vars}'
        if output_callback is None:
            try:
                stdin, stdout, stderr = ssh.exec_command(command)
                test_output = stdout.read().decode().strip()
                err = stderr.read().decode()
                if test_output:
                    if err:
                        print("Note: Recived the following output message:", err, "\n")
                    test_suite_results, environment_details, execution_details, summary_details = self.parseOutput(test_output)
                    self.collectResults(test_suite_results, environment_details, execution_details, summary_details)
                    #print("Debug: Test Output Recieved:\n", test_output)
            except Exception as e:
                    print(f"Error during test execution: {e}")
                    return None
        else:
            output_callback("****************************************Executing Test Suites.....****************************************\n")
            full_output = []
            try:
                stdin, stdout, stderr = ssh.exec_command(command)
                while True:
                    line = stdout.readline()
                    if not line:
                        break
                    line_decoded = line.strip()
                    full_output.append(line_decoded)
                test_output = "\n".join(full_output).strip()
                if test_output:
                    test_suite_results, environment_details, execution_details, summary_details = self.parseOutput(test_output)
                    self.collectResults(test_suite_results, environment_details, execution_details, summary_details)
                #print("Debug: Test Output Recieved:\n", test_output)
                err = ""
                for line in stderr:
                    err += line
                if err.strip():
                    print("Note: Recived the following message in stderr:", err.strip())
                    if output_callback:
                        output_callback(f"Error: {err.strip()}")
            except Exception as e:
                    print(f"Error during test execution: {e}")
                    if output_callback:
                        output_callback(f"Error during test execution{e}")
                    return None
        
    def executeLocalTest(self, output_callback=None):
        print("****************************************Executing Test Suites.....****************************************\n")
        if output_callback:
            output_callback("****************************************Executing Test Suites.....****************************************\n")
        test_path = self.test_mode.getTestPath()
        test_scripts = []
        for suite in self.test_suites:
            test_scripts.append(suite.getName())
        test_suites_argument = " ".join([script[0:-3] for script in test_scripts])
        if self.test_mode.getTestRunner() is None:
            command = f'cd "{test_path}" && python3 MasterTestRunner.py {test_suites_argument}'
        else:
            test_runner = self.test_mode.getTestRunner().getName()
            command = f'cd "{test_path}" && python3 TestRunnerWrapper.py {test_suites_argument} --runner_module {test_runner}'
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            test_output = result.stdout
            err = result.stderr
            if err:
                print("Note: Recived the following output message:", err)
                if output_callback:
                    output_callback(f"Note: Recived the following output message: {err}")
            print(test_output)
            test_suite_results, environment_details, execution_details, summary_details = self.parseOutput(test_output, output_callback)
            self.collectResults(test_suite_results, environment_details, execution_details, summary_details, output_callback)
        except Exception as e:
            print(f"Error during test execution: {e}")
            if output_callback:
                output_callback(f"Error during test execution: {e}")
            return None
        return True
    
    def parseOutput(self, output, output_callback=None):
        test_suite_results = []
        environment_details = []
        execution_details = []
        summary_details = []
        print("****************************************Parsing Test Output....****************************************\n")
        if output_callback:
            output_callback("****************************************Parsing Test Output....****************************************\n")
        try: 
            data = json.loads(output)
            for result_data in data['test_suite_results']:
                suite_name = result_data['test_suite'].strip().split('.')[-1] + '.py'
                execution_time = result_data['total_time']
                test_results = result_data['test_results']
                suite_results = []
                for result in test_results:
                    test_result = TestResult(
                    result['test_name'].strip().split('.')[-1],
                    result['status'].strip(),
                    #result['error_messages'].strip(),
                    result.get('error_messages', 'N/A').strip(),
                    result['execution_time'].strip()
                    )
                    suite_results.append(test_result)

                coverage_results = []
                coverage_files=[]
                for suite in self.test_suites:
                    if suite.getName() == suite_name:
                        if suite.getCoverageFiles() is not None:
                            coverage_files = suite.getCoverageFiles()
                        else:
                            coverage_files = None
                if coverage_files is not None:
                    for coverage_file in coverage_files:
                        coverage_data = result_data['coverage_results'].get(coverage_file)
                        if coverage_data:
                            coverage_result = CoverageResult(
                                coverage_data['function_coverage'],
                                coverage_data['line_coverage'],
                                coverage_data['branch_coverage'],
                                coverage_data['covered_functions'],
                                coverage_data['uncovered_functions']
                            )
                            coverage_results.append(coverage_result)
                        else:
                            print(f"Coverage data could not be found for {coverage_file}")
                            if output_callback:
                                output_callback(f"Coverage data could not be found for {coverage_file}")

                if not coverage_results:
                    coverage_results = None

                passed = 0
                failed = 0
                error = 0
                for result in suite_results:
                    if result.getStatus() == 'Passed':
                        passed +=1
                    elif result.getStatus() == 'Failed':
                        failed +=1
                    elif result.getStatus() == 'Error':
                        error +=1
                test_suite_result = TestSuiteResult(suite_name, datetime.now(), passed, failed, error, execution_time, suite_results, coverage_results)
                test_suite_results.append(test_suite_result)

            environment_data = data['environment_details']
            if environment_data:
                environment_details = EnvironmentDetails(environment_data['OS Type'], environment_data['OS Version'], environment_data['IP Address'], environment_data['Test Directory'], environment_data['Python Version'])
            execution_details = ExecutionDetails(data['executed_test_suites'], data['start_time'], data['end_time'], data['total_execution_time'])

            total_tcs = 0
            for suite_results in test_suite_results:
                total_tcs += suite_results.getPassed() + suite_results.getFailed() + suite_results.getErrors()
            total_passes = 0
            for suite_results in test_suite_results:
                total_passes += suite_results.getPassed()
            total_failures = 0
            for suite_results in test_suite_results:
                total_failures += suite_results.getFailed() 
            total_errors = 0
            for suite_results in test_suite_results:
                total_errors += suite_results.getErrors()
            success_rate = total_passes/total_tcs * 100
            summary_details = TestSummary(data['num_of_suites'], total_tcs, total_passes, total_failures, total_errors, success_rate)
            print("Successfully Parsed the Test Output!")
            if output_callback:
                output_callback("Successfully Parsed the Test Output!")
        except json.JSONDecodeError as e:
            print("Error parsing test output line: ", e)
            if output_callback:
                output_callback(f"Error parsing test output line: {e}")
        except KeyError as e:
            print(f"Key error in parsing json: ",{e})
            if output_callback:
                output_callback(f"Key error in parsing json: {e}")
        return test_suite_results, environment_details, execution_details, summary_details

    def collectResults(self, test_suite_results, environment_details, execution_details, summary_details, output_callback=None):
        print("****************************************Collecting results....****************************************\n")
        if output_callback:
            output_callback("****************************************Collecting results....****************************************\n")
        reporter = self.results_reporter
        for result in test_suite_results:
            reporter.addTestSuiteResult(result)
        reporter.setEnvironmentDetails(environment_details)
        reporter.setExecutionDetails(execution_details)
        reporter.setSummaryDetails(summary_details)
        print("Results Saved")
        if output_callback:
            output_callback("Results Saved")

    def generateReport(self, framework, output_callback=None):
        print("****************************************Generating Report....****************************************\n")
        if output_callback:
            output_callback("****************************************Generating Report....****************************************\n")
        reporter = self.results_reporter
        report = reporter.generateReport(framework)
        print("Test Report Saved")
        if output_callback:
            output_callback("Test Report Saved")
        return report
    
    def testSummary(self, report):
        report_content = f"****************************************TEST SUMMARY****************************************\n"
        report_content += f"*******************************************************************************************\n"
        report_content += f"{report.getDate()}\n"
        report_content += f"Number of Test Suites's: {report.getTestSummary().getNumberOfTestSuites()}\n"
        report_content += f"Number of Test Cases's: {report.getTestSummary().getNumberOfTestCases()}\n"
        report_content += f"Number of Passes's: {report.getTestSummary().getPasses()}\n"
        report_content += f"Number of Failure's: {report.getTestSummary().getFailures()}\n"
        report_content += f"Number of Error's: {report.getTestSummary().getErrors()}\n"
        report_content += f"Success Rate: {report.getTestSummary().getSuccessRate()}\n"
        report_content += "\n"
        return report_content
    
    def RunEngine(self, framework, output_callback=None):
        print("****************************************Starting Engine....****************************************\n")
        framework_id = framework.getID()
        create_report = True
        result = self.configureTestEnvironment(output_callback)
        if result is None:
            print("Failed to set up test environment")
            return
        if self.test_mode.getHost() == 'localhost':
            result = self.executeLocalTest(output_callback)
            if result == None:
                create_report == False
        else:
            result = self.executeRemoteTest(output_callback)
            if result == None:
                create_report == False
        self.tearDownEnvironment(output_callback)
        if not create_report:
                print("Test Exectuion Failed")
                print("Exiting")
        else: 
            report = self.generateReport( framework, output_callback)
            print('****************************************Finished****************************************\n')
            print(self.testSummary(report))
            if output_callback:
                output_callback('****************************************Finished****************************************\n')
                output_callback(self.testSummary(report))





