import os

class Command:
    def __init__(self, commands):
        self.commands = commands
        self.currentcommand = 0
        self.stdout = []
    def RunNext(self):
        if self.currentcommand != len(self.commands):
            print(f"EXECUTING {self.commands[self.currentcommand]}")
            x = os.popen(self.commands[self.currentcommand])
            self.stdout.append(x.read())
            self.currentcommand += 1
            return True
        return False