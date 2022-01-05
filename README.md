# allmaps_scripts
Scripts to make the georeferenced UBVU digitized map collection usable with https://github.com/allmaps via IIIF.

`export_cdm_list.py` exports the relevant identifiers of all images in the CONTENTdm map collection to `cdm_export.json` using the CONTENTdm API.

`export_omo.py` uses `cdm_export.json` as input to lookup the oldmapsonline identifiers and retrieves omo metadata and georeferences using the oldmapsonline API. Data is ouput to ubvu_maps.json. 

`create_annotations.py` uses `ubvu_maps.json` as input to create allmaps json annotations output to `/annotations` and `/annotations_unreviewed` (split according to the review status in Georeferencer). 

Note: the dimensions of the original scans used in oldmapsonline are different from the dimensions of the images in CONTENTdm, the script recalculates the cutline and ground control points to make up for the difference:
```
shrink_factor = rec['cdm']['width'] / rec['omo']['width']
```

Test by using the raw url to a json annotation (for example https://raw.githubusercontent.com/vu-geoplaza/allmaps_scripts/main/annotations/ubvu_114.json) in the allmaps viewer (https://viewer.allmaps.org):

- https://viewer.allmaps.org/#data=data%3Atext%2Fx-url%2C+https%3A%2F%2Fraw.githubusercontent.com%2Fvu-geoplaza%2Fallmaps_scripts%2Fmain%2Fannotations%2Fubvu_114.json
- https://viewer.allmaps.org/#data=data%3Atext%2Fx-url%2C+https%3A%2F%2Fraw.githubusercontent.com%2Fvu-geoplaza%2Fallmaps_scripts%2Fmain%2Fannotations%2Fubvu_2450.json
- https://viewer.allmaps.org/#data=data%3Atext%2Fx-url%2C+https%3A%2F%2Fraw.githubusercontent.com%2Fvu-geoplaza%2Fallmaps_scripts%2Fmain%2Fannotations%2Fubvu_7242.json
- https://viewer.allmaps.org/#data=data%3Atext%2Fx-url%2C+https%3A%2F%2Fraw.githubusercontent.com%2Fvu-geoplaza%2Fallmaps_scripts%2Fmain%2Fannotations%2Fubvu_254.json
