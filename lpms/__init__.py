# Copyright 2009 - 2011 Burak Sezer <purak@hadronproject.org>
# 
# This file is part of lpms
#  
# lpms is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#   
# lpms is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#   
# You should have received a copy of the GNU General Public License
# along with lpms.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import logging
import inspect


# firstly, override this for backward compatibility
###################################################
from lpms import declarations
values = declarations.ConstantValues()
constants = values.val
del values
###################################################


def terminate(msg=None):
    if msg is not None:
        sys.stdout.write(msg+'\n')
    sys.stdout.write("quitting...\n")
    raise SystemExit(0)


def set_sandbox_paths():
    '''Set writable sandbox paths for build operation'''
    os.environ['SANDBOX_PATHS'] = ";".join(constants.sandbox_paths)


def getopt(opt, like=False):
    if like:
        for item in sys.argv:
            if item.startswith(opt):
                # FIXME: Use regex for this
                return item.split("=")[1]
        return
    if opt in sys.argv:
        return True


# FIXME-1: The following is an ungodly hack. Fuck it, remove it, re-write it!
# FIXME-2: improve this for detalied debug output.
def catch_error(err, stage=0):
    backtree = inspect.stack()
    for output in backtree: 
        if len(output[1].split("interpreter.py")) <= 1:
            continue
        for item in backtree:
            if item[-1] is None and item[-2] is None:
                sys.stdout.write("\n>> internal error:\n")
                index = backtree.index(item)+1
                sys.stdout.write(" "+item[3]+" ("+"line "+str(backtree[index][2])+")"+": "+str(err)+'\n\n')
                terminate()
    print(err)
    terminate()


def init_logging():
    logger = None
    # create lpms.log file if it does not exist
    if not os.access(constants.logfile, os.F_OK):
        f = open(constants.logfile, 'w')
        f.close()
    # initialize
    if os.access(constants.logfile, os.W_OK):
        logger = logging.getLogger(__name__)
        hdlr = logging.FileHandler(constants.logfile)
        formatter = logging.Formatter('%(created)f %(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)
    return logger


# lpms uses utf-8 encoding as default
reload(sys)
sys.setdefaultencoding('utf-8')
# initialize logging feature
logger = init_logging()
# set writable sandbox paths for various operations
set_sandbox_paths()

