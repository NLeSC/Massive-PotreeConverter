# Massive-PotreeConverter
This repository extends the [PotreeConverter](https://github.com/potree/PotreeConverter)
through a bunch of Python scripts to make it able to convert massive
point clouds to the Potree-OctTree format.

Massive-PotreeConverter consists of four steps, all executable through command-line tools.
The steps to convert a massive point cloud into the Potree-OctTree are:
- Determine the bounding cube of the massive point cloud.
- Split the point cloud in tiles following a special tiling schema.
- For all the tiles run PotreeConverter to create Potree-OctTrees. We use pycoeman (https://github.com/NLeSC/pycoeman).
- Merge the multiple Potree-OctTrees into a single massive Potree-OctTree.

In order to run the four basic Massive-PotreeConverter steps we need PDAL, LAStools (only the open-source components) pycoeman and PotreeConverter.

In addition, this repository also contains tools to:
 - Sort and index a bunch of LAS/LAZ files in parallel (this requires a commercial LAStools license)
 - Dump the extents of a bunch of LAS/LAZ files into a PostGIS database. This is useful for LAStools as a pre-filter step when dealing with large number of files.
 - Dump the extents of the nodes of a Potree-OctTree into a PostGIS database. Each node of the tree is stored in a separate file.

These additional tools can be used to make rectangular selections on the raw data or in the different levels of the Potree-OctTree offering a multi-level selection tool. This is for example done in https://github.com/NLeSC/ahn-pointcloud-viewer-ws/blob/master/src/main/python/create_user_file.py. In this example a LAS/LAZ file is created from the selected data.

Massive-PotreeConverter has been used for the dutch [AHN2](http://ahn2.pointclouds.nl) with 640 Billion points.

[![Join the chat at https://gitter.im/NLeSC/ahn-pointcloud-viewer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/NLeSC/ahn-pointcloud-viewer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Requirements

The following libraries/packages are required for the basic components of Massive-PotreeConverter:

[PDAL] (http://www.pdal.io/), [PotreeConverter] (https://github.com/potree/PotreeConverter),  [pycoeman] (https://github.com/NLeSC/pycoeman) and [LAStools] (http://rapidlasso.com/lastools/) (only open-source).

For now Massive-PotreeConverter works only in Linux systems. Requires Python 3.5.

There is a Dockerfile available and a image build in [Docker Hub] (https://registry.hub.docker.com/u/oscarmartinezrubi/massive-potreeconverter/). See end of page for information on how to use it.

## Installation

Install the dependencies, i.e. PDAL, PotreeConverter, pycoeman and LAStools (only open-source for basic components but commercial license is required for the additional components).

Clone this repository and install it with pip (using a virtualenv is recommended):

```
git clone https://github.com/NLeSC/Massive-PotreeConverter
cd Massive-PotreeConverter
pip install .
```

or install directly with:

```
pip install git+https://github.com/NLeSC/Massive-PotreeConverter
```

### Installation for additional steps

In order to perform the additional components some additional libraries/packages have to be installed:

- To insert extents LAS/LAZ files a Potree-OctTrees in a PostGIS database, the additional requirements are:
  - PostgreSQL, PostGIS
  - Python modules: psycopg2

- To sort/index LAS/LAZ files in parallel (allowing faster selection), the additional requirements are:
  - LAStools with license

## Installation

Look at the web pages of [PDAL] (http://www.pdal.io/) and [PotreeConverter] (https://github.com/potree/PotreeConverter) to install those.
For PotreeConverter the develop branch is currently required.

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

1- We get the bounding cube and average density of the massive point cloud. We can use `get_info.py`. First argument is the input folder with all the input data. Second argument is the number of processes we want to use to get the information.
Note that it is a cube, i.e. the axis have the same length.
The CAABB values must be used in the next steps!
``
python /path/to/get_info.py -i /path/to/input_data -c [number processes]
``

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
python /path/to/generate_tiles.py -i /path/to/input_data -o /path/to/output -t /path/to/temp_folder -e "[minX] [minY] [maxX] [maxY]" -n [number tiles] -p [number processes]
``


3- Determine a number of levels and spacing to be used by ALL the PotreeConverter executions.
This is important that is pre-computed and always use these same values for the
individual potree executions (otherwise they can not be combined).
Use a combination of spacing (this is defined at root level) and number of
levels such as the spacing at the deepest level is similar to the average density
 and the number of points at the root level is not more than 100K points.

You can use the spreedsheet at `doc/Find_required_spacing_numlevels.ods` to
help you with that. Fill-in the extent and number of points of your point cloud. Then, try
different spacings at root level and different number of levels until you find
a combination that guarantees less than 100K points per node and spacing at the deepest level small enough
for your point density.

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

7- Index and sort the raw data (we consider raw data the data before the 2D tiling). Use `sort_index_tiles.py'.

8- Fill a DB with the extents of the files in the raw data

``
createdb extents
psql extents -c "create extension postgis"
``


Run the `fill_db_raw.py`.

9- Fill a DB with the extents of the files in the potree octree.
Run the `fill_db_potree.py`

## Docker

We have created a Dockerfile which is a Ubuntu 14.04 with the proper installations of PDAL, PotreeConverter, LAStools (open) and Massive-PotreeConverter. It is meant to help you when running the `generate_tiles.py`, `generate_potree.py`, `merge_potree.py` and `merge_potree_all.py`

Dont's know about Docker? See [Docker] (https://www.docker.com/)

There is also an image build in [Docker Hub] (https://registry.hub.docker.com/u/oscarmartinezrubi/massive-potreeconverter/) that can be directly pulled and work with!

In addition to installing all the required software it also creates three volumnes (/data1, /data2, /data3) which are meant to be mounted from different devices when executing docker run. Ideally always try to run in a way that the input data is in one device and the output in another (we actually have 3 volumes because of temp data fodler required by `generate_tiles.py` script)

An example of using Massive-PotreeConverter through docker:

1 - Build the Massive-PotreeConverter docker image from the Dockerfile in this GitHub repository:

`cd /path/to/Massive-PotreeConverter`

`docker build -t oscar/mpc:v1 .`


Or pull the image from Docker Hub:

`docker pull oscarmartinezrubi/massive-potreeconverter`


The following instructions assume that the first option was used. If you pulled the image from Docker you will need to replace the image name.

2 - Run the script to know the point cloud details, i.e. the CAABB and density:
``
docker run -v /home/oscar/test_drives/d1:/data1 oscar/mpc:v1  get_info.py -i /data1/ -c [number processes]
``

3 - Run the script to generate tiles (use the X,Y values of the CAABB computed in the previous step):

``
docker run -v /home/oscar/test_drives/d1:/data1 -v /home/oscar/test_drives/d2:/data2 -v /home/oscar/test_drives/d3:/data3 oscar/mpc:v1 generate_tiles.py -i /data1/ -o /data2/ -t /data3/ -e "[minX] [minY] [maxX] [maxY]" -n [number tiles] -p [number processes]
``

Note that we specify 3 different local folders which will be available in the docker container, one for the input data, one for the output and one for the temporal data. Also note that a local file in `/home/oscar/test_drives/d1/myfile` is accessed as `/data1/myfile` in the container.

4- Run the script to generate the potree octree of each tile (we need to use the X,Y,Z values of the CAABB computed before. You also need to compute a optimal spacing and number of levels). You can split the tiles, and run different containers in different systems with different tiles:

``
docker run -v /home/oscar/test_drives/d1:/data1 -v /home/oscar/test_drives/d2:/data2 oscar/mpc:v1 generate_potree.py -i /data2/ -o /data1/tiles_potree -f LAZ -l [number levels] -s [spacing] -e "[minX] [minY] [minZ] [maxX] [maxY] [maxZ]" -c [number processes]
``

5 - Run the script to merge all the potree octrees into one:

``
docker run -v /home/oscar/test_drives/d1:/data1 oscar/mpc:v1 merge_potree_all.py -i /data1/tiles_potree -o /data1/tiles_potree_merged
``

Note that in this case we only mount and use one volume. For this specific script it is better to have the same device for both input and output.
