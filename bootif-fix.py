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
import pyinotify

replace=[["{mac", "{net0/mac"]]
path="/httpboot"

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CREATE

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

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if event.pathname.endswith(".ipxe") or event.pathname.endswith("config"):
            for r in replace:
               inplace_change("{}".format(event.pathname), r[0], r[1])
               
def _main():
    for r in replace:
       inplace_change("{}/inspector.ipxe".format(path), r[0], r[1])
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(path, mask, rec=True)

    notifier.loop()

if __name__ == '__main__':
    _configure_logging()
    _main()
