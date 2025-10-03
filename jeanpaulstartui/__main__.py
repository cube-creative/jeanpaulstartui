import sys
import os.path
import tempfile
import subprocess


if __name__ == '__main__':
    main_filepath = os.path.join(os.path.dirname(__file__), 'main.py')

    if '--save-logs' in sys.argv:
        sys.argv.remove('--save-logs')
        log_filepath = os.path.join(tempfile.gettempdir(), 'jeanpaulstart.log')
        command = [sys.executable, main_filepath] + sys.argv[1:] + ['>', log_filepath, '2>&1']

    else:
        command = [sys.executable, main_filepath] + sys.argv[1:]

    sys.exit(subprocess.call(' '.join(command), shell=True))
