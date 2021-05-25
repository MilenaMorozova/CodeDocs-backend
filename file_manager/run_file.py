import threading
import uuid
import os
import sys 

import pexpect

#from .exceptions import FileDoesNotExistException

FILE_PATH = '/home/username/Code_Docs/running_files/'
DOCKER_IMAGES = {'python': 'code_docs_python'}


class RunFileThread(threading.Thread):
#class RunFileThread:
    def __init__(self, file_content, programming_language, consumer=1):
        super().__init__(name="run file")
        self.filename = self.create_file(file_content)
        self.docker_image = DOCKER_IMAGES[programming_language]
        self.consumer = consumer
        self.inputs = []

    def create_file(self, file_content):
        generated_filename = FILE_PATH + str(uuid.uuid4())

        if not os.path.exists(FILE_PATH):
            os.makedirs(FILE_PATH)

        with open(generated_filename, 'w') as file:
            file.write(file_content)

        return generated_filename

    def delete_file(self):
        try:
            os.remove(self.filename)
        except OSError:
            print("OSERROR", OSError)
#            raise FileDoesNotExistException()
        
    def add_input(file_input):
        self.inputs.append(file_input)

    def run(self) -> None:
        program = ['docker', 'run', '--mount',
                    f'type=bind,source={self.filename},destination=/root/my_file,readonly', '--rm', '-it',
                    self.docker_image]
        print('Create subprocess')
        count = 0
        command = ' '.join(program)
        child = pexpect.spawn(command, encoding='utf-8')
        # child.delaybeforesend = 0.5
        while True:
            if self.inputs:
                child.write(self.inputs.pop(0))
            output = child.read(1)
#            print(output, 'Child is alive', child.isalive())
            self.consumer.file_output(output)

            if not child.isalive() and not output:
                print("I'm NOT here")
                break
        print("EXIT CODE", child.exitstatus)
        self.consumer.send_json({'type': 'END run_file', 'exit_code': child.exitstatus})
        self.delete_file()
