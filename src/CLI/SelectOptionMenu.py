
class SelectOptionMenu:
    def __init__(self, title, start_index, data):
        self.title = title
        self.start_index = start_index
        self.data = data
    
    def displayTitle(self):
        title_length = len(self.title)
        print(self.title)
        print('*' * title_length)
        return

    def display(self):
        self.displayTitle()
        #index = self.start_index
        #for item in self.data:
            #print(f"{index}. {item}")
            #index += 1
        #return None
        for index, item in enumerate(self.data, start=self.start_index):
            print(f"{index}. {item}")
    
    def getUserInput(self):
        #if self.data == None or len(self.data) == 0:
            #return "There are no items available"
        if not self.data:
            print("There are no items available")
            return None
        self.display()
        while True:
            try:
                value = int(input("Enter Selection: "))
                if self.start_index <= value < self.start_index + len(self.data):
                    return value
                else:
                    print(f"Enter a value between {self.start_index} and {len(self.data) -1}")
            except ValueError as e:
                print(f"Error input {e}")
        

                
#Example Usage
#title = "My Menu"
#data = ["First", "Second", "Third"]
#start_index = 0
#object = 'project'
#menu = SelectOptionMenu(title, start_index, data)
#print(menu.display(object))
#menu.getUserInput()

        
