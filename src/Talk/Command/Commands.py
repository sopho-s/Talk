import os

class Command:
    def __init__(self, commands, commandlist):
        self.commands = []
        self.currentcommand = 0
        self.stdout = []
        takenkeys = commandlist["TAKEN"].keys()
        freekeys = commandlist["FREE"].keys()
        for command in commands:
            if command in takenkeys:
                for macro in commandlist["TAKEN"][command]:
                    self.commands.append(macro)
            elif command in freekeys:
                for macro in commandlist["FREE"][command]:
                    self.commands.append(macro)
            else:
                self.commands.append(command)
    def RunNext(self):
        if self.currentcommand != len(self.commands):
            if self.commands[self.currentcommand] == "<RESET>":
                raise Exception("STOP")
            print(f"EXECUTING {self.commands[self.currentcommand]}")
            x = os.popen(self.commands[self.currentcommand])
            self.stdout.append(x.read())
            self.currentcommand += 1
            return True
        return False