
class TestMode:
    def __init__(self, id, test_mode_name, host, username, key_path, test_path, requirements_path, env_vars, test_runner):
        self.id = id
        self.test_mode_name = test_mode_name
        self.host = host
        self.username = username
        self.key_path = key_path
        self.test_path = test_path
        self.requirements_path = requirements_path
        self.env_vars = env_vars
        self.test_runner = test_runner
        self.init_files = []

    def getID(self):
        return self.id
    
    def getTestModeName(self):
        return self.test_mode_name
    
    def getHost(self):
        return self.host
    
    def getUsername(self):
        return self.username
    
    def getKeyPath(self):
        return self.key_path
    
    def getTestPath(self):
        return self.test_path
    
    def getRequirementsPath(self):
        return self.requirements_path
    
    def getEnvironmentVariablesPath(self):
        return self.env_vars
    
    def getTestRunner(self):
        return self.test_runner
    
    def getInitFiles(self):
        return self.init_files
    
    def setTestModeName(self, test_mode_name):
        self.test_mode_name = test_mode_name

    def setHost(self, host):
        self.host = host

    def setUsername(self, username):
        self.username = username
    
    def setKeyPath(self, key_path):
        self.key_path = key_path

    def setTestPath(self, test_path):
        self.test_path = test_path

    def setRequirementsPath(self, requirements_path):
        self.requirements_path = requirements_path

    def setEnvironmentVariablesPath(self, env_vars):
        self.env_vars = env_vars

    def setTestRunner(self, test_runner):
        self.test_runner = test_runner

    def addInitialisationFile(self, init_file):
        self.init_files.append(init_file)
    
    def getDetails(self):
        details = "Test Mode Name: " + self.test_mode_name + "\n"
        details += "Host IP: " + str(self.host) + "\n"
        details += "Test Path: " + self.test_path + "\n"
        details += "Requirements Path: " + self.requirements_path + "\n"
        details += "Environment Variables Path: " + self.env_vars + "\n"
        if self.test_runner is not None:
            details += "Test Runner Name: " +  self.test_runner.getName() + "\n"
        else:
            details += "No Test Runner found for this Test Mode" + "\n"
        if self.init_files is not None:
            for init_file in self.init_files:
                details += "Initialisation File: " +  init_file + "\n"
        else:
            details += "No Initialisation File found for this Test Mode" + "\n"
        return details


        