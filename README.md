# Massive-PotreeConverter
Convert massive pointclouds, for example ahn2 (640 Billion points) to the potree format.

[![Join the chat at https://gitter.im/NLeSC/ahn-pointcloud-viewer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/NLeSC/ahn-pointcloud-viewer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This repository contains a set of tools to aid when converting a massive 
point cloud into the potree format (Octtree)


## Requirements

liblas, GDAL, LAStools (only open source), PostgreSQL, PostGIS

Python modules: psycopg2, numpy, liblas, GDAL

It also requires PDAL and PotreeConverter but modified versions in:
https://github.com/oscarmartinezrubi/PDAL
https://github.com/oscarmartinezrubi/PotreeConverter

For the installation of liblas, GDAL, LAStools, PostgreSQL, PostGIS and PDAL
look at https://github.com/NLeSC/pointcloud-benchmark/tree/master/install
For the installation of the modified PotreeConverter look at 
doc/Installing_PotreeConverter