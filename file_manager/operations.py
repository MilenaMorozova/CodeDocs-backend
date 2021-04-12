class Operation:
    def __init__(self, position, text):
        self.position = position
        self.text = text

    def __truediv__(self, prev_operation):
        pass

    def execute(self, file_content):
        pass

    def __str__(self):
        return f"[{self.__class__}, {self.position} {self.text}]"


class NeutralOperation(Operation):
    def __init__(self):
        super().__init__(None, None)


class Insert(Operation):
    def execute(self, file_content):
        return file_content[:self.position] + self.text + file_content[self.position:]

    def __truediv__(self, prev_operation):
        # insert
        if isinstance(prev_operation, Insert):
            if self.position <= prev_operation.position:
                return self
                # return Insert(self.position, self.text)
            else:
                return Insert(self.position + len(prev_operation.text), self.text)
        # delete
        elif isinstance(prev_operation, Delete):
            if self.position <= prev_operation.position:
                return self
                # return Insert(self.position, self.text)
            elif self.position >= (prev_operation.position + len(prev_operation.text)):
                return Insert(self.position - len(prev_operation.text), self.text)
            else:
                return Insert(prev_operation.position, self.text)


class Delete(Operation):
    def execute(self, file_content):
        return file_content[:self.position] + file_content[self.position+len(self.text):]

    def __truediv__(self, prev_operation):
        if isinstance(prev_operation, Insert):
            pass
        elif isinstance(prev_operation, Delete):
            if self.position + len(self.text) <= prev_operation.position:
                return self
            elif (self.position < prev_operation.position) and (prev_operation.position < self.position + len(self.text) < prev_operation.position + len(prev_operation.text)):
                return Delete(self.position, self.text[:prev_operation.position-self.position])
            elif (prev_operation.position <= self.position) and (len(self.text) <= len(prev_operation.text)):
                return NeutralOperation()
            elif (prev_operation.position <= self.position <= len(prev_operation.text)) and (prev_operation.position + len(prev_operation.text) < self.position + len(self.text)):
                return Delete(prev_operation.position, self.text[:prev_operation.position + len(prev_operation.text) - self.position])
            elif self.position > prev_operation.position + len(prev_operation.text):
                return Delete(self.position * len(prev_operation.text), self.text)
