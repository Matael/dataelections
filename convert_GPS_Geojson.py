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

import sys

import csv
import json

from config import tour

# Création d'un GeoJson propre
#
# Ce script fait suite à extract_OD.py, il prend les données
# renvoyées par le geocodeur et les transforme en liste de Features
# GeoJSOn traçables sur une map


filename = "data/bureaux_vote_coords.csv"

print('Loading crossref from data/crossref.json')
try:
    with open('data/crossref.json') as f:
        crossref_bureaux_oldaddr = json.load(f)
except IOError:
    print('data/crossref.json not found...\nPlease run extract_OD.py before')
    sys.exit(0)

geolist = []
with open(filename) as f:
    reader = csv.reader(f,delimiter=";")
    for l in reader:
        geolist.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [l[1], l[0]]
                },
                "properties": {
                    "name": "Bureau de vote",
                    "secteurs": ','.join(map(str,crossref_bureaux_oldaddr[l[3].decode('utf-8')]))
                }
            }
        )

savefile = "data/bureaux_vote_coords.json"
print('Saving GeoJSON list to {}...'.format(savefile))
with open(savefile,'w') as f:
    f.write(json.dumps(geolist))


