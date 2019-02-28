import os
import getpass, logging
import argparse
import pkg_resources

ROOT = os.path.abspath((os.path.dirname(__file__)))

from .launcher import Launcher


class ReadableDirectory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        directories = values.split(';')
        valid_directories = list()

        for directory in directories:
            if not os.path.isdir(directory):
                logging.warning('ReadableDirectory:{0} is not a valid path'.format(directory))
                continue

            if os.access(directory, os.R_OK):
                valid_directories.append(directory)

            else:
                logging.warning('ReadableDirectory:{0} is not a valid path'.format(directory))

        setattr(namespace, self.dest, valid_directories)


class ReadableFilePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        file_path = values

        if not os.path.isfile(file_path):
            raise argparse.ArgumentError(self, 'ReadableFilePath:{0} is not a valid path'.format(file_path))

        if os.access(file_path, os.R_OK):
            setattr(namespace, self.dest, file_path)
        else:
            raise argparse.ArgumentError(self, 'ReadableFilePath:{0} is not a valid path'.format(file_path))


def process_args(args=None):
    parser = argparse.ArgumentParser(description="Jean-Paul Start - Cube's Launcher")
    parser.add_argument(
        '-b',
        '--batches',
        action=ReadableDirectory,
        required=True,
        help="path to batch directory"
    )
    parser.add_argument(
        '-t',
        '--tags',
        action=ReadableFilePath,
        required=True,
        help="path to tags config"
    )
    parser.add_argument(
        '-u',
        '--username',
        type=str,
        default=getpass.getuser(),
        help="username (default: current user login name)"
    )
    parse_args = parser.parse_args(args)
    return parse_args


def launch_widget(args=None, width=None, height=None, title=None, tray=True):
    args = process_args(args)

    try:
        version = pkg_resources.require("jeanpaulstart")[0].version
    except pkg_resources.DistributionNotFound:
        version = 'Not installed with pip'

    launcher = Launcher(width=width, height=height, title=title, tray=tray)
    launcher.batch_directories = args.batches
    launcher.tags_filepath = args.tags
    launcher.username = args.username
    launcher.version = version
    launcher.update()
    return launcher
