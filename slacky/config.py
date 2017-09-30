from __future__ import print_function

import os
import sys

from collections import namedtuple
from ConfigParser import SafeConfigParser

config = namedtuple('Config', 'token')


def read_config(config_file):
    if not os.path.isfile(config_file):
	print('File {} not found.'.format(config_file), file=sys.stderr)
	sys.exit(1)
    parser = SafeConfigParser()
    parser.read(config_file)
    token = parser.get('slacky', 'token')
    return config(token=token)


if __name__ == '__main__':
    print(read_config('config.ini.example'))
