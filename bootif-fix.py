#!/usr/bin/env python
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

# This script is used as a work around to fix booting issues of nodes being
# introspected. Thanks to Keith Tenzer (https://keithtenzer.com) for pointing
# out the issues and for the simple shell script. Unfortunatly the original bash
# script written by Keith was eating into my CPU resources on my small lab server.
# Tried getting inotify packages from Red Hat repos, but couldn't. Luckily
# python inotify package was available in a repo. installed it using
# yum install python-inotify

import logging
import sys
import traceback
import inotify.adapters

# The strings to be replaced in the config and pxe files in /httpboot
replace=[["--timeout 60000", ""], ["{mac", "{net0/mac"]]

# Folder path containing the images and pxe configs
httpboot="/httpboot"

_DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_LOGGER = logging.getLogger(__name__)


def _configure_logging():
    ''' Setup logging '''
    _LOGGER.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()

    formatter = logging.Formatter(_DEFAULT_LOG_FORMAT)
    ch.setFormatter(formatter)

    _LOGGER.addHandler(ch)

def inplace_change(filename, old_string, new_string):
    ''' Function to replace strings in a given file '''
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            return

    with open(filename, 'w') as f:
        _LOGGER.info('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)

def _main():
    ''' Main function watching over the httpboot folder for any changes
        in *.ipxe and config file and then immediatly replace the strings specified
        above with the workaround ones'''
    i = inotify.adapters.InotifyTree(httpboot)

    try:
        for event in i.event_gen():
            if event is not None:
                (header, type_names, watch_path, filename) = event
                if "IN_CLOSE_WRITE" in type_names:
                    if filename.endswith(".ipxe") or filename.endswith("config"):
                       _LOGGER.info("MASK->NAMES={}  FILENAME=[{}/{}]".format(type_names, watch_path, filename))
                       for r in replace:
                          inplace_change("{}/{}".format(watch_path, filename), r[0], r[1])
    except KeyboardInterrupt:
       _LOGGER.info("Keyboard interrupted")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    finally:
        _LOGGER.info("Exiting monitor")
    sys.exit(0)

if __name__ == '__main__':
    _configure_logging()
    _main()
