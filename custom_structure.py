class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return len(self.items)==0

    def push(self,item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        if not self.isEmpty():
            return self.items[len(self.items)-1]
        else:
            # print('stack is empty')
            return -1

    def size(self):
        return len(self.items)

    def clean(self):
        self.items = []

class Paragraph:
    def __init__(self):
        self.sentences = []

    def show(self):
        for s in self.sentences:
            print(s)

class Mark:
    def __init__(self):
        self.word_now = []
        self.word_origin = []
        self.label = []
        self.emo = []

    def show(self):
        for i in range(len(self.word_now)):
            print(self.word_now[i],' ',self.word_origin[i],' ',self.label[i],' ',self.emo[i])

    def statistic_len(self,threshold):
        if len(self.word_now)>threshold:
            print('** ',len(self.word_now))
            return True
        return False
