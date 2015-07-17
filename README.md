# Massive-PotreeConverter
This repository extends the [PotreeConverter](https://github.com/potree/PotreeConverter) 
to make it able to convert massive point clouds to the potree format (octree).

For example [AHN2](http://ahn2.pointclouds.nl) with 640 Billion points.

[![Join the chat at https://gitter.im/NLeSC/ahn-pointcloud-viewer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/NLeSC/ahn-pointcloud-viewer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Requirements

LAStools (only open source), PostgreSQL, PostGIS, PDAL
Python modules: psycopg2, numpy

It also requires PotreeConverter but modified a version in:
https://github.com/oscarmartinezrubi/PotreeConverter

The PotreeConverter modified version allows to define the bounding cube that is used when creating the octree

For the installation of LAStools, PostgreSQL, PostGIS and PDAL
look at https://github.com/NLeSC/pointcloud-benchmark/tree/master/install
For the installation of the modified PotreeConverter look at 
doc/Installing_PotreeConverter

## Installation

Once the requirements are installed just clone this repository and add the python folder contained in it in the PYTHONPATH and PATH environment variables

## Method

To convert a massive point cloud we split it in tiles, we create octrees for each tile in parallel and we finally merge them into a single massive octree.

More detailed steps:

1- We get the bounding cube and average density of the massive point cloud. With python:
```
import utils
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
individual Potree executions (otherwise they can not be combined).
Use a combination of spacing (this is defined at root level) and number of 
levels such as the spacing at the deepest level is similar to the average density
 and the number of points at the root level is not more than 100K points. 
 
For example for our AHN2 massive octree we used 13 levels and a spacing of 1024 
(meters) at root level which means 1 point per square kilometer at root level. 
NL has around 40K km2 so this means around 40K points at root level and a 
spacing of 0.125 at level 13.

4- Run the individual PotreeConverters for each tile (but using the modified PotreeConverter that allows to specify the used bounding cube and use the one computed before). 
For this you can:
  - Use the the generate_potree.py script which is meant to run a in a single machine.  
  - If you run in a cluster of machines you can use scripts similar to the one in the python/das folder to distribute the generation of potrees octrees in different machines.
 In both cases it is not recommended to use more than 8 cores per machine since there the processing is quite IO-bound.
 
5- After the different potree octrees are created we need to merge them into a sinlge one. For this you need to use the merge_potree.py script which joins to potree octrees into one. 
You need to run different iterations until there is only one potree octree

6- You have a single massive potree octree! Enjoy it! 