# Massive-PotreeConverter
This repository extends the [PotreeConverter](https://github.com/potree/PotreeConverter) 
through a bunch of Python scripts to make it able to convert massive 
point clouds to the potree format (octree). Done for Linux environments.

For example this has been used for the dutch [AHN2](http://ahn2.pointclouds.nl) with 640 Billion points.

To convert a massive point cloud, first we split it in tiles, then we create 
potree octrees for each tile in parallel, and we finally merge them into a 
single massive octree.

In addition this repository also contains Python scripts:
 - to sort and index (with LAStools) LAS/LAZ files
 - to dump the extents of the initial (raw) LAS/LAZ files into a PostGIS database.
 - to dump the extents of a potree octree into a PostGIS database.
 - to make rectangular selections on the raw data or in the different levels of the potree octree offering a multi-level selection tool.

[![Join the chat at https://gitter.im/NLeSC/ahn-pointcloud-viewer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/NLeSC/ahn-pointcloud-viewer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Requirements

The following libraries/packages are required:

[PDAL] (http://www.pdal.io/), [PotreeConverter] (https://github.com/potree/PotreeConverter), [LAStools] (http://rapidlasso.com/lastools/) (only open source)

Python modules: numpy

IMPORTANT: For time being use this [PotreeConverter fork] (https://github.com/oscarmartinezrubiorg/PotreeConverter)

There is a Dockerfile available. See end of page.

### Optional

Optionally the extents of the different involved data (raw data and potree octree) can be dumped into a PostGIS database. Extra requirements are:

PostgreSQL, PostGIS

Python modules: psycopg2

Optionally the data can be sorted and indexed in order to have faster selection (only recommended with raw data). Extra requirements are:

LAStools closed source which requires licensing required for lassort 

## Installation

Look at the web pages of [PDAL] (http://www.pdal.io/) and [PotreeConverter] (https://github.com/potree/PotreeConverter) to install those.

Note that for closed part of LAStools wine is required. 

For the installation of LAStools, PostgreSQL, PostGIS and PDAL we recommend 
looking at the guidelines in https://github.com/NLeSC/pointcloud-benchmark/tree/master/install

When installing PotreeConverter there may be some issues if you have custom 
builds of some of the libraries. 
Look at [doc/Installing_PotreeConverter] (https://github.com/NLeSC/Massive-PotreeConverter/blob/master/doc/Installing_PotreeConverter)

Once the requirements are installed just clone this repository and add the 
Python folder contained in it into the PYTHONPATH and PATH environment variables

## Method

More detailed steps:

1- We get the bounding cube and average density of the massive point cloud. With python:
```
import utils
absPath = '/path/to/your/massive/pc'
numProc = 32 #number of processes to use for reading the input path
(_, tcount, tminx, tminy, tminz, tmaxx, tmaxy, tmaxz, _, _, _) = utils.getPCFolderDetails(absPath, numProc)
maxRange = max((tmaxx - tminx, tmaxy - tminy, tmaxz - tminz))
(minX,minY,minZ,maxX,maxY,maxZ) = (tminx, tminy, tminz, tminx + maxRange, tminy + maxRange, tminz + maxRange)
density  = float(tcount) / ((tmaxx - tminx)*(tmaxy - tminy)*(tmaxz - tminz))
print 'AABB:', minX,minY,minZ,maxX,maxY,maxZ
print '#Points:', tcount
print 'Average density:', density
```
Note that it is a cube, i.e. the axis have the same length. 
The AABB values must be used in the next steps!

2- We use `generate_tiles.py` to create tiles and we use the previous computed 
bounding box (only X and Y coordinates) in order that the generated tiles nicely
 fit with the octree structure that we are trying to create.
 
Depending on how big it is we need to use more or less number of tiles. 
It is recommended to use a number such that each tile has no more that 5 billion
 points. 
Use a number of tiles that is power of 4, in this way a thanks to the used 
bounding box, the extents of the tiles will match the extent of the OctTree 
nodes at a certain level (and thus the future merging will be done faster)

``
python /path/to/generate_tiles.py -i /path/to/input_data -o /path/to/output -t /path/to/temp_folder -e "[minX],[minY],[maxX],[maxY]" -n [number tiles] -p [number processes]
``


3- Determine a number of levels and spacing to be used by ALL the PotreeConverter executions. 
This is important that is pre-computed and always use these same values for the
individual potree executions (otherwise they can not be combined).
Use a combination of spacing (this is defined at root level) and number of 
levels such as the spacing at the deepest level is similar to the average density
 and the number of points at the root level is not more than 100K points. 
 
For example for our AHN2 massive octree we used 13 levels and a spacing of 1024 
(meters) at root level which means 1 point per square kilometer at root level. 
NL has around 40K km2 so this means around 40K points at root level and a 
spacing of 0.125 at level 13.

4- Run the individual PotreeConverters for each tile using ALWAYS the same 
previously computed AABB and the selected  spacing and number of levels. 

For this you can:
  - Use the the `generate_potree.py` script which is meant to run a in a single machine.  
  - If you run in a cluster of machines you can use scripts similar to the one 
  in the python/das folder to distribute the generation of potrees octrees in 
  different machines.

In both cases it is not recommended to use more than 8 cores per machine since 
the processing is quite IO-bound.
 
5- After the different potree octrees are created we need to merge them 
into a single one. For this you need to use the `merge_potree.py` script which 
joins two potree octrees into one. 

You need to run different iterations until there is only one potree octree
The script `merge_potree_all.py` can be used to merged all the potree octrees into one 
but this has to be used carefully. 

6- You have a single massive potree octree! Enjoy it! 
See an example in [AHN2](http://ahn2.pointclouds.nl).

For that web service also the following repositories where used:

 - https://github.com/NLeSC/ahn-pointcloud-viewer
 - https://github.com/NLeSC/ahn-pointcloud-viewer-ws

### Optional steps

7- Index and sort the raw data (we consider raw data the data before the first tiling). Use `sort_index_tiles.py'.

8- Fill a DB with the extents of the files in the raw data

``
createdb extents
psql extents -c "create extension postgis"
``


Run the `fill_db_raw.py`.

9- Fill a DB with the extents of the files in the potree octree. 
Run the `fill_db_potree.py`

After these additional steps you can make selections with level of detail selection. 
as for instance done in `create_user_file.py`.

## Docker

We have created a Dockerfile which is a Ubuntu 14.04 with the proper installations of PDAL, PotreeConverter, LAStools (open) and Massive-PotreeConverter. It is meant to help you when running the `generate_tiles.py`, `generate_potree.py`, `merge_potree.py` and `merge_potree_all.py`

Dont's know about Docker? See [Docker] (https://www.docker.com/)

In addition to installing all the required software it also creates three volumnes (/data1, /data2, /data3) which are meant to be mounted from different devices when executing docker run. Ideally always try to run in a way that the input data is in one device and the output in another (we actually have 3 volumes because of temp data)

An example of using Massive-PotreeConverter through docker:

1 - Build the Massive-PotreeConverter docker image:

`cd /path/to/Massive-PotreeConverter`

`docker build -t oscar/mpc:v1 .`

2 - Run the script to generate tiles:

``
docker run -v /home/oscar/test_drives/d1:/data1 -v /home/oscar/test_drives/d2:/data2 -v /home/oscar/test_drives/d3:/data3 oscar/mpc:v1 generate_tiles.py -i /data1/ahn_bench000020.laz -o /data2/tiles -t /data3/temp -e 85000.0,446250.0,88000.0,449250.0 -n 16 -p 1
``

3- Run the script to generate the potree octree of each tile:

``
docker run -v /home/oscar/test_drives/d1:/data1 -v /home/oscar/test_drives/d2:/data2 -v /home/oscar/test_drives/d3:/data3 oscar/mpc:v1 generate_potree.py -i /data2/tiles -o /data1/tiles_potree -f LAZ -l 8 -s 20 -e 85000.0,446250.0,-50,88000.0,449250.0,2950 -c 2
``

4 - Run the script to merge all the potree octrees into one:

``
docker run -v /home/oscar/test_drives/d1:/data1 -v /home/oscar/test_drives/d2:/data2 -v /home/oscar/test_drives/d3:/data3 oscar/mpc:v1 merge_potree_all.py -i /data1/tiles_potree -o /data1/tiles_potree_merged 
``
