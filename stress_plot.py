#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
# Python 2 or 3


import glob
import json

import pygal


t_chart =  pygal.XY(stroke=True)
t_chart.title = 'Temperatures'
t_chart.x_title = 'Time (seconds)'
t_chart.y_title = 'Temperature (C)'
t_chart.truncate_legend = 30  # or -1 to disable

#TODO Move legend to right? not sure this is possible, move to bottom is

for filename in glob.glob('*.json'):
    #print(filename)
    file_in = open(filename)
    data = json.load(file_in)
    file_in.close()

    t_chart.add(data['name'], zip(data['time'], data['temperature']))


result = t_chart.render()

print(result)  # dump SVG to stdout

