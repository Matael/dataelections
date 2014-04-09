#!/usr/bin/env python
# -*- coding: utf8 -*-

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

from bs4 import BeautifulSoup
from requests import get

from config import tour

base_url = 'http://extra.lemans.fr/elections/{}/xml/'.format(tour)

get_liste = get('{}{}'.format(base_url,'Election.xml'))
bureaux_soup  = BeautifulSoup(get_liste.text).find_all('bureau')

bureaux = {}
for b in bureaux_soup:

    # récupération du numéro
    num = int(b.find('numero').text)
    print("Scraping office {}...".format(num))

    # récupération du fichier XML correspondant au bureau
    fichier = "{}.xml".format(b.find('fichier').text)

    # extraction des résultats
    candidats = BeautifulSoup(get("{}{}".format(base_url,fichier)).text).find_all('candidat')
    c_results = {}
    for c in candidats:
        c_results[int(c.find('intituler').text.split('-')[0])] = float(c.find('pourcentage').text.split('%')[0].replace(',','.'))

    # ajout à la liste globale
    bureaux[num] = c_results


# sauvegarde
savefile = "data/{}.json".format(tour)
print('\nSaving to : {}'.format(savefile))
with open(savefile, 'w') as f:
    f.write(json.dumps(bureaux))

print("Everything's OK... Quit.")
