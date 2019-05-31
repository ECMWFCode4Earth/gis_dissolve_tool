#!/usr/bin/env python
############################################################################
#
# MODULE:       v.ecmwf.addregion
# AUTHOR(S):    Markus Metz, mundialis
# PURPOSE:      Add a new partner region to existing partner regions
# COPYRIGHT:    (C) 2019 by the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
############################################################################

#%module
#% description: Add a new partner region to existing partner regions.
#% keyword: vector
#% keyword: import
#% keyword: OGR
#% keyword: topology
#% keyword: geometry
#% keyword: cleaning
#%end
#%option
#% key: partner_regions
#% type: string
#% required: yes
#% multiple: no
#% label: Name of OGR datasource with partner regions
#% gisprompt: old,datasource,datasource
#% guisection: Input
#%end
#%option
#% key: partner_regions_layer
#% type: string
#% required: no
#% multiple: no
#% label: OGR layer name for partner regions. 
#% description: If not given, all available layers are used
#% gisprompt: old,datasource_layer,datasource_layer
#% guisection: Input
#%end
#%option
#% key: new_partner
#% type: string
#% required: yes
#% multiple: no
#% label: Name of OGR datasource with new partner
#% gisprompt: old,datasource,datasource
#% guisection: Input
#%end
#%option
#% key: new_partner_layer
#% type: string
#% required: no
#% multiple: no
#% label: OGR layer name for new partner. 
#% description: If not given, all available layers are used
#% gisprompt: old,datasource_layer,datasource_layer
#% guisection: Input
#%end
#%option
#% key: column
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% description: Name of the column with dissemination center code
#% answer: DISS_CENTR
#% gisprompt: old,dbcolumn,dbcolumn
#% guisection: Input
#%end
#%option
#% key: output
#% type: string
#% required: yes
#% multiple: no
#% key_desc: name
#% label: Name of output OGR datasource
#% description: For example ESRI Shapefile filename or directory for storage
#% gisprompt: new,file,file
#% guisection: Output
#%end
#%option
#% key: output_layer
#% type: string
#% required: no
#% multiple: no
#% label: Name for output OGR layer.
#% description: For example: ESRI Shapefile: shapefile name
#% guisection: Output
#%end
#%option
#% key: format
#% type: string
#% required: no
#% multiple: no
#% label: Data format to write
#% description: e.g. ESRI_Shapefile,GPKG (see v.out.ogr)
#% answer: ESRI_Shapefile
#% guisection: Output
#%end


import sys
import os
import atexit
import grass.script as gscript

# initialize global vars
TMPLOC = None
GISDBASE = None
orgenv = None
switchloc = False


def cleanup():
    if switchloc:
	# switch back to original location+mapset
	gscript.run_command('g.mapset', location=orgenv['LOCATION_NAME'],
					mapset=orgenv['MAPSET'])
    # remove temp location
    if TMPLOC:
        gscript.try_rmdir(os.path.join(GISDBASE, TMPLOC))


def main():
    global TMPLOC, GISDBASE
    global orgenv, switchloc

    partner_regions = options['partner_regions']
    partner_regions_layer = options['partner_regions_layer']
    new_partner = options['new_partner']
    new_partner_layer = options['new_partner_layer']
    diss_column = options['column']
    partner_output = options['output']
    partner_output_layer = options['output_layer']
    output_format = options['format']

    orgenv = gscript.gisenv()
    GISDBASE = orgenv['GISDBASE']
    TMPLOC = 'ECMWF_temp_location_' + str(os.getpid())

    # import master polygons with v.in.ogr into new location
    kwargs = dict()
    if partner_regions_layer:
	kwargs['layer'] = partner_regions_layer
    gscript.run_command('v.in.ogr', input=partner_regions,
				    output="partner_master",
				    location=TMPLOC,
				    snap="0.1", **kwargs)
    del kwargs

    # switch to new location
    gscript.run_command('g.mapset', location=TMPLOC, mapset="PERMANENT")
    switchloc = True

    # the column diss_column must exist
    columns = gscript.read_command('v.info', map="partner_master", flags="c")

    found = False
    for line in columns.splitlines():
	colname = line.split("|", 1)[1]
	if colname == diss_column:
	    found = True

    if found is False:
	gscript.fatal("Column <%s> not found in input <%s>" % (diss_column, partner_regions))

    # import new partner polygon with v.import
    # need to snap and for this we need the extents to figure out if it is ll or metric
    # get unit with g.proj -g
    # disabled because not reliably working with GeoPackage:
    # different layers in the same GPKG can have different CRS 

    kwargs = dict()
    if new_partner_layer:
	kwargs['layer'] = new_partner_layer
    gscript.run_command('v.import', input=new_partner,
				    output="partner_new",
				    snap="-1", **kwargs)
    del kwargs

    # the column diss_column must exist
    columns = gscript.read_command('v.info', map="partner_new", flags="c")

    found = False
    for line in columns.splitlines():
	colname = line.split("|", 1)[1]
	if colname == diss_column:
	    found = True

    if found is False:
	gscript.fatal("Column <%s> not found in input <%s>" % (diss_column, new_partner))

    # combine with v.overlay with snap=0.01
    gscript.run_command('v.overlay', ainput="partner_master",
                                     atype="area",
				     binput="partner_new",
				     btype="area",
				     operator="or",
				     output="partner_master_new_1",
				     olayer="1,0,0",
				     snap="0.01")

    # now we have one master table as combination of the two original tables
    gscript.run_command('v.db.addcolumn', map="partner_master_new_1",
                                          column="%s varchar(254)" % (diss_column))

    # use DISS_CENTR from master, update DISS_CENTR from new polygon if not set in master
    gscript.run_command('v.db.update', map="partner_master_new_1",
                                       column=diss_column,
				       value="-1")

    gscript.run_command('v.db.update', map="partner_master_new_1",
                                       column=diss_column,
				       query_column="a_%s" % (diss_column),
				       where="a_%s is not null" % (diss_column))
    gscript.run_command('v.db.update', map="partner_master_new_1",
                                       col=diss_column,
				       query_column="b_%s" % (diss_column),
				       where="b_%s is not null and %s = '-1'" % (diss_column, diss_column))

    # clean up overlapping parts and small gaps
    gscript.run_command('v.clean', input="partner_master_new_1",
                                   output="partner_master_new_2",
				   tool="rmarea",
				   thresh="50000000",
				   flags="c")

    # dissolve with v.extract dissolve_column=DISS_CENTR
    # v.extract in=partner_master_new_3 out=partner_master_new_4 type=area layer=1 -d dissolve_column=DISS_CENTR
    # also reclassify
    gscript.run_command('v.dissolve', input="partner_master_new_2",
                                      output="partner_master_new_3",
				      column=diss_column)

    # TODO: how to remove larger gaps ?

    # export
    kwargs = dict()
    if partner_output_layer:
	kwargs['output_layer'] = partner_output_layer
    gscript.run_command('v.out.ogr', input="partner_master_new_3",
                                     output=partner_output,
				     type="area",
				     format=output_format,
				     flags="ms")

    return 0

if __name__ == "__main__":
    options, flags = gscript.parser()
    atexit.register(cleanup)
    sys.exit(main())
