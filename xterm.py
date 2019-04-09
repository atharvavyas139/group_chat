import os
from subprocess import Popen, PIPE
import time

PIPE_PATH = "/tmp/my_pipe"

if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)

Popen(['xterm', '-e', 'tail -f %s' % PIPE_PATH])

def print_xterm_message(message_content):
    with open(PIPE_PATH, "w") as p:
        p.write(str(message_content)+"\n")
        # time.sleep(10)