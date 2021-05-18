import threading
import uuid
import os
import pexpect

FILE_PATH = '/home/username/Code_Docs/running_files/'
DOCKER_IMAGES = {'python': 'code_docs_python'}


class RunFileThread(threading.Thread):
    def __init__(self, file_content, programming_language, consumer):
        super().__init__(name="run file")
        self.filename = self.create_file(file_content)
        self.docker_image = DOCKER_IMAGES[programming_language]
        self.consumer = consumer

    def create_file(self, file_content):
        generated_filename = FILE_PATH + str(uuid.uuid4())

        if not os.path.exists(FILE_PATH):
            os.makedirs(FILE_PATH)

        with open(generated_filename, 'w') as file:
            file.write(file_content)

        return generated_filename

    def run(self) -> None:
        program = ['docker', 'run', '--mount',
                    f'type=bind,source={self.filename},destination=/root/my_file,readonly', '--rm', '-it',
                    self.docker_image]
        print('Create subprocess')

        command = ' '.join(program)
        child = pexpect.spawn(command, encoding='utf-8')
        # child.delaybeforesend = 0.5
        while True:
            output = child.readline()
            print(output, 'Child is alive', child.isalive())
            self.consumer.file_output(output)

            if child.isalive() and not output:
                print("I'm here")

            if not child.isalive() and not output:
                print("I'm NOT here")
                break
