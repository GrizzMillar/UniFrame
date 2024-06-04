import paramiko
import socket
import logging
import os
import subprocess
import shutil
import json
from Reporting.Results import TestResult
from Reporting.ResultReporter import ResultReporter

logging.basicConfig(filename='paramiko.log', level=logging.DEBUG)
paramiko.util.log_to_file('paramiko.log')

class EnvironmentManager:

    def __init__(self):
        self.ssh_client = None

    def establishConnection(self, host, username, key_path, output_callback=None):
        print(f"****************************************Connecting to host {host}......****************************************\n")
        if output_callback:
            output_callback(f"****************************************Connecting to host {host}......****************************************\n")
        key_path = os.path.expanduser(key_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username=username, key_filename=key_path)
            print(f"****************************************Successfully connected to {host}****************************************\n")
            if output_callback:
                output_callback(f"****************************************Successfully connected to {host}****************************************\n")
            self.ssh_client = ssh
            return True
        except paramiko.SSHException as e:
            print(f"****************************************Connection to host {host} failed: {e}****************************************\n")
            if output_callback:
                output_callback(f"****************************************Connection to host {host} failed: {e}****************************************\n")
            return None
        except socket.gaierror as e:
            print(f"****************************************Connection to host {host} failed: {e}****************************************\n")
            if output_callback:
                output_callback(f"****************************************Connection to host {host} failed: {e}****************************************\n")
            return None
        except Exception as e:
            print(f"****************************************Connection to host {host} failed: {e}****************************************\n")
            if output_callback:
                output_callback(f"****************************************Connection to host {host} failed: {e}****************************************\n")
            return None
        
    def closeConnection(self, ssh, output_callback=None):
        print("****************************************Closing connection....****************************************\n")
        if output_callback:
            output_callback("****************************************Closing connection....****************************************\n")
        if ssh:
            ssh.close()
            print("****************************************Connection Closed****************************************\n")
            if output_callback:
                output_callback("****************************************Connection Closed****************************************\n")

    def getSSHClient(self):
        return self.ssh_client

    def setUpEnvironment(self, test_mode, test_suites, output_callback=None):
        print("****************************************Setting up the test environment....****************************************\n")
        if output_callback:
            output_callback("****************************************Setting up the test environment....****************************************\n")
        if test_mode.getHost() == 'localhost':
            result = self.setUpLocalEnvironment(test_mode, test_suites, output_callback)
            if result is None:
                return None
        else:
            result = self.establishConnection(test_mode.getHost(), test_mode.getUsername(), test_mode.getKeyPath(), output_callback)
            if result is None:
                return None
            result = self.setUpRemoteEnvironment(test_mode, test_suites, output_callback)
            if result is None:
                return None
        return True

    def setUpLocalEnvironment(self, test_mode, test_suites, output_callback=None):
        print("****************************************Setting up local test environment....****************************************\n")
        if output_callback:
            output_callback("****************************************Setting up local test environment....****************************************\n")
        if test_mode.getTestRunner() is None:
            run_suite = 'Execution/MasterTestRunner.py'
        else:
            test_runner = test_mode.getTestRunner()
            run_suite = test_runner.getLocation()
            try:
                shutil.copy('Execution/TestRunnerWrapper.py', os.path.join(test_mode.getTestPath(), os.path.basename('Execution/TestRunnerWrapper.py')))
                print(f"Test Runner Wrapper uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename('Execution/TestRunnerWrapper.py'))}")
                if output_callback:
                    output_callback(f"Test Runner Wrapper uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename('Execution/TestRunnerWrapper.py'))}")
            except Exception as e:
                print(f"Failed to upload the Test Runner Wrapper: {e}")
                if output_callback:
                    output_callback(f"Failed to upload the Test Runner Wrapper: {e}")
                return None
        if test_mode.getInitFiles():
            for init_file in test_mode.getInitFiles():
                try:
                    shutil.copy(init_file, os.path.join(test_mode.getTestPath(), os.path.basename(init_file)))
                    print(f"Initialisation File uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename(init_file))}")
                    if output_callback:
                        output_callback(f"Initialisation File uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename(init_file))}")
                    command = f'cd "{test_mode.getTestPath()}" && bash {init_file}'
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output = result.stdout
                        err = result.stderr
                        if err:
                            print("Note: Recived the following output message:", err)
                            if output_callback:
                                output_callback(f"Note: Recived the following output message: {err}")
                        print(output)
                    except Exception as e:
                        print(f"Error during execution of initialisation file: {e}")
                        if output_callback:
                            output_callback(f"Error during execution of initialisation file: {e}")
                except Exception as e:
                    print(f"Failed to upload the Initialisation File: {e}")
                    if output_callback:
                        output_callback(f"Failed to upload the Initialisation File: {e}")
                    return None
        try:
            shutil.copy(run_suite, os.path.join(test_mode.getTestPath(), os.path.basename(run_suite)))
            print(f"Run Suite Script uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename(run_suite))}")
            if output_callback:
                output_callback(f"Run Suite Script uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename(run_suite))}")
        except Exception as e:
            print(f"Failed to upload the run suite script: {e}")
            if output_callback:
                output_callback(f"Failed to upload the run suite script: {e}")
            return None
        
        for test_script in test_suites:
            try:
                shutil.copy(test_script, os.path.join(test_mode.getTestPath(), os.path.basename(test_script)))
                print(f"Test Suite Script uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename(test_script))}")
                if output_callback:
                    output_callback(f"Test Suite Script uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename(test_script))}")
            except Exception as e:
                print(f"Failed to upload the test script: {e}")
                if output_callback:
                    output_callback(f"Failed to upload the test script: {e}")
                return None
        
        try:
            shutil.copy('Reporting/CodeCoverage.py', os.path.join(test_mode.getTestPath(), os.path.basename('Reporting/CodeCoverage.py')))
            print(f"Code Coverage Script uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename('Reporting/CodeCoverage.py'))}")
            if output_callback:
                output_callback(f"Code Coverage Script uploaded to {os.path.join(test_mode.getTestPath(), os.path.basename('Reporting/CodeCoverage.py'))}")
        except Exception as e:
            print(f"Failed to upload the code coverage script: {e}")
            if output_callback:
                output_callback(f"Failed to upload the test script: {e}")
            return None

        result = self.setDependencies(test_mode, output_callback)
        if result is None:
            return None
        result = self.setEnvironmentVariables(test_mode, output_callback)
        if result is None:
            return None
        return True
        
    def setUpRemoteEnvironment(self, test_mode, test_suites, output_callback=None):
        print("****************************************Setting up remote enviornment....****************************************\n")
        if output_callback:
            output_callback("****************************************Setting up remote enviornment....****************************************\n")
        ssh = self.ssh_client
        if test_mode.getTestRunner() is None:
            run_suite = 'Execution/MasterTestRunner.py'
        else:
            test_runner = test_mode.getTestRunner()
            run_suite = test_runner.getLocation()
            try:
                with ssh.open_sftp() as sftp:
                    remote_file_path = os.path.join(test_mode.getTestPath(), os.path.basename('Execution/TestRunnerWrapper.py'))
                    sftp.put('Execution/TestRunnerWrapper.py', remote_file_path)
                    print(f"Test Runner Wrapper script uploaded to {remote_file_path}")
                    if output_callback:
                        output_callback(f"Test Runner Wrapper script uploaded to {remote_file_path}")
            except Exception as e:
                print(f"Failed to upload the Test Runner Wrapper script: {e}")
                if output_callback:
                    output_callback(f"Failed to upload the Test Runner Wrapper  script: {e}")
                return None
        
        if test_mode.getInitFiles():
            for init_file in test_mode.getInitFiles():
                try:
                    with ssh.open_sftp() as sftp:
                        remote_file_path = os.path.join(test_mode.getTestPath(), os.path.basename(init_file))
                        sftp.put(init_file, remote_file_path)
                        print(f"Initialisation script uploaded to {remote_file_path}")
                        if output_callback:
                            output_callback(f"Initialisation script uploaded to {remote_file_path}")
                        try:
                            stdin, stdout, stderr = ssh.exec_command(f'bash {remote_file_path}')
                            err = stderr.read()
                            if err:
                                print(f'Error occureed whil executing initialisation scriptCould not execute the initialisation script {err}')
                                if output_callback:
                                    output_callback(f'Error occureed whil executing initialisation scriptCould not execute the initialisation script {err}')
                            print("Initialisation script successfully executed!")
                            if output_callback:
                                    output_callback(f'Error occureed whil executing initialisation scriptCould not execute the initialisation script {err}')
                        except Exception as e:
                            print(f'Error: Could not execute the initialisation script {e}')
                            if output_callback:
                                output_callback(f'Error: Could not execute the initialisation script {e}')
                except Exception as e:
                    print(f"Failed to upload the Initlisation script: {e}")
                    if output_callback:
                        output_callback(f"Failed to upload the Initialisation script: {e}")
                    return None
        try:
            with ssh.open_sftp() as sftp:
                remote_file_path = os.path.join(test_mode.getTestPath(), os.path.basename(run_suite))
                sftp.put(run_suite, remote_file_path)
                print(f"Run Suite script uploaded to {remote_file_path}")
                if output_callback:
                    output_callback(f"Run Suite script uploaded to {remote_file_path}")
        except Exception as e:
            print(f"Failed to upload the run suite script: {e}")
            if output_callback:
                output_callback(f"Failed to upload the run suite script: {e}")
            return None
        
        for suite in test_suites:
            try:
                with ssh.open_sftp() as sftp:
                    remote_file_path = os.path.join(test_mode.getTestPath(), os.path.basename(suite))
                    sftp.put(suite, remote_file_path)
                    print(f"Test Script uploaded to {remote_file_path}")
                    if output_callback:
                        output_callback(f"Test Script uploaded to {remote_file_path}")
            except Exception as e:
                print(f"Failed to upload the test script: {e}")
                if output_callback:
                    output_callback(f"Failed to upload the test script: {e}")
                return None
        try:
            with ssh.open_sftp() as sftp:
                remote_file_path = os.path.join(test_mode.getTestPath(), os.path.basename('Reporting/CodeCoverage.py'))
                sftp.put('Reporting/CodeCoverage.py', remote_file_path)
                print(f"Code Coverage uploaded to {remote_file_path}")
                if output_callback:
                    output_callback(f"Code Coverage uploaded to {remote_file_path}")
        except Exception as e:
            print(f"Failed to upload the Code Coverage script: {e}")
            if output_callback:
                    output_callback(f"Failed to upload the Code Coverage script: {e}")
            return None
        
        result = self.setDependencies(test_mode, output_callback)
        if result is None:
            return None
        result = self.setEnvironmentVariables(test_mode, output_callback)
        if result is None:
            return None
        return True
        
    def setEnvironmentVariables(self, test_mode, output_callback=None):
        config = test_mode.getEnvironmentVariablesPath()
        if test_mode.getHost() == 'localhost':
            print("****************************************Setting up local environment variables...****************************************\n")
            if output_callback:
                output_callback("****************************************Setting up local environment variables...****************************************\n")
            try:
                with open(config, 'r') as file:
                    env_vars = json.load(file)
                for key, value in env_vars.items():
                    os.environ[key] = str(value)
                print("Environment Variables set successfully!")
                if output_callback:
                    output_callback("Environment Variables set successfully!")
            except Exception as e:
                print(f"Failed to set Environment Variables {e}")
                if output_callback:
                    output_callback(f"Failed to set Environment Variables {e}")
                return None
        else:
            print("****************************************Setting up Remote Environment Variables....****************************************\n")
            if output_callback:
                output_callback("****************************************Setting up Remote Environment Variables....****************************************\n")
            ssh = self.ssh_client
            remote_env_script_path = None
            try:
                with ssh.open_sftp() as sftp:
                    remote_path = os.path.join(test_mode.getTestPath(), os.path.basename(config))
                    sftp.put(config, remote_path)
                    remote_env_script_path = remote_path
                    print(f"Environment Variables file uploaded to {remote_path}")
                    if output_callback:
                        output_callback(f"Environment Variables file uploaded to {remote_path}")
            except Exception as e:
                print(f"Failed to upload the environment variables file: {e}")
                if output_callback:
                    output_callback(f"Failed to upload the environment variables file: {e}")
                return None
        return True

    def setDependencies(self, test_mode, output_callback=None):
        print("****************************************Installing dependencies....****************************************\n")
        if output_callback:
            output_callback("****************************************Installing dependencies....****************************************\n")
        requirements = test_mode.getRequirementsPath()
        if test_mode.getHost() == 'localhost':
            try:
                new_requirements_file_path = os.path.join(test_mode.getTestPath(), os.path.basename(requirements))
                shutil.copy(requirements, new_requirements_file_path)
                print(f"Requirements file uploaded to {new_requirements_file_path}")
                if output_callback:
                    output_callback(f"Requirements file uploaded to {new_requirements_file_path}")
                result = subprocess.run(f'pip install -r "{new_requirements_file_path}"', shell=True, capture_output=True, text=True)
                if result.stdout:
                    print(result.stdout)
                    if output_callback:
                        output_callback(result.stdout)
                if result.stderr:
                    print(f'Error installing dependencies: {result.stderr}')
                    if output_callback:
                        output_callback(f'Error installing dependencies: {result.stderr}')
                else:
                    print("Dependencies installed")
                    if output_callback:
                        output_callback("Dependencies installed")
            except Exception as e:
                print(f"Failed to install dependencies: {e}")
                if output_callback:
                    output_callback(f"Failed to install dependencies: {e}")
                return None
        else:
            ssh = self.ssh_client
            try:
                with ssh.open_sftp() as sftp:
                    remote_requirements_path = os.path.join(test_mode.getTestPath(), 'requirements.txt')
                    sftp.put(requirements, remote_requirements_path)
                    print("Dependency file uploaded!")
                    if output_callback:
                        output_callback("Dependency file uploaded!")
            except Exception as e:
                print(f"Failed to upload the requirements file: {e}")
                if output_callback:
                    output_callback(f"Failed to upload the requirements file: {e}")
                return None
            try:
                command = f'pip install -r {remote_requirements_path}'
                stdin, stdout, stderr = ssh.exec_command(command)
                print(stdout.read().decode())
                if output_callback:
                    output_callback(stdout.read().decode())
                err = stderr.read().decode()
                if err:
                    print(f'Debug Message: {err}')
                    if output_callback:
                        output_callback(f'Error installing dependencies: {err}')
                print("Dependencies installed!")
                if output_callback:
                    output_callback("Dependencies installed!")
            except Exception as e:
                print(f"Failed to install dependencies: {e}")
                if output_callback:
                    output_callback(f"Failed to install dependencies: {e}")
                return None
        return True
    def tearDownEnvironment(self, test_mode, test_suites, output_callback=None):
        if test_mode.getHost() == 'localhost':
            self.tearDownLocalEnvironment(test_mode, test_suites, output_callback)
        else:
            self.tearDownRemoteEnvironment(test_mode, test_suites, output_callback)
        
    def tearDownLocalEnvironment(self, test_mode, test_suites, output_callback=None):
        print("****************************************Tearing down local test environment....****************************************\n")
        if test_mode.getTestRunner() is None:
            run_suite = "MasterTestRunner.py"
        else:
            run_suite = "TestRunnerWrapper.py"
            test_runner = test_mode.getTestRunner().getName()
            try:
                os.remove(os.path.join(test_mode.getTestPath(), test_runner))
                print("Test Runner Removed")
                if output_callback:
                    output_callback("Test Runner Removed")
            except Exception as e:
                print(f"Error during environment tear down, could not remove test runner: {e}")
                if output_callback:
                    output_callback(f"Error during environment tear down, could not remove test runner: {e}")

        try:
            os.remove(os.path.join(test_mode.getTestPath(), run_suite))
            print(f"{run_suite} removed")
            if output_callback:
                output_callback(f"{run_suite} removed")
        except Exception as e:
            print(f"Error during environment tear down failed to remove {run_suite}: {e}")
            if output_callback:
                output_callback(f"Error during environment tear down failed to remove {run_suite}: {e}")
        for test_suite in test_suites:
            try:
                os.remove(os.path.join(test_mode.getTestPath(), test_suite))
                print("Test Suites Removed")
                if output_callback:
                    output_callback("Test Suites Removed")
            except Exception as e:
                print(f"Error during enviorment tear down: {e}") 
                if output_callback:
                    output_callback(f"Error during enviorment tear down: {e}")
        
        try:
            os.remove(os.path.join(test_mode.getTestPath(), 'CodeCoverage.py'))
            print("Code Coverage Removed")
            if output_callback:
                output_callback("Code Coverage Removed")
        except Exception as e:
            print(f"Error during enviorment tear down: {e}")
            if output_callback:
                output_callback(f"Error during enviorment tear down: {e}")

        requirements = test_mode.getRequirementsPath()
        try:
            print(f"Uninstalling requirements from {requirements}")
            if output_callback:
                output_callback(f"Uninstalling requirements from {requirements}")
            result = subprocess.run(['pip', 'uninstall', '-y', '-r', requirements], capture_output=True, text=True)

            if result.stdout:
                print(result.stdout)
                if output_callback:
                    output_callback(result.stdout)
            if result.stderr:
                print(f'Error uninstalling dependencies: {result.stderr}')
                if output_callback:
                    output_callback(f'Error uninstalling dependencies: {result.stderr}')
            else:
                print("Dependencies successfully uninstalled")
                if output_callback:
                    output_callback("Dependencies successfully uninstalled")
        except Exception as e:
                print(f"Failed to uninstall dependencies: {e}")
                if output_callback:
                    output_callback(f"Failed to uninstall dependencies: {e}")
                return
        
        try:
            os.remove(os.path.join(test_mode.getTestPath(), 'requirements.txt'))
            print("Requirements file Removed")
            if output_callback:
                output_callback("Requirements file Removed")
        except Exception as e:
            print(f"Error during enviorment tear down: {e}")
            if output_callback:
                output_callback(f"Error during enviorment tear down: {e}")
        
        try:
            os.remove(os.path.join(test_mode.getTestPath(), 'coverage.json'))
            print("coverage json file Removed")
            if output_callback:
                output_callback("coverage json file Removed")
        except Exception as e:
            print(f"Error during enviorment tear down: {e}")
            if output_callback:
                output_callback(f"Error during enviorment tear down: {e}")
            
        config = test_mode.getEnvironmentVariablesPath()
        try:
            with open(config, 'r') as file:
                env_vars = json.load(file)
            for key in env_vars:
                os.environ.pop(key, None)
            print("Environment Variables unset successfully!")
            if output_callback:
                output_callback("Environment Variables unset successfully!")
        except Exception as e:
                print(f"Failed to unset Environment Variables {e}")
                if output_callback:
                    output_callback(f"Failed to unset Environment Variables {e}")
        

    def tearDownRemoteEnvironment(self, test_mode, test_suites, output_callback=None):
        print("****************************************Tearing down remote test environment....****************************************\n")
        if output_callback:
            output_callback("****************************************Tearing down remote test environment....****************************************\n")
        requirements = test_mode.getRequirementsPath()
        ssh = self.ssh_client
        requirements_command = f'pip uninstall -y -r {os.path.join(test_mode.getTestPath(), requirements)}'
        try:
            print(f"Uninstalling requirements from {requirements}")
            if output_callback:
                output_callback(f"Uninstalling requirements from {requirements}")
            stdin, stdout, stderr = ssh.exec_command(requirements_command)
            test_output = stdout.read().decode()
            err = stderr.read().decode()
            if err:
                print("Note: Recieved the following output message: ", err)
                if output_callback:
                    output_callback("Note: Recieved the following output message: ", err)
            print("Requirements Uninstalled")
            if output_callback:
                output_callback("Requirements Uninstalled")
        except Exception as e:
            print(f"Error during environment tear down: {e}")
            if output_callback:
                output_callback(f"Error during environment tear down: {e}")
            return
        
        if test_mode.getTestRunner() is None:
            run_suite = 'MasterTestRunner.py'
            command = ''
            for suite in test_suites:
                command += f'rm {os.path.join(test_mode.getTestPath(), suite)} && ' 
            command += f'rm {os.path.join(test_mode.getTestPath(), run_suite)} && rm {os.path.join(test_mode.getTestPath(), "requirements.txt")} && rm {os.path.join(test_mode.getTestPath(), "env_var.json")} && rm {os.path.join(test_mode.getTestPath(), "CodeCoverage.py")} && rm {os.path.join(test_mode.getTestPath(), "coverage.json")}'
        else: 
            run_suite = 'TestRunnerWrapper.py'
            test_runner = test_mode.getTestRunner()
            test_runner_script = test_runner.getName()
            command = ''
            for suite in test_suites:
                command += f'rm {os.path.join(test_mode.getTestPath(), suite)} && ' 
            command += f'rm {os.path.join(test_mode.getTestPath(), run_suite)} && rm {os.path.join(test_mode.getTestPath(), test_runner_script)} && rm {os.path.join(test_mode.getTestPath(), "requirements.txt")} && rm {os.path.join(test_mode.getTestPath(), "env_var.json")} && rm {os.path.join(test_mode.getTestPath(), "CodeCoverage.py")} && rm {os.path.join(test_mode.getTestPath(), "coverage.json")}'
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            test_output = stdout.read().decode()
            err = stderr.read().decode()
            if err:
                print("Note: Recieved the following output message: ", err)
                if output_callback:
                    output_callback("Note: Recieved the following output message: ", err)
            print("Temporary files removed")
            if output_callback:
                output_callback("Temporary files removed")
        except Exception as e:
            print(f"Error during environment tear down: {e}")
            if output_callback:
                output_callback(f"Error during environment tear down: {e}")
        
        self.closeConnection(ssh)
        

        

