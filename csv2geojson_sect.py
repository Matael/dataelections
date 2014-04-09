#! /usr/bin/env python
# -*- coding:utf8 -*-

# Copyright 2014 Mathieu (matael) Gaborit <mathieu@matael.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
