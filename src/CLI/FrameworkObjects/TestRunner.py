class TestRunner:
    def __init__(self, id, name, location):
        self.id = id
        self.name = name
        self.location = location

    def getID(self):
        return self.id
    
    def getName(self):
        return self.name
    
    def getLocation(self):
        return self.location
    
    def getDetails(self):
        details = ''
        details += f'ID: {self.id}\n'
        details += f'Name: {self.name}\n'
        details += f'Location: {self.location}\n'
        return details