import threading
import uuid
import os

import pexpect

FILE_PATH = '/home/username/Code_Docs/running_files/'
DOCKER_IMAGES = {'python': 'code_docs_python'}


class RunFileThread(threading.Thread):
    def __init__(self, file_content, programming_language, consumer=1):
        super().__init__(name="run file")
        self.filename = self.create_file(file_content)
        self.docker_image = DOCKER_IMAGES[programming_language]
        self.consumer = consumer
        self.inputs = []
        self.__close_force = False

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
            pass
        
    def add_input(self, file_input):
        self.inputs.append(file_input)

    def run(self) -> None:
        program = ['docker', 'run', '--mount',
                    f'type=bind,source={self.filename},destination=/root/my_file,readonly', '--rm', '-it',
                    self.docker_image]
        print('Create subprocess')
        command = ' '.join(program)
        child = pexpect.spawn(command, encoding='utf-8')

        try:
            while True:
                # force process to stop
                if self.__close_force:
                    child.close(force=True)
                    break

                if self.inputs:
                    child.write(self.inputs.pop(0))

                output = child.read(1)
                self.consumer.file_output(output)

                if not child.isalive() and not output:
                    break
        except pexpect.EOF:
            self.consumer.file_output("Nothing for reading")
            child.close(force=True)
        except pexpect.TIMEOUT:
            self.consumer.file_output("Your time is over")
            child.close(force=True)
        print("EXIT CODE", child.exitstatus)
        self.consumer.send_json({'type': 'END run_file', 'exit_code': child.exitstatus})
        self.consumer.launched_file_manager.remove_stopped_file(self.consumer.file.pk)
        self.delete_file()

    def close(self):
        self.__close_force = True
