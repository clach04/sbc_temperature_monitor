#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
# Python 2 or 3


import glob
import json
import sys

import pygal


def generate_pygal_chart():
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

        # NOTE Python 3.8 needs list cast, iterator does not work
        t_chart.add(data['name'], list(zip(data['time'], data['temperature'])))

        # rock64 cpu frequency never changes, even when throttled, so not added at this time
        #t_chart.add('CPU ' + data['name'], list(zip(data['time'], data['cpu frequency'])), secondary=True)
        # TODO 'cpu frequency' https://www.pygal.org/en/stable/documentation/configuration/axis.html#secondary-range
    return t_chart



def main(argv=None):
    if argv is None:
        argv = sys.argv

    t_chart = generate_pygal_chart()
    #result = t_chart.render()
    #print(result)  # dump SVG to stdout - py2 only
    t_chart.render_to_file('chart.svg')  # py2 and py3

    return 0


if __name__ == "__main__":
    sys.exit(main())


