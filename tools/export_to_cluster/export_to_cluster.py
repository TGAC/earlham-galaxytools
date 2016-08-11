#!/usr/bin/env python
from __future__ import print_function

import optparse
import os
import os.path
import shutil
import sys
import re

parser = optparse.OptionParser()
parser.add_option('-d', '--export_dir', help='Directory where to export the datasets')
parser.add_option('-p', '--dir_prefix', help='How the export dir should start')
(options, args) = parser.parse_args()
if not options.export_dir:
    parser.error('Export directory cannot be empty')
if not options.dir_prefix:
    parser.error('Directory prefix cannot be empty')
if len(args) < 2:
    parser.error('Require at least two arguments')
if len(args) % 2 != 0:
    parser.error('Require an even number of arguments')

real_export_dir = os.path.realpath(options.export_dir)
dir_prefix = options.dir_prefix.rstrip(os.sep)
if not real_export_dir.startswith(dir_prefix):
    sys.exit("%s must be a subdirectory of %s" % (options.export_dir, dir_prefix))
if not os.path.exists(real_export_dir):
    sys.exit("%s does not exist or it is not accessible by the Galaxy user" % options.export_dir)
if not os.path.isdir(real_export_dir):
    sys.exit("%s is not a directory" % options.export_dir)

dataset_paths = args[::2]
dataset_names = args[1::2]
for dp, dn in zip(dataset_paths, dataset_names):
    """
    Copied from get_valid_filename from django
    https://github.com/django/django/blob/master/django/utils/text.py
    """
    dn_safe = dn.strip().replace(' ', '_')
    dn_safe = re.sub(r'(?u)[^-\w.]', '', dn_safe)
    dest = os.path.join(real_export_dir, dn_safe)
    try:
        shutil.copy2(dp, dest)
        print("'%s' copied to '%s'" % (dn, dest))
    except Exception as e:
        msg = "Error copying '%s' to '%s', %s" % (dn, dest, e)
        print(msg)
        sys.stderr.write(msg)
