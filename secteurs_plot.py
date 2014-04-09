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

# d'abord, on lit la liste des secteurs et on en fait un truc utilisable.
sect_filename = "data/secteurs.json"
with open(sect_filename) as f:
    tmp = json.load(f)
    map_secteurs = {int(_['properties']['name'].split(' ')[1]):_['geometry']['coordinates'] for _  in tmp['features']}

# chargement des données du vote
print('Loading poll data...')
with open('data/{}.json'.format(tour)) as f:
    bureaux = json.load(f)
    bureaux = {int(k):v for k,v in bureaux.items()}


# on crée un objet GeoJSON vide
geolist = {"type": "FeatureCollection", "features": []}

for s in map_secteurs.keys():
    new_feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': map_secteurs[s]
        },
        'properties': {
            '_storage_options': {},
            'name': 'Secteur {}'.format(s)
        }
    }

    res = bureaux[s]
    res = {int(k):int(v) for k,v in res.items()}

    # couleur du secteur
    res_sortedkeys = sorted(res, key=res.get, reverse=True)
    color = colors[tour][res_sortedkeys[0]]
    new_feature['properties']['_storage_options']['color'] = color

    # ajout du score de chacun
    for k,v in res.items():
        new_feature['properties'][listes[tour][k]] = "{} %".format(v)

    # ajout à la liste
    geolist['features'].append(new_feature)

savefile = "data/secteurs_results_{}.json".format(tour)
print('Saving to {}...'.format(savefile))
with open(savefile,'w') as f:
    f.write(json.dumps(geolist))
