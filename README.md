# Massive-PotreeConverter
Convert massive point clouds, for example AHN22 (640 Billion points) to the potree format.

[![Join the chat at https://gitter.im/NLeSC/ahn-pointcloud-viewer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/NLeSC/ahn-pointcloud-viewer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This repository contains a set of tools to aid when converting a massive 
point cloud into the potree format (Octtree)


## Requirements

LAStools (only open source), PostgreSQL, PostGIS
Python modules: psycopg2, numpy

It also requires PDAL and PotreeConverter but modified versions in:
https://github.com/oscarmartinezrubi/PDAL
https://github.com/oscarmartinezrubi/PotreeConverter

The PotreeConverter modified version allows to define the bounding cube that is used when creating the OctTree
The PDAL modified version allows to use the gridder application which will divide a file into several parts according to a define grid

For the installation of LAStools, PostgreSQL, PostGIS and PDAL
look at https://github.com/NLeSC/pointcloud-benchmark/tree/master/install
For the installation of the modified PotreeConverter look at 
doc/Installing_PotreeConverter

## Installation

Once the requirements are installed just clone this repository and add the python folder contained in it in the PYTHONPATH and PATH environment variables

## Method

To convert a massive point cloud we split it in tiles, we create OctTrees for each tile in parallel and we finally merge them into a single massive OctTree.

More detailed steps:

1- We get the bounding cube and average density of the massive point cloud:
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

2- We use `generate_tiles.py` to create tiles and we use the previous computed bounding box (only X and Y coordinates) in order that the generated tiles nicely fit with the OctTree structure that we are trying to create.
Depending on how big it is we need to use more or less number of tiles. It is recommended to use a number such that each tile has no more that 5 billion points. 
Use a number of tiles that is power of 4, in this way a thanks to the used bounding box, the extents of the tiles will match the extent of the OctTree nodes at a certain level (and thus the future merging will be done faster)

3- Determine a number of levels and spacing to be used. This is important that is precomputed and always use these values for the individual Potree generations (otherwise they can not be combined).
Use a combination of spacing (at root level) and number of levels such as the spacing at the deepest level is similar to the average density.  

4- Run the individual PotreeConverters for each tile (but using the modified PotreeConverter that allows to specify the used bounding cube and use the one computed before). 
For this you can:
  - Use the the generate_potree.py script which is meant to run a in a single machine.  
  - If you run in a cluster of machines you can use scripts similar to the one in the python/das folder to distribute the generation of potrees octtrees in different machines.
 In both cases it is not recommended to use more than 8 cores per machine since there is a considerable amunt of IO.
 
5- After the different potree octrees are created we need to merge them into a sinlge one. For this you need to use the merge_potree.py script which joins to potree octtrees into one. 
You need to run different iterations until there is only one potree octree

6- You have a single massive potree octree! Enjoy it! 