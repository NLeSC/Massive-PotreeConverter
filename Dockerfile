# DockertFile for the Massive-PotreeConverter
FROM ubuntu:14.04
MAINTAINER Oscar Martinez Rubi <o.rubi@esciencecenter.nl>
RUN apt-get update -y

# Install some required packages
RUN apt-get install -y wget git cmake g++ cmake-gui cmake-curses-gui zlib1g-dev libncurses5-dev build-essential unzip
# Install GEOS, PROJ4, TIFF and GEOTIFF
RUN apt-get install -y libgeos-dev libproj-dev libtiff4-dev libgeotiff-dev
# Install Boost 1.55
RUN apt-get install -y libboost1.55-all-dev
# Install GDAL
RUN apt-get install -y libgdal-dev

# Install LASZIP
WORKDIR /opt
RUN wget http://download.osgeo.org/laszip/laszip-2.1.0.tar.gz
RUN tar xvfz laszip-2.1.0.tar.gz
WORKDIR /opt/laszip-2.1.0
RUN mkdir makefiles
WORKDIR /opt/laszip-2.1.0/makefiles/
RUN cmake ..
RUN make; make install

# Install liblas
WORKDIR /opt
RUN git clone git://github.com/libLAS/libLAS.git liblas
WORKDIR /opt/liblas/
RUN mkdir makefiles
WORKDIR /opt/liblas/makefiles/
RUN wget https://raw.githubusercontent.com/NLeSC/pointcloud-benchmark/master/install/centos7/FindPROJ4.cmake
RUN mv FindPROJ4.cmake ../cmake/modules/
RUN cmake -G "Unix Makefiles" .. -DWITH_GDAL=ON  -DWITH_GEOTIFF=ON -DWITH_LASZIP=ON -DWITH_PKGCONFIG=ON -DWITH_TESTS=ON
RUN make; make install

# Install PDAL (using commit that works)
WORKDIR /opt/
RUN git clone https://github.com/PDAL/PDAL.git PDAL-trunk
WORKDIR /opt/PDAL-trunk/
RUN git checkout d61e3db8b8e76c7c84bdefffbcf9d754df4baacf
RUN mkdir makefiles
WORKDIR /opt/PDAL-trunk/makefiles/
RUN cmake .. -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DWITH_APPS=ON -DWITH_GEOTIFF=ON -DWITH_LASZIP=ON -DWITH_TESTS=ON  -DCMAKE_CXX_FLAGS="-std=c++11 -Wl,--no-as-needed -ldl" -DCMAKE_SHARED_LINKER_FLAGS="-Wl,--no-as-needed -ldl" -DCMAKE_MODULE_LINKER_FLAGS="-Wl,--no-as-needed -ldl" -DCMAKE_EXE_LINKER_FLAGS="-Wl,--no-as-needed -ldl"  
RUN make; make install

# Install PotreeConverter
WORKDIR /opt/
RUN git clone -b develop https://github.com/potree/PotreeConverter.git
WORKDIR /opt/PotreeConverter/
RUN mkdir makefiles
WORKDIR /opt/PotreeConverter/makefiles/
RUN cmake .. -DCMAKE_BUILD_TYPE=Release 
RUN make; make install

WORKDIR /opt/
RUN wget http://www.cs.unc.edu/~isenburg/lastools/download/lastools.zip
RUN unzip lastools.zip 
WORKDIR /opt/LAStools/
RUN make
  
#Install Massive-PotreeConverter
RUN apt-get install -y python-numpy
WORKDIR /opt/
RUN git clone https://github.com/NLeSC/Massive-PotreeConverter.git

#Create links for enabled executables
RUN ln -s /opt/LAStools/bin/lasinfo /usr/local/sbin/lasinfo
RUN ln -s /opt/LAStools/bin/lasmerge /usr/local/sbin/lasmerge
    
RUN ln -s /opt/Massive-PotreeConverter/python/generate_tiles.py /usr/local/sbin/generate_tiles.py
RUN ln -s /opt/Massive-PotreeConverter/python/merge_potree.py /usr/local/sbin/merge_potree.py
RUN ln -s /opt/Massive-PotreeConverter/python/generate_potree.py /usr/local/sbin/generate_potree.py
RUN ln -s /opt/Massive-PotreeConverter/python/merge_potree_all.py /usr/local/sbin/merge_potree_all.py

RUN ldconfig

# Create 3 volumes to be used when running the script. Ideally each run must be mounted to a different physical device
VOLUME ["/data1"]
VOLUME ["/data2"]
VOLUME ["/data3"]

WORKDIR /data1
