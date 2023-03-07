# allmaps_scripts
Scripts to make the georeferenced UBVU digitized map collection usable with https://github.com/allmaps via IIIF.

`export_cdm_list.py` exports the relevant identifiers of all images in the CONTENTdm map collection to `cdm_export.json` using the CONTENTdm API.

`export_omo.py` uses `cdm_export.json` as input to lookup the oldmapsonline identifiers and retrieves omo metadata and georeferences using the oldmapsonline API. Data is ouput to ubvu_maps.json. 

`create_maps.py` uses `ubvu_maps.json` as input to create allmaps "map files" output to `/maps` and `/maps_unreviewed` (split according to the review status in Georeferencer). 

Note: the dimensions of the original scans used in oldmapsonline are different from the dimensions of the images in CONTENTdm, the script recalculates the cutline and ground control points to make up for the difference:
```
shrink_factor = rec['cdm']['width'] / rec['omo']['width']
```

