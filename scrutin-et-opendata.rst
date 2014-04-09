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

geocoding
---------
lien bureau - résultats
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
