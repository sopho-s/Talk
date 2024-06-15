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
        if self.count == 0:
            self.current = self.head
            raise StopIteration
        with self.queuelock:
            if self.current < self.tail:
                self.current += 1
                while self.queue[self.current-1] == None:
                    self.current += 1
                    if self.current >= self.tail:
                        self.current = self.head
                        raise StopIteration
                return self.queue[self.current-1]
            else:
                self.current = self.head
                raise StopIteration
    def __len__(self):
        return self.count
    def Remove(self, index):
        for i in range(self.size):
            if index == 0:
                index = i
                break
            if self.queue[i] != None:
                index -= 1
        self.queue[index] = None
        self.count -= 1
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
            return False
        returnval = None
        with self.queuelock:
            while self.queue[self.head] == None:
                self.head = (1 + self.head) % self.size
            returnval = self.queue[self.head]
            self.head = (1 + self.head) % self.size
            self.current = self.head
            self.count -= 1
        return returnval
            
