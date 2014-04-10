==========================================
Scrutin et OpenData : parlons technique...
==========================================
----------------------------------------------------------------------------------
Un calvaire de données pour une action citoyenne :: opendata, LeMans, haum, python
----------------------------------------------------------------------------------

Ce n'est pas la première fois que je m'attaque aux données du Mans. La fois dernière, c'est les données de la SETRAM_
qui m'intéressaient, cette fois ci, il s'agit des données électorales.

Avant de commencer, sachez que tous les scripts utilisés pour cette exploitation des données sont disponibles sur un
`dépôt Github`_. Au long de cet article, nous essaierons de comprendre le fonctionnement des scripts. Sachez d'avance
qu'ils sont plus simples que ceux pour la SETRAM.

Données du Scrutin
==================

Puisque nous cherchons à analyser la dernière élection, il nous faut les données du scrutin avec la meilleure
granularité possible. Pour nous, ce sera les données du vote classées par secteur. Ces données là ne sont pas simples à
trouver (et un grand merci à feedoo_ pour le lien), elles sont sur un site qui semble dédié à ça :
http://extra.lemans.fr/elections/ .

Si vous cherchez à analyser la source de la page du `premier tour`_ en version "classique", vous serez peut être un peu
déçu... Qu'à cela ne tienne, nous allons jeter un oeil dans le seul indice que nous ayons : un script_ JS nommé
``soluvote.js`` et appelé dans la page.

Le script est un peu long (et sans grande surprise) mais certaines lignes sont intéressantes : les lignes 15, 205 et 236
notamment :

.. sourcecode:: javascript

    // ligne 15
    $.ajax({
        url: "xml/Election.xml?d=" + (new Date()).getTime(),
        // ...

    // ligne 205
    fichier = $(this).find('fichier').first().text() + ".xml";
    // ligne 236
    $.ajax({
        url: "xml/" + fichier + "?d=" + (new Date()).getTime(),
        // ...

Ces lignes nous donnent l'envie de tester l'ajout de quelques bouts de chemin à l'URL :

- l'ajout de ``/xml/`` nous permet de voir qu'il est interdit de lister les fichiers
- si on ajoute ``/xml/Election.xml`` (en laissant tomber la date mise dans le script) on arrive à un fichier XML qui
  semble être une table de correspondance entre les différents bureaux (qui sont en fait les secteurs) et les résultats
  qui leurs sont associés.
- enfin, en ajoutant ``/xml/`` et un des champs ``fichier`` du ``Election.xml``, on obtient les résultats de vote liste
  par liste pour le bureau choisi...

Reste donc à autoriser cette récupération, ce que fait le script ``scrap_scrutin.py``.

Configuration générale
----------------------

Le fichier ``config.py`` contient le nom du tour électoral d'intérêt, la liste des listes engagées au tour et la liste
des couleurs associée à chaque liste électorale (nous verrons pourquoi).

Ainsi, ``config.py`` ressemble à :

.. sourcecode:: python

    tour = 'second_tour'

    listes = {
        'premier_tour': {
            1: "LISTE D'UNION DE LA DROITE ET DU CENTRE (Alain PIGEAU)",
            2: "LUTTE OUVRIERE FAIRE ENTENDRE LE CAMP DES TRAVAILLEURS (Yves CHEÈRE)",
            3: "LE MANS RENOUVEAU CITOYEN (Ariane HENRY)",
            4: "AVEC VOUS POUR LE MANS (Christelle MORANÇAIS)",
            5: "LE MANS POUR TOUS (Jean-Claude BOULARD)",
            6: "CARTON ROUGE (Pascal LE PORT)",
            7: "LE MANS BLEU MARINE (Louis NOGUÈS)",
            8: "ALTERNATIVE PROGRESSISTE SOLIDAIRE (Michel PEZERIL)"},
        'second_tour': {
            1: "AVEC VOUS POUR LE MANS (Christelle MORANÇAIS)",
            2: "LE MANS POUR TOUS (Jean-Claude BOULARD)",
            3: "LE MANS BLEU MARINE (Louis NOGUÈS)"}
    }

    colors = {'premier_tour': {
            1: "#2E9AFE",
            2: "#FF0040",
            3: "#B40404",
            4: "#0101DF",
            5: "#FE2E9A",
            6: "#FF0000",
            7: "#08088A",
            8: "#B40431"
        },
        'second_tour' : {
            1: "#0101DF",
            2: "#FE2E9A",
            3: "#08088A",
        }
    }

Scraping
--------

Pour une fois, le scraping ne fut pas (trop) horrible : les données étaient prévues pour être exploitées par un script
et ça a facilité les choses. Ainsi, le script s'écrit simplement (``scrap_scrutin.py``):

.. sourcecode:: python

    import json

    from bs4 import BeautifulSoup
    from requests import get

    from config import tour

    base_url = 'http://extra.lemans.fr/elections/{}/xml/'.format(tour)

    # récupération de la liste des bureaux
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

Le début et la fin du script sont respectivement la récupération d'une liste des bureaux de vote et la sauvegarde des
résultats dans un fichier (mise en cache pour plus tard).

La boucle, elle, se content d'itérer sur les différents bureaux et pour chacun des bureaux de regarder les champs ``num``
d'une part (pour pouvoir les relier aux secteurs ensuite) et ``fichier`` d'autre part. Connaissant ainsi le nom du
fichier xml de résultats pour le bureau, on fait une nouvelle requête pour le récupérer et on en extrait les score de
chacun des candidats en lice. On crée alors une hashmap liant les candidats (numéro de liste uniquement) à leur score.

Emplacements des bureaux de vote
================================

Le Mans n'est pas connu pour sa brillante politique OpenData... en effet, et j'en avais déjà `disserté ici`_, les
données sont disponibles sous forme de zip, après validation d'une license et sous des URLs qui rendent la procédure pas
automatisable.

On récupère donc un fichier zip à l'adresse suivante : http://www.lemans.fr/page.do?t=2&uuid=10A48915-550EA533-1F82E3AA-D697BAF8

Après décompression on ne conserve que le fichier ``csv/BUREAUX_VOTE.csv`` et on va chercher les colonnes ``COMMUNE``,
``ADRRESSE`` et ``SECTEURS``. On redécoupe la dernière pour exporter les numéros de secteurs uniquement et on extrapole
le code postal depuis la première... Ça nous donne le script suivant :

.. sourcecode:: python


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
            if l[3] == 'Le Mans': # extrapol. du CP
                cp = 72000
            else: error_count += 1
            addr_str = "{}, {} {}, France".format(l[6],cp,l[3]) # formattage de l'addresse complète

            # transfor. du champ SECTEURS en liste
            crossref_bureaux_oldaddr[addr_str.decode('latin-1')] = [int(_) for _ in l[10].split(':')[1].split(',')]
            print(addr_str)


    print("\n\nErrors : {}".format(error_count))

    # sauvegarde des crossref
    savefile = 'data/crossref.json'
    print('Saving crossref file to {}...'.format(savefile))
    with open(savefile, 'w') as f:
        f.write(json.dumps(crossref_bureaux_oldaddr))

On exporte aussi le dictionnaire de références croisées pour l'utiliser plus tard.

Geocoding
---------

Pour pouvoir les placer sur un fond de carte, il faut ensuite convertir ces adresses postales en coordonnées GPS.
Pour cela, on utilisera le site suivant_ (merci à eux d'ailleurs, on a joyeusement poutré leur quota...).

On récupère alors un csv de la forme :

.. sourcecode:: csv

    lat;lon;adresse utilisée;adresse fournie

De ce csv, on sort les coordonées que l'on lie, via le dictionnaire de crossref aux secteurs :

.. sourcecode:: python

    import sys

    import csv
    import json

    from config import tour

    # Création d'un GeoJson propre
    #
    # Ce script fait suite à extract_OD.py, il prend les données
    # renvoyées par le geocodeur et les transforme en liste de Features
    # GeoJSOn traçables sur une map

    # fichier retourné par le geocodeur
    filename = "data/bureaux_vote_coords.csv"

    # on charge le fichier de crossref
    print('Loading crossref from data/crossref.json')
    try:
        with open('data/crossref.json') as f:
            crossref_bureaux_oldaddr = json.load(f)
    except IOError:
        print('data/crossref.json not found...\nPlease run extract_OD.py before')
        sys.exit(0)

    # lecture du CSV et création d'un GeoJSON importable
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

    # sauvegarde de la liste des bureaux de vote
    savefile = "data/bureaux_vote_coords.json"
    print('Saving GeoJSON list to {}...'.format(savefile))
    with open(savefile,'w') as f:
        f.write(json.dumps(geolist))

Lien bureau - résultats
-----------------------


Secteurs de vote
================

Aspect des données brutes
-------------------------
Partition sectorielle
---------------------
Geocoding a la mano
-------------------
Passage en GeoJSON
------------------
Tracé sur la map et export
--------------------------
Ajout de résultats et de la couleur
-----------------------------------

Et maintenant ?
===============

.. _SETRAM: article
.. _dépôt Github:
.. _feedoo: twitter
.. _premier tour: http://extra.lemans.fr/elections/premier_tour/
.. _script: http://extra.lemans.fr/elections/premier_tour/soluvote.js
.. _disserté ici: article opendata
.. _suivant: http://www.gpsfrance.net/liste-adresses-vers-coordonnees-gps
