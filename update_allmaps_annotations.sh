#!/bin/bash
today=$(date +"%Y-%m-%d")
cd ~/scripts/allmaps_scripts
git pull
source ~/scripts_venv/bin/activate
python export_omo.py
rm -f annotations_unreviewed/*
rm -f annotations/*
rm -f maps/*
rm -f maps_unreviewed/*
#python create_annotations.py
python create_maps.py
git add .
git commit -m "scheduled update ${today}" .
git push
