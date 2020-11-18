import fileinput
from pathlib import PurePosixPath

if __name__ == '__main__':
    RUN_KEYS = PurePosixPath('/home/agrodroid/app/versions/current/package/config/navigator/run_keys.txt')
    for line in fileinput.FileInput(str(RUN_KEYS), inplace=1):
        if 'consoleMode ' in line:
            line = line.replace('true ', 'false')
        else:
            line = line
        print(line, end='')
