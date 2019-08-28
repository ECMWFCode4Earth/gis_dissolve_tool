# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Gridpoints
                                 A QGIS plugin
 This plugin updates ECMWF grid points
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-08-26
        copyright            : (C) 2019 by mundialis
        email                : metz@mundialis.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Gridpoints class from file Gridpoints.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ecmwf_gridpoints import Gridpoints
    return Gridpoints(iface)
