class Framework:
    def __init__(self, framework_id, framework_name, framework_target, description, test_report_directory, test_report_email, reports):
        self.framework_id = framework_id
        self.framework_name = framework_name
        self.framework_target = framework_target
        self.description = description
        self.test_report_directory = test_report_directory
        self.test_report_email = test_report_email
        self.reports = reports
        self.test_suites = []
        self.test_modes = []
        self.test_runners = []

    def getID(self):
        return self.framework_id
    
    def getName(self):
        return self.framework_name
    
    def getTarget(self):
        return self.framework_target
    
    def getDescription(self):
        return self.description
    
    def getTestReportDirectory(self):
        return self.test_report_directory
    
    def getTestReportEmail(self):
        return self.test_report_email
    
    def getTestSuites(self):
        return self.test_suites
    
    def getTestModes(self):
        return self.test_modes
    
    def getTestRunners(self):
        return self.test_runners
    
    def getReports(self):
        return self.reports
    
    def getTestSuite(self, test_suite_name):
        for test_suite in self.test_suites:
            if test_suite.getName() == test_suite_name:
                return test_suite
        print(f"The given Test Suite '{test_suite_name}' does not exist for this framework")
        return
    
    def getTestMode(self, test_mode_name):
        for test_mode in self.test_modes:
            if test_mode.getTestModeName() == test_mode_name:
                return test_mode
        print(f"The given Test Mode '{test_mode_name}' does not exist for {self.framework_name}")
        return
    
    def getReport(self, report_date):
        for report in self.reports:
            if report.getDate() == report_date:
                return report
        print("The given Test Mode does not exist for this framework")
        return
        
    def addTestSuite(self, test_suite):
        self.test_suites.append(test_suite)

    def addTestMode(self, test_mode):
        self.test_modes.append(test_mode)
    
    def addTestRunner(self, test_runner):
        self.test_runners.append(test_runner)

    def addReport(self, report):
        self.reports.append(report)
    
    def getDetails(self):
        details = "Framework ID: " + str(self.framework_id) + "\n"
        details += "Framework Name: " + self.framework_name + "\n"
        details += "Test Target: " + self.framework_target + "\n"
        details += "Description: " + self.description
        return details
        
    