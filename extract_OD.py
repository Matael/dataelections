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

# Extraction des données des fichiers "Opendata" du mans.
#
# On cherche à afficher toutes les addresses pour pouvoir
# ensuite les passer en bloc à un geocodeur

filename = "data/BUREAUX_VOTE.csv"

with open(filename) as f:
    reader = csv.reader(f, delimiter=";")
    reader.next()

    crossref_bureaux_oldaddr = {}
    error_count = 0
    for l in reader:
        if l[3] == 'Le Mans':
            cp = 72000
        else: error_count += 1
        addr_str = "{}, {} {}, France".format(l[6],cp,l[3])
        crossref_bureaux_oldaddr[addr_str.decode('latin-1')] = [int(_) for _ in l[10].split(':')[1].split(',')]
        print(addr_str)


print("\n\nErrors : {}".format(error_count))

# sauvegarde des crossref
savefile = 'data/crossref.json'
print('Saving crossref file to {}...'.format(savefile))
with open(savefile, 'w') as f:
    f.write(json.dumps(crossref_bureaux_oldaddr))
