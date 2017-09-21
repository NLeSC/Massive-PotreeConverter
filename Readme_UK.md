# Massive PotreeConverter test run for UK LIDAR point cloud (free)
A test run of the Massive-PotreeConverter for the UK LIDAR point cloud. 
Massive-PotreeConverter consists of four steps, all executable through command-line tools.
We examine each step seperatly and skip the tiling since it loads al the input laz files into memory, which may slow the computer considerbly.
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
  >Average density [pts / m2]: 2.1390596605415118
  >Suggested number of tiles: 1. For this number of points Massive-PotreeConverter is not really required!
  >Suggested Potree-OctTree CAABB:  340000 130000 -1 349999 139999 9998
  >Suggested Potree-OctTree spacing:  41
  >Suggested Potree-OctTree number of levels:  7
  >Suggested potreeconverter command:
  >$(which PotreeConverter) -o <potree output directory> -l 7 -s 41 --aabb "340000 130000 -1 349999 139999 9998" --output-format   LAZ -i <laz input directory>

## Option 1: running a potree for each laz seperatly in order to then merge them
* RUN

 `for d in 'ls uk_merge_rawlaz_tiles/uk_st43_flat'`
`do
$(which PotreeConverter) -o $PWD/uk_st43_flat_pt_ind/$d -l 7 -s 41 --aabb "340000 130000 -1 349999 139999 9998" --output-format LAZ -i $PWD/uk_merge_rawlaz_tiles/uk_st43_flat/$d
done `

* Merge the octrees. RUN 

 ` python3 pympc/merge_potree_all.py -i $PWD/uk_st43_flat_pt_ind -o uk_st43_pt_merged `

## Visualization
* view in potree-viewer [add capture2_mid_merge]

## Option 2: use PotreeConverter to build potree octree from the laz files .  

 `$(which PotreeConverter) -o $PWD/uk_st43_pt_all_flat -l 7 -s 41 --aabb "340000 130000 -1 349999 139999 9998" --output-format LAZ -i $PWD/uk_merge_rawlaz_tiles/uk_st43_flat/ `

* view in potree-viewer [add capture1]
- Copy the directory <uk_st43_flat_pt> to ~/potree/pointclouds and change the 








