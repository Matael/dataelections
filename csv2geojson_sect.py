#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# csv2geojson_sect.py
#
# Copyright © 2014 Mathieu Gaborit (matael) <mathieu@matael.org>
#
#
# Distributed under WTFPL terms
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

"""

"""


import csv
import json

import sys
import os

def proceed(filename, savefile):

    geo_sect = []
    with open(filename) as f:
        reader = csv.reader(f, delimiter=";")

        for l in reader:
            geo_sect.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [l[1], l[0]]
                },
                "properties": {
                    "filename": filename,
                    "street": l[3]
                }
            })

    with open(savefile,'w') as f:
        f.write(json.dumps(geo_sect))


def main():

    if len(sys.argv) != 3:
        print("Usage : ./csv2geojson_sect in out")
        sys.exit()
    else:
        filename = sys.argv[1]
        savefile = sys.argv[2]
        if not os.path.exists(filename):
            print("File {} doesn't exist. Quitting...".format(filename))
            sys.exit()
        if os.path.exists(savefile):
            print("File {} does exist. Continue ? [y/N]".format(savefile))
            answer = input()
            if answer.lower() == 'y':
                proceed(filename,savefile)
            else:
                print("Aborting...")
                sys.exit()
        else:
            proceed(filename,savefile)

if __name__=='__main__': main()
