import threading

class CircularQueue:
    def __init__(self, size):
        self.size = size
        self.count = 0
        self.head = 0
        self.tail = 0
        self.queue = [None for _ in range(size)]
        self.queuelock = threading.Lock()
        self.current = self.head
    def __iter__(self):
        return self
    def __next__(self):
        print(True)
        with self.queuelock:
            if self.current < self.tail:
                self.current += 1
                return self.queue[self.current-1]
            else:
                self.current = self.head
                raise StopIteration
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
            self.current = self.head
            self.count -= 1
        return returnval
            