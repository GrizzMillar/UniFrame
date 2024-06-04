from Reporting.Report import Report
import matplotlib.pyplot as plot 
import smtplib
from email.message import EmailMessage
from Execution.DatabaseHandler import DatabaseHandler
import json
import time
from os.path import basename

class ResultReporter:
    def __init__(self):
        self.test_suite_results = []
        self.environment_details = []
        self.execution_details = []
        self.summary_details = []
    
    def addTestSuiteResult(self, test_suite_result):
        self.test_suite_results.append(test_suite_result)

    def setSummaryDetails(self, summary):
        self.summary_details = summary

    def setEnvironmentDetails(self, env_details):
        self.environment_details = env_details

    def setExecutionDetails(self, execution):
        self.execution_details = execution

    def generateReport(self, framework):
        framework_id = framework.getID()
        start_time = time.time()
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        report = Report(date, self.summary_details, self.environment_details, self.execution_details, self.test_suite_results, framework_id)
        db_controller = DatabaseHandler()
        db_connection = db_controller.connection()
        field_names = ['date', 'framework_id']
        data_values = [date, framework_id]
        report_id = db_controller.insert_data(db_connection, 'reports', field_names, data_values)
        if report_id is not None:
            test_summary_data_values = [report_id, self.summary_details.getNumberOfTestSuites(), self.summary_details.getNumberOfTestCases(), self.summary_details.getPasses(), self.summary_details.getFailures(), self.summary_details.getErrors(), self.summary_details.getSuccessRate()]
            test_summary_field_names = ['report_id', 'number_test_suites', 'number_test_cases', 'passes', 'failures', 'errors', 'success_rate']
            test_summary_table_name = 'test_summary'
            db_controller.insert_data(db_connection, test_summary_table_name, test_summary_field_names, test_summary_data_values)

            environment_details_data_values = [report_id, self.environment_details.getOSType(), self.environment_details.getOSVersion(), self.environment_details.getIPAddress(), self.environment_details.getTestDirectory(), self.environment_details.getPythonVersion()]
            environment_details_field_names = ['report_id', 'os_type', 'os_version', 'ip_address', 'test_directory', 'python_version']
            environment_details_table_name = 'environment_details'
            db_controller.insert_data(db_connection, environment_details_table_name, environment_details_field_names, environment_details_data_values)

            executed_test_suites_json = json.dumps(self.execution_details.getTestSuitesExecuted())
            execution_details_data_values = [report_id, executed_test_suites_json, self.execution_details.getStartTime(), self.execution_details.getEndTime(), self.execution_details.getTotalTime()]
            execution_details_field_names = ['report_id', 'test_suites_executed', 'start_time', 'end_time', 'total_time']
            execution_details_table_name = 'execution_details'
            db_controller.insert_data(db_connection, execution_details_table_name, execution_details_field_names, execution_details_data_values)

            for suite in self.test_suite_results:
                test_suite_data = db_controller.get_data_for_id(db_connection, 'test_suites', suite.getTestSuiteName(), 'test_suite_name', framework_id)
                test_suite_id = test_suite_data[0][0]
                test_suite_results_data_values = [suite.getTestSuiteName(), suite.getDate(), suite.getPassed(), suite.getFailed(), suite.getErrors(), suite.getExecutionTime(), report_id, test_suite_id]
                test_suite_results_field_names = ['test_suite_name', 'date', 'passed', 'failed', 'error', 'execution_time', 'report_id', 'test_suite_id']
                test_suite_results_table_name = 'test_suite_results'
                test_suite_results_id = db_controller.insert_data(db_connection, test_suite_results_table_name, test_suite_results_field_names, test_suite_results_data_values)
                for test_result in suite.getTestResults():
                    test_result_data_values = [test_result.getName(), test_result.getStatus(), test_result.getErrorMessages(), float(test_result.getExecutionTime().rstrip('s')), test_suite_results_id]
                    test_result_field_names = ['test_name', 'status', 'error_messages', 'execution_time', 'test_suite_results_id']
                    test_result_table_name = 'test_results'
                    db_controller.insert_data(db_connection, test_result_table_name, test_result_field_names, test_result_data_values)
                if suite.getCoverageResults() is not None:
                    for coverage_result in suite.getCoverageResults():
                        covered_functions_json = json.dumps(coverage_result.getCoveredFunctions())
                        uncovered_functions_json = json.dumps(coverage_result.getUncoveredFunctions())
                        coverage_result_data_values = [coverage_result.getFunctionCoverage(), coverage_result.getLineCoverage(), coverage_result.getBranchCoverage(), covered_functions_json, uncovered_functions_json, test_suite_results_id]
                        coverage_result_field_names = ['function_coverage', 'line_coverage', 'branch_coverage', 'covered_functions', 'uncovered_functions', 'test_suite_results_id']
                        coverage_result_table_name = 'coverage_results'
                        db_controller.insert_data(db_connection, coverage_result_table_name, coverage_result_field_names, coverage_result_data_values)
            test_report_directory = framework.getTestReportDirectory()
            report_name = f'Test Report:{date}.pdf'
            if test_report_directory:
                report_name = test_report_directory + '/' + report_name
                report.generatePDFReport(report_name)
            test_report_email = framework.getTestReportEmail()
            if test_report_email:
                self.email(report_name, test_report_email)
            print('Results successfully stored in database!')
            return report
        else:
            print('Failed to store report in the database')
    
    def exportReport(self, report, format):
        report = self.generateReport()
        if format == "PDF":
            pass
        elif format == "HTML":
            pass

    def email(self, file, email):
        msg = EmailMessage()
        msg['Subject'] = f'The contents {file}'
        msg['From'] = "clmillar009@gmail.com"
        msg['To'] = email
        with open(file, 'rb') as f:
            file_content = f.read()
            msg.add_attachment(file_content, maintype='application', subtype='pdf', filename=basename(file))
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        try:
            server.login("clmillar009@gmail.com", "lshr pjpw hfha bumm")
            server.send_message(msg)
            print("Email Successfully Sent")
        except Exception as e:
            print(f"Failed to send the results email: {e}")
        finally:
            server.quit()

    def barGraphGenerator(self):
        graph_data = {'Passed': 0, 'Failed': 0, 'Error': 0}

        for result in self.test_results:
            graph_data[result.getStatus()] += 1

        plot.bar(graph_data.keys(), graph_data.values())
        plot.xlabel('Status')
        plot.ylabel('Number of Tests')
        plot.title('Test Results Overview')

        max_tests = max(graph_data.values())
        plot.ylim(0, max_tests + 1)

        plot.savefig("test_results_overview.png")
        plot.show()
