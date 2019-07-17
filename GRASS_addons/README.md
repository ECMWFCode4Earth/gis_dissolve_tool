GRASS addons for the GIS dissolve tool
======================================

Here are GRASS addons that are the base for QGIS plugins. The QGIS 
plugins will use exactly the same fuunctionality and workflow, but with 
a different user interface.

## How to install a GRASS addon

GRASS addons can be installed within any GRASS GIS session with 
g.extension, e.g.
```
g.extension url=/path/to/v.ecmwf.addregion
```
where `v.ecmwf.addregion` is a directory such as included here

v.ecmwf.addregion
=================

## How to run `v.ecmwf.addregion`

This GRASS addon uses as input the existing partner regions and a new 
partner region that needs to be merged with the existing partner regions.

It has a number of parameters, some are required, some are 
optional. 

Required parameters are
 * partner_regions (OGR datasource with existing partner regions)
 * new_partner (OGR datasource with new partner region)
 * output (OGR datasource with updated partner regions)

Optional parameters are
 * partner_regions_layer (OGR layer of existing partner regions to be used)  
 * new_partner_layer (OGR layer of new partner region to be used)
 * output_layer (OGR layer of updated partner regions to be created)
 * column (column to be used for dissolving, default: DISS_CENTR)
 * format (Output format to be used, default: ESRI Shapefile)

As usual, this GRASS addon must be used within a running GRASS session. 
It can be used with any GRASS location, e.g. one of the GRASS sample 
datasets.

Example usage:
```
v.ecmwf.addregion partner_regions=/path/to/efas_partner_regions_epsg3857_clean.shp \
		  new_partner=/path/to/galicia_region.shp \
		  output=/path/to/efas_partner_regions_epsg3857_v2.shp
```

v.ecmwf.gridpoints
==================

## How to run `v.ecmwf.gridpoints`

This GRASS addon uses as input hydrological grid points, the main 
basins, and the existing partner regions. The purpose is to update grid 
points with MOU IDs of existing and new partner regions.

It has a number of parameters, some are required, some are 
optional. 

Required parameters are
 * partner_regions (OGR datasource with existing partner regions)
 * basins (OGR datasource with new partner region)
 * grid_points (OGR datasource with new partner region)
 * output (OGR datasource with updated partner regions)

Optional parameters are
 * partner_regions_layer (OGR layer of existing partner regions to be used)  
 * basins_layer (OGR layer of basins to be used)
 * grid_points_layer (OGR layer of grid_points to be used)
 * partner_id (Name of the column with partner ID (default: MOU_IDS)
 * all_partner_id ame of the column with all partner IDs for grid points (default: MOUids_all)
 * output_layer (OGR layer of updated partner regions to be created)
 * format (Output format to be used, default: ESRI Shapefile)

As usual, this GRASS addon must be used within a running GRASS session. 
It can be used with any GRASS location, e.g. one of the GRASS sample 
datasets.

Example usage:
```
v.ecmwf.gridpoints partner_regions=/path/to/MOUids_EFAS_LAEA_edited_v4.shp \
		   basins=/path/to/mainbasins_EU_EFAS_LAEA_ETRS89_v2_clean.shp \
		   grid_points=/path/to/efas_river_network_named_v9.shp \
		   output=/path/to/efas_river_network_named_new.shp
```

v.ecmwf.riverbasins
===================

## How to run `v.ecmwf.gridpoints`

This GRASS addon uses as input the main basins and the existing partner 
regions. The purpose id to update basins with MOU IDs of existing and 
new partner regions.

It has a number of parameters, some are required, some are 
optional. 

Required parameters are
 * partner_regions (OGR datasource with existing partner regions)
 * basins (OGR datasource with new partner region)
 * output (OGR datasource with updated partner regions)

Optional parameters are
 * partner_regions_layer (OGR layer of existing partner regions to be used)  
 * basins_layer (OGR layer of basins to be used)
 * partner_id (Name of the column with partner ID (default: MOU_IDS)
 * all_partner_id ame of the column with all partner IDs for grid points (default: MOUids_all)
 * output_layer (OGR layer of updated partner regions to be created)
 * format (Output format to be used, default: ESRI Shapefile)

As usual, this GRASS addon must be used within a running GRASS session. 
It can be used with any GRASS location, e.g. one of the GRASS sample 
datasets.

Example usage:
```
v.ecmwf.riverbasins partner_regions=/path/to/MOUids_EFAS_LAEA_edited_v4.shp \
		    basins=/path/to/mainbasins_EU_EFAS_LAEA_ETRS89_v2_clean.shp \
		    output=/path/to/efas_river_network_named_new.shp
```
