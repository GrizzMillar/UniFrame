class TestResult:
    def __init__(self, test_name, status, error_messages, execution_time):
        self.test_name = test_name
        self.status = status
        self.error_messages = error_messages
        self.execution_time = execution_time

    def getName(self):
        return self.test_name
    
    def getStatus(self):
        return self.status
    
    def getErrorMessages(self):
        return self.error_messages
    
    def getExecutionTime(self):
        return self.execution_time
    
    def display(self):
        display = "Test: " + str(self.test_name) + " Status: " + str(self.status) + " Errors: " + str(self.error_messages) + "Execution Time: " + str(self.execution_time) + "\n"
        return display
    
class CoverageResult:
    def __init__(self, function_coverage, line_coverage, branch_coverage, covered_functions, uncovered_functions):
        self.function_coverage = function_coverage
        self.line_coverage = line_coverage
        self.branch_coverage = branch_coverage
        self.covered_functions = covered_functions
        self.uncovered_functions = uncovered_functions
    
    def getFunctionCoverage(self):
        return self.function_coverage
    
    def getLineCoverage(self):
        return self.line_coverage
    
    def getBranchCoverage(self):
        return self.branch_coverage
    
    def getCoveredFunctions(self):
        return self.covered_functions
    
    def getUncoveredFunctions(self):
        return self.uncovered_functions
    
    def display(self):
        display = "Function Coverage: " + str(self.function_coverage) + "\n"
        display += "Line Coverage: " + str(self.line_coverage) + "\n"
        display += "Branch Coverage: " + str(self.branch_coverage) + "\n"
        display += "Covered Functions: " + str(self.covered_functions) + "\n"
        display += "Uncovered Functions: " + str(self.uncovered_functions) + "\n"
        return display
    
class TestSuiteResult:
    def __init__(self, test_suite_name, date, passed, failed, error, execution_time, test_results, coverage_results):
        self.id = id
        self.test_suite_name = test_suite_name
        self.date = date
        self.passed = passed
        self.failed = failed
        self.error = error
        self.execution_time = execution_time
        self.test_results = test_results
        self.coverage_results = coverage_results
    
    def getTestSuiteName(self):
        return self.test_suite_name
    
    def getDate(self):
        return self.date
    
    def getPassed(self):
        return self.passed
    
    def getFailed(self):
        return self.failed
    
    def getErrors(self):
        return self.error
    
    def getExecutionTime(self):
        return self.execution_time
    
    def getTestResults(self):
        return self.test_results
    
    def getCoverageResults(self):
        return self.coverage_results
    
    def display(self):
        display = "Test Suite Name: " + str(self.test_suite_name) + "\n"
        display += "Date: " + str(self.date) + "\n"
        display += "Number of tests passed: " + str(self.passed) + "\n"
        display += "Number of tests failed: " + str(self.failed) + "\n"
        display += "Number of errors: " + str(self.error) + "\n"
        display += "Execution Time: " + str(self.execution_time) + "\n"
        display += "Test Results" + "\n"
        for result in self.test_results:
            display += result.display()
        display += "Coverage Results" + "\n"
        if self.coverage_results:
            for coverage_result in self.coverage_results:
                display += coverage_result.display()
        else:
            display += "There were no code coverage results recorded for this test suite execution"
        
        return display

class EnvironmentDetails:
    def __init__(self, os_type, os_version, ip_address, test_directory, python_version):
        self.os_type = os_type
        self.os_version = os_version
        self.ip_address = ip_address
        self.test_directory = test_directory
        self.python_version = python_version

    def getOSType(self):
        return self.os_type
    
    def getOSVersion(self):
        return self.os_version
    
    def getIPAddress(self):
        return self.ip_address
    
    def getTestDirectory(self):
        return self.test_directory
    
    def getPythonVersion(self):
        return self.python_version

class TestSummary:
    def __init__(self, number_test_suites, number_test_cases, passes, failures, errors, success_rate):
        self.number_test_suites = number_test_suites
        self.number_test_cases = number_test_cases
        self.passes = passes
        self.failures = failures
        self.errors = errors
        self.success_rate = success_rate

    def getNumberOfTestSuites(self):
        return self.number_test_suites
    
    def getNumberOfTestCases(self):
        return self.number_test_cases
    
    def getPasses(self):
        return self.passes
    
    def getFailures(self):
        return self.failures
    
    def getErrors(self):
        return self.errors
    
    def getSuccessRate(self):
        return self.success_rate

class ExecutionDetails:
    def __init__(self, test_suites_executed, start_time, end_time, total_time):
        self.test_suites_executed = test_suites_executed
        self.start_time = start_time
        self.end_time = end_time
        self.total_time = total_time

    def getTestSuitesExecuted(self):
        return self.test_suites_executed
    
    def getStartTime(self):
        return self.start_time
    
    def getEndTime(self):
        return self.end_time
    
    def getTotalTime(self):
        return self.total_time
        