from Reporting.Results import TestSuiteResult

class TestSuite:
    def __init__(self, id, suite_name, suite_description, test_script):
        self.results = []
        self.coverage_files = []
        self.id = id
        self.suite_name = suite_name
        self.suite_description = suite_description
        self.test_script = test_script

    def getID(self):
        return self.id
    
    def getName(self):
        return self.suite_name
    
    def getDescription(self):
        return self.suite_description
    
    def getTestScript(self):
        return self.test_script
    
    def getResultsHistory(self):
        return self.results
    
    def getResult(self, index):
        return self.results[index]

    def getCoverageFiles(self):
        return self.coverage_files
    
    def addCoverageFiles(self, file):
        self.coverage_files.append(file)
    
    def getDetails(self):
        details = "Test Suite Name: " + self.suite_name + "\n"
        details += "Description: " + self.suite_description + "\n"
        if self.coverage_files:
            for coverage_file in self.coverage_files:
                details += f"Coverage File: {coverage_file}\n"
        else:
            details += f"No coverage files were found for thsi test suite\n"
        return details
    
    def setName(self, name):
        self.suite_name = name

    def setDescription(self, desc):
        self.description = desc

    def setTestScript(self, script):
        self.test_script = script

    def addResult(self, result):
        self.results.append(result)








    

    
    


