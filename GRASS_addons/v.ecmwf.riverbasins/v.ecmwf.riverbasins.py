#!/usr/bin/env python
############################################################################
#
# MODULE:       v.ecmwf.riverbasins
# AUTHOR(S):    Markus Metz, mundialis
# PURPOSE:      Update basns with MOU_IDS of all partner regions
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
#% description: Update grid points with MOU_IDS of all partner regions.
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
#% key: partner_id
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% description: Name of the column with partner ID (default: MOU_IDS)
#% answer: MOU_IDS
#% gisprompt: old,dbcolumn,dbcolumn
#% guisection: Input
#%end
#%option
#% key: basins
#% type: string
#% required: yes
#% multiple: no
#% label: Name of OGR datasource with basins
#% gisprompt: old,datasource,datasource
#% guisection: Input
#%end
#%option
#% key: basins_layer
#% type: string
#% required: no
#% multiple: no
#% label: OGR layer name for basins. 
#% description: If not given, all available layers are used
#% gisprompt: old,datasource_layer,datasource_layer
#% guisection: Input
#%end
#%option
#% key: all_partner_id
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% description: Name of the column with all partner IDs for basins (default: MOUids_all)
#% answer: MOUids_all
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
#% description: For example: ESRI Shapefile name without suffix
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
    partner_id_column = options['partner_id']

    basins = options['basins']
    basins_layer = options['basins_layer']
    all_partner_id_column = options['all_partner_id']

    output = options['output']
    output_layer = options['output_layer']
    output_format = options['format']

    orgenv = gscript.gisenv()
    GISDBASE = orgenv['GISDBASE']
    TMPLOC = 'ECMWF_temp_location_' + str(os.getpid())

    # import basins with v.in.ogr into new location
    # need to snap, assume units are meters !!!
    kwargs = dict()
    if basins_layer:
	kwargs['layer'] = basins_layer
    gscript.run_command('v.in.ogr', input=basins,
				    output="basins",
				    location=TMPLOC,
				    snap="10", **kwargs)
    del kwargs

    # switch to new location
    gscript.run_command('g.mapset', location=TMPLOC, mapset="PERMANENT")
    switchloc = True

    # check if we have an attribute table
    dbinfo = gscript.vector_db("basins")
    if 1 not in dbinfo.keys():
	# add new table 
	gscript.run_command('v.db.addtable', map="basins")
	dbinfo = gscript.vector_db("basins")

    # check if the column all_partner_id_column exists
    columns = gscript.read_command('v.info', map="basins", flags="c")

    found = False
    for line in columns.splitlines():
	colname = line.split("|", 1)[1]
	if colname == all_partner_id_column:
	    found = True

    if found is False:
	# add column
	gscript.run_command('v.db.addcolumn', map="basins",
	                                      column="%s varchar(255)" % (all_partner_id_column))
    else:
	# clear column entries
	table = dbinfo[1]['table']
	database = dbinfo[1]['database']
	driver = dbinfo[1]['driver']
	sqlcmd = "UPDATE %s SET %s = NULL" % (table, all_partner_id_column)
	gscript.write_command('db.execute', input='-', database=database, driver=driver, stdin=sqlcmd)

    # import all partner polygons with v.import
    # need to snap, assume units are meters !!!

    kwargs = dict()
    if partner_regions_layer:
	kwargs['layer'] = partner_regions_layer
    gscript.run_command('v.import', input=partner_regions,
				    output="partner_regions_1",
				    snap="0.01", **kwargs)
    del kwargs

    # the column partner_id_column must exist
    columns = gscript.read_command('v.info', map="partner_regions_1", flags="c")

    found = False
    for line in columns.splitlines():
	colname = line.split("|", 1)[1]
	if colname == partner_id_column:
	    found = True

    if found is False:
	gscript.fatal("Column <%s> not found in input <%s>" % (partner_id_column, partner_regions))


    # clean partner regions
    # clean up overlapping parts and gaps smaller mingapsize 
    mingapsize=10000000
    gscript.run_command('v.clean', input="partner_regions_1",
                                   output="partner_regions_2",
				   tool="rmarea",
				   thresh=mingapsize,
				   flags="c")

    # combine basins and partner regions with v.overlay with snap=0.01
    gscript.run_command('v.overlay', ainput="basins",
                                     atype="area",
				     binput="partner_regions_2",
				     btype="area",
				     operator="and",
				     output="basins_partners",
				     olayer="1,0,0",
				     snap="0.01")


    # select all basin cats from basins
    basincats = gscript.read_command('v.db.select', map="basins",
                                                    column="cat",
						    flags="c")

    basincatsint = [int(c) for c in basincats.splitlines()]
    basincatsint = sorted(set(basincatsint))
    
    # loop over basin cats
    gscript.message(_("Updating %d basins with partner region IDs, this can take some time..") % (len(basincatsint)))
    for bcat in basincatsint:

	# for each basin cat, select all partner ids from the overlay
	pcats = gscript.read_command('v.db.select', map="basins_partners",
                                                    column="b_%s" % (partner_id_column),
						    where="a_cat = %d" % (bcat),
						    flags="c")

	# create comma-separated list and upload to grid points, 
	# column all_partner_id_column
	if len(pcats) > 0:
	    pcatlist = []
	    for c in pcats.splitlines():
		# the MOU_IDS column can already contain a comma-separated list of IDs
		for cc in c.split(','):
		    pcatlist.append(int(cc))
	    
	    pcatlist = sorted(set(pcatlist))
	    pcatstring = ','.join(str(c) for c in pcatlist)
	    gscript.run_command('v.db.update', map="basins",
					       column=all_partner_id_column,
					       value=pcatstring,
					       where="cat = %d" % (bcat),
					       quiet=True)



    # export updated basins
    kwargs = dict()
    if output_layer:
	kwargs['output_layer'] = output_layer
    gscript.run_command('v.out.ogr', input="basins",
                                     output=output,
				     type="area",
				     format=output_format,
				     flags="sm", **kwargs)
    del kwargs

    return 0

if __name__ == "__main__":
    options, flags = gscript.parser()
    atexit.register(cleanup)
    sys.exit(main())
