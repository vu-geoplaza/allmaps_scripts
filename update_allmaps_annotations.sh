#!/bin/bash
cd ~/allmaps_scripts
git pull
source ~/geo_venv/bin/activate
python export_omo.py
rm -f annotations_unreviewed/*
python create_annotations.py
git add .
git commit -m 'scheduled update' .
git push
