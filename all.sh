#! /bin/bash

echo 'Récupération des données de vote en ligne...'
./scrap_scrutin.py
echo 'Tracé en secteurs...'
./secteurs_plot.py
echo 'Tracé en bureaux...'
./bv_plot.py

