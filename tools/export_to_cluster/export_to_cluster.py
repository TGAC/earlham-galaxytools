#!/usr/bin/env python
from __future__ import print_function

import optparse
import os
import os.path
import re
import shutil
import sys

parser = optparse.OptionParser()
parser.add_option('-d', '--export_dir', help='Directory where to export the datasets')
parser.add_option('-p', '--dir_prefix', help='How the export dir should start')
(options, args) = parser.parse_args()
if not options.export_dir:
    parser.error('Export directory cannot be empty')
if not options.dir_prefix:
    parser.error('Directory prefix cannot be empty')
if len(args) < 3:
    parser.error('Require at least two arguments')
if len(args) % 3 != 0:
    parser.error('Require an even number of arguments')

real_export_dir = os.path.realpath(options.export_dir)
dir_prefix = options.dir_prefix.rstrip(os.sep)
if not real_export_dir.startswith(dir_prefix):
    raise Exception("'%s' must be a subdirectory of '%s'" % (options.export_dir, dir_prefix))
if not os.path.exists(real_export_dir):
    raise Exception("'%s' directory does not exist or it is not accessible by the Galaxy user" % options.export_dir)
if not os.path.isdir(real_export_dir):
    raise Exception("'%s' is not a directory" % options.export_dir)

dataset_paths = args[::3]
dataset_names = args[1::3]
dataset_exts = args[2::3]
exit_code = 0
for dp, dn, de in zip(dataset_paths, dataset_names, dataset_exts):
    """
    Copied from get_valid_filename from django
    https://github.com/django/django/blob/main/django/utils/text.py
    """
    dn_de = "%s.%s" % (dn, de)
    dn_de_safe = re.sub(r'(?u)[^-\w.]', '', dn_de.strip().replace(' ', '_'))
    dest = os.path.join(real_export_dir, dn_de_safe)
    try:
        shutil.copy2(dp, dest)
        print("Dataset '%s' copied to '%s'" % (dn, dest))
    except Exception as e:
        msg = "Error copying dataset '%s' to '%s', %s" % (dn, dest, e)
        print(msg, file=sys.stderr)
        exit_code = 1
sys.exit(exit_code)
