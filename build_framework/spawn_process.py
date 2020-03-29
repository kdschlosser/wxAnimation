import sys
import subprocess
import threading
import distutils.log

# this is the component that does the legwork for spawning processes.
# The one that distutils uses does not collect output as it gets produced.
# it is a mechanism i use to buffer the output from subprocess.Popen and allows
# me to grab one line at a time as it becomes available. This eliminates any
# jumping or long pauses in information being written to the screen. This is
# far simpler then creating additional threads that monitors a queue to check
# for new information, which is what typically gets done. Those types of systems
# have to stall the queue thread between loops which leads to a not nice pleasent
# flow of information into the screen

if sys.version_info[0] > 2:
    DUMMY_RETURN = b''
    FILE_TYPES = [b'.cpp', b'.c']
else:
    DUMMY_RETURN = ''
    FILE_TYPES = ['.cpp', '.c']

COMPILERS = ['g++', 'gcc', 'clang', 'clang++', 'cc', 'c++']

if sys.platform.startswith('win'):
    SHELL = 'cmd'
else:
    SHELL = 'bash'

# this is a thread lock for printing. I use 10 threads to compile it speeds
# up the build process a lot. but we do not want to get the output all
# jumbled up so before printing anything from the output buffer we use
# this lock before we print the output buffer to stdout or stderr. we
# iterate over the output buffer line by line so if this lock is not in
# place the lines that get printed would be out of order.
print_lock = threading.Lock()


def spawn(cmd, search_path=1, level=1, cwd=None):
    if sys.platform.startswith('win'):
        if cwd is None:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
        else:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=cwd
            )

        if isinstance(cmd, (list, tuple)):
            cmd = ' '.join(cmd) + '\n'

        distutils.log.debug(cmd)

    else:
        if cwd is None:
            p = subprocess.Popen(
                SHELL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
        else:
            p = subprocess.Popen(
                SHELL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=cwd
            )

        if isinstance(cmd, (list, tuple)):
            cmd = ' '.join(cmd) + '\n'

        distutils.log.debug(cmd)
        p.stdin.write(cmd.encode('utf-8'))
        p.stdin.close()

    while p.poll() is None:
        with print_lock:
            for line in iter(p.stdout.readline, DUMMY_RETURN):
                line = line.strip()
                if line:
                    distutils.log.debug(line)

                    if sys.platform.startswith('win'):
                        for file_type in FILE_TYPES:
                            if line.endswith(file_type):
                                break
                        else:
                            continue

                        f = line
                    else:
                        continue
                    if sys.version_info[0] > 2 and sys.platform.startswith('win'):
                        new_line = b'compiling ' + f + b'...'
                        sys.stdout.write(new_line.decode('utf-8') + '\n')
                    else:
                        new_line = 'compiling ' + f + '...'
                        sys.stdout.write(new_line + '\n')

                    sys.stdout.flush()

            for line in iter(p.stderr.readline, DUMMY_RETURN):
                line = line.strip()
                if line:
                    if sys.version_info[0] > 2:
                        sys.stderr.write(line.decode('utf-8') + '\n')
                    else:
                        sys.stderr.write(line + '\n')

                    sys.stderr.flush()

    if not p.stdout.closed:
        p.stdout.close()

    if not p.stderr.closed:
        p.stderr.close()

    sys.stdout.flush()
    sys.stderr.flush()
