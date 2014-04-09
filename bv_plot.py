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

import json

from config import listes, colors, tour

print('Loading poll data...')
with open('data/{}.json'.format(tour)) as f:
    bureaux = json.load(f)
    bureaux = {int(k):v for k,v in bureaux.items()}

print('Loading coords of offices')
geo_filename = "data/bureaux_vote_coords.json"
with open(geo_filename) as f:
    geolist = json.load(f)

# ajout des résultats
for i in range(len(geolist)):
    data_files = geolist[i]['properties']['secteurs']
    results = {_+1:0 for _ in range(len(listes[tour]))}
    secteurs = map(int, data_files.split(','))

    # regroupement de plusieurs secteurs sur un bureau
    for num in secteurs:
        for k,v in bureaux[num].items(): results[int(k)] += v

    # normalisation
    for k,v in results.items():
        geolist[i]['properties'][listes[tour][k]] = "{} %".format(v/len(secteurs))

savefile = "data/bureaux_vote_results_{}.json".format(tour)
print('Saving to {}...'.format(savefile))
with open(savefile,'w') as f:
    f.write(json.dumps(geolist))
