class Operation:
    def __init__(self, position, text):
        self.position = position
        self.text = text

    def __truediv__(self, prev_operation):
        pass

    def execute(self, file):
        pass

    def __str__(self):
        return f"[{self.__class__}, {self.position} {self.text}]"


class NeutralOperation(Operation):
    pass


class Insert(Operation):
    def execute(self, file_content):
        return file_content[:self.position] + self.text + file_content[self.position:]

    def __truediv__(self, prev_operation):
        # insert
        if isinstance(prev_operation, Insert):
            if self.position <= prev_operation.position:
                return Insert(self.position, self.text)
            else:
                return Insert(self.position + len(prev_operation.text), self.text)
        # delete
        elif isinstance(prev_operation, Delete):
            if self.position <= prev_operation.position:
                return Insert(self.position, self.text)
            elif self.position >= (prev_operation.position + len(prev_operation.text)):
                return Insert(self.position - len(prev_operation.text), self.text)
            else:
                return Insert(prev_operation.position, self.text)


class Delete(Operation):
    pass
