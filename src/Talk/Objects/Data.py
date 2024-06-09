import json

class Data:
    def __init__(self, data = None):
        self.data = data
    def Stringify(self):
        if type(self.data) != str:
            self.data = json.dumps(self.data)
    def JSONify(self):
        if len(self.data) == 0:
            return
        if type(self.data) != dict:
            self.data = json.loads(self.data)
    def Encode(self):
        self.Stringify()
        return self.data.encode("utf-8")
    def Decode(self):
        self.data = self.data.decode("utf-8")
        self.JSONify()
        return self.data
        
    