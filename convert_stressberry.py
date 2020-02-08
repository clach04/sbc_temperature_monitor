#!/usr/bin/env python3
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
# NOTE use py3 - py2 will do odd uniode namespace in key names in yaml output
# Python 2 or 3

import glob
import json
import os
import os.path
import sys

import yaml

def json2yaml(file_in, file_out):
    data = json.load(file_in)
    yaml.dump(data, file_out)

def yaml2json(file_in, file_out):
    data = yaml.load(file_in, Loader=yaml.SafeLoader)
    json.dump(data, file_out)

def y2j(filename_in, filename_out):
    file_in = open(filename_in)
    file_out = open(filename_out, 'w')

    # TODO sniff first line for a comment
    yaml2json(file_in, file_out)

    file_out.close()
    file_in.close()

def j2y(filename_in, filename_out):
    file_in = open(filename_in)
    file_out = open(filename_out, 'w')

    # TODO see if there is a "comment" field and emit that as yaml comment first line
    json2yaml(file_in, file_out)

    file_out.close()
    file_in.close()

#y2j('pi3.dat', 'pi3.json')
#j2y('rock64.json', 'rock64.yaml')


def j2y_one(filename):
    print(filename)
    print(os.path.splitext(filename)[0])
    filename_no_ext = os.path.splitext(filename)[0]
    print(filename_no_ext + '.yaml')
    filename_yaml = filename_no_ext + '.yaml'
    j2y(filename, filename_yaml)

"""
argv = sys.argv
filename = argv[1]
j2y_one(filename)
"""

for filename in glob.glob('*.json'):
    j2y_one(filename)

