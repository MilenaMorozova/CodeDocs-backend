import threading
import uuid
import os
import subprocess

FILE_PATH = '/home/username/Code_Docs/running_files/'
DOCKER_IMAGES = {'python': 'princesska/python',
                 'js': 'princesska/js'}


class RunFileThread(threading.Thread):
    def __init__(self, file_content, programming_language):
        super().__init__(name="run file")
        self.filename = self.create_file(file_content)
        self.docker_image = DOCKER_IMAGES[programming_language]

    def create_file(self, file_content):
        generated_filename = FILE_PATH + str(uuid.uuid4())

        if not os.path.exists(FILE_PATH):
            os.makedirs(FILE_PATH)

        with open(generated_filename, 'w') as file:
            file.write(file_content)

        return generated_filename

    def run(self) -> None:
        program = f'docker run ' \
                  f'--mount type=bind,source={self.filename},destination=/root/my_file,readonly {self.docker_image}'
        process = subprocess.Popen(program)
        code = process.wait()

        print(code)
