# Massive PotreeConverter test run for UK LIDAR point cloud (free)
A test run of the Massive-PotreeConverter for the UK LIDAR point cloud. 
Massive-PotreeConverter consists of four steps, all executable through command-line tools.
We examine each step seperatly and skip the tiling since it loads all the input laz files into memory, which may slow the computer considerbly.
## Steps:
* Download UK laz files from the [UK survey](http://environment.data.gov.uk/ds/survey).
Each tile is divided into NW,SE,NE,SW (zipped files), and some laz files might be duplicated.
 `<laz input directory> ` should contain unique laz files.
* mkdir `<laz input directory> `
* cd `<laz input directory> `
* put laz files in `<laz input directory> `
 
* RUN 

`python3 pympc/get_info.py -i <laz input directory>`

Output contains information about suggested Potree-OctTree CAABB, spacing, number of levels and a suggeted potreeconverter command. 

For example: 
```
Average density [pts / m2]: 2.1390596605415118
Suggested number of tiles: 1. For this number of points Massive-PotreeConverter is not really required!
Suggested Potree-OctTree CAABB:  340000 130000 -1 349999 139999 9998
Suggested Potree-OctTree spacing:  41
Suggested Potree-OctTree number of levels:  7
Suggested potreeconverter command:
$(which PotreeConverter) -o <potree output directory> -l 7 -s 41 --aabb "340000 130000 -1 349999 139999 9998" --output-format   LAZ -i <laz input directory> 
```

## Option 1: run a potree for each laz seperatly in order to then merge them
* RUN (use full path for the directories)

`for d in 'ls uk_merge_rawlaz_tiles/uk_st43_flat'`


`do`


`$(which PotreeConverter) -o $<potree output directory>$d -l 7 -s 41 --aabb "340000 130000 -1 349999 139999 9998" --output-format LAZ -i $<laz input directory>$d`


`done `

* Merge the octrees: RUN 

 ` python3 pympc/merge_potree_all.py -i <potree output directory> -o <merged laz directory> `

## Visualization
* View in potree-viewer. 

*For demonstration purposes we first merged only part of the octree tiles, presented in this figure. When merging all the laz files we will get Figure 2 (see below).*

![alt tag](https://github.com/NLeSC/Massive-PotreeConverter/blob/master/data/Potree_UK_midmerge1.PNG) 

## Option 2: use PotreeConverter to build potree octree from the laz files .  
* RUN 
 
`$(which PotreeConverter) -o <output directory> -l 7 -s 41 --aabb "340000 130000 -1 349999 139999 9998" --output-format LAZ -i <laz input directory> `

## Visualization
* View in potree-viewer 

![alt tag](https://github.com/NLeSC/Massive-PotreeConverter/blob/master/data/Potree_UK1.PNG) 








