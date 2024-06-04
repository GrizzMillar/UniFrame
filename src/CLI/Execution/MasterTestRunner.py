from typing import TextIO
import unittest
import traceback
import json
import argparse
import coverage
import platform
import socket
import os
import time
from CodeCoverage import process_coverage_results
import concurrent.futures

class RunSuite(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []
        self.tc_start_times = {}

    def startTest(self, test):
        super().startTest(test)
        self.tc_start_times[test.id()] = time.time()

    def stopTest(self, test):
        super().stopTest(test)
        if test.id() in self.tc_start_times:
            del self.tc_start_times[test.id()]
    
    def addSuccess(self, test):
        execution_time = time.time() - self.tc_start_times.get(test.id(), 0)
        self.results.append(self.formatResult(test, "Passed", None, execution_time))

    def addFailure(self, test, err):
        execution_time = time.time() - self.tc_start_times.get(test.id(), 0)
        self.results.append(self.formatResult(test, "Failed", err, execution_time))

    def addError(self, test, err):
        execution_time = time.time() - self.tc_start_times.get(test.id(), 0)
        self.results.append(self.formatResult(test, "Error", err, execution_time))

    def formatResult(self, test, status, error=None, execution_time=None):
        return {
            "test_name": test.id(),
            "status": status,
            "error_messages": self.errorsToString(error) if error else "",
            "execution_time": f"{execution_time:.4f}s" if execution_time is not None else "N/A"
        }
    
    def errorsToString(self, error):
        return ''.join(traceback.format_exception(*error))
    
    @staticmethod
    def setEnvironmentVairables(env_vars):
        try:
            with open(env_vars, 'r') as file:
                env_vars = json.load(file)
            for key, value in env_vars.items():
                os.environ[key] = str(value)
            #print("Environment variables set successfully!")
        except Exception as e:
            print(f"Failed to set environment variables from {env_vars}: {e}")
    
    @staticmethod
    def collectEnvironmentDetails():
        os_type = platform.system()
        os_version = platform.release()
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        test_directory = os.getcwd()
        python_version = platform.python_version()

        environment_details = {
            "OS Type": os_type,
            "OS Version": os_version,
            "IP Address": ip_address,
            "Test Directory": test_directory,
            "Python Version": python_version
        }
        return environment_details

    @classmethod
    def runTests(cls, run_script):
        start_time = time.time()

        cov = coverage.Coverage(branch=True)
        cov.start()

        suite = unittest.defaultTestLoader.loadTestsFromName(run_script)
        runner = unittest.TextTestRunner(resultclass=RunSuite)
        result = runner.run(suite)

        cov.stop()
        cov.save()

        cov.json_report(outfile='coverage.json')
        coverage_results = process_coverage_results('coverage.json')

        end_time = time.time()
        total_time = end_time - start_time

        #formatted_results = [json.dumps(result) for result in result.results]
        combined_results = {"test_results": [result for result in result.results],
                            "coverage_results": coverage_results,
                            #"environment_details": environment_details,
                            "test_suite": run_script,
                            "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                            "end_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)),
                            "total_time": total_time
                            }
        
        #print(json.dumps(combined_results))
        return combined_results
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run tests and output them in json format')
    parser.add_argument("test_scripts", nargs='+', help="Name of the test script")
    parser.add_argument("--env", help="Path to the environment variables JSON file")
    args = parser.parse_args()

    if args.env:
        RunSuite.setEnvironmentVairables(args.env)

    environment_details = RunSuite.collectEnvironmentDetails()
    all_results = []

    start_time = time.time()
    for test_script in args.test_scripts:
        results = RunSuite.runTests(test_script)
        all_results.append(results)

    end_time = time.time()
    total_time = end_time - start_time

    final_output = {
        "environment_details": environment_details,
        "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
        "end_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)),
        "total_execution_time": total_time,
        "executed_test_suites": args.test_scripts,
        "test_suite_results": all_results,
        "num_of_suites": len(args.test_scripts)
    }

    print(json.dumps(final_output))


    