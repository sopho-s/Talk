import threading

class CircularQueue:
    def __init__(self, size):
        self.size = size
        self.count = 0
        self.head = 0
        self.tail = 0
        self.queue = [None for _ in range(size)]
        self.queuelock = threading.Lock()
    def EnQueue(self, item):
        if self.count == self.size:
            return False
        with self.queuelock:
            self.queue[self.tail] = item
            self.tail += 1
            self.tail = self.tail % self.size
            self.count += 1
        return True
    def DeQueue(self):
        if self.count == 0:
            return True
        returnval = None
        with self.queuelock:
            returnval = self.queue[self.head]
            self.head += 1
            self.head = self.head % self.size
            self.count -= 1
        return returnval
            