# Copyright 1996-2023 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes
import os
import sys

if sys.platform == 'linux' or sys.platform == 'linux2':
    path = os.path.join('lib', 'controller', 'libController.so')
elif sys.platform == 'win32':
    path = os.path.join('lib', 'controller', 'Controller.dll')
elif sys.platform == 'darwin':
    path = os.path.join('Contents', 'lib', 'controller', 'libController.dylib')


def _controller_lib_dir():
    """Return the directory holding the controller library.

    Prefer the location of this file over the WEBOTS_HOME environment
    variable.  Webots passes WEBOTS_HOME to controller processes, and on
    Windows systems whose install path contains non-ASCII characters
    (e.g. Chinese folder names) the value can arrive double-encoded
    (UTF-8 bytes decoded with the local code page), so the library path
    below would point to a non-existent file and every controller would
    die at start-up.  Deriving the directory from __file__ is always
    correct; the environment variable is only a fallback.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.normpath(os.path.join(here, '..', '..'))
    if os.path.exists(os.path.join(candidate, os.path.basename(path))):
        return candidate
    home = os.environ.get('WEBOTS_HOME', '')
    if not os.path.isdir(home):
        # Try to undo a UTF-8 -> local code page double encoding.
        for encoding in ('gbk', 'mbcs', 'latin-1'):
            try:
                fixed = home.encode(encoding).decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if os.path.isdir(fixed):
                return os.path.join(fixed, os.path.dirname(path))
    return os.path.join(home, os.path.dirname(path))


lib_dir = _controller_lib_dir()

wb = ctypes.cdll.LoadLibrary(os.path.join(lib_dir, os.path.basename(path)))

if sys.platform == 'win32':
    ctypes.cdll.LoadLibrary(os.path.join(lib_dir, 'generic_robot_window.dll'))