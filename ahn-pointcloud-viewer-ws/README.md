AHN pointcloud viewer web service
=================================

Uses a PostGIS database to approximate number of points in selected area 
and starts a script to create a laz file of the selection.

Development
-----------


First create config file `config.yml`, use `config.yml-dist` as an example.
Se `src/main/java/nl/esciencecenter/ahn/pointcloud/db/PointCloudStore.java` for instructions to create an example PostGIS database.

Run web service:
````
./gradlew run 
````

Perform tests with test and coverage reports in `build/reports` directory.
````
./gradlew test jacocoTestReport
````

To open in an IDE like Eclipse or Intellij IDEA, create project files with `./gradlew eclipse` or `./gradlew idea` respectively.

### Manual testing

1. Create a database.
2. Create a executable to run to create laz files. For example:

````
#!/bin/bash
echo `date -Iseconds`: $@ >> ahn-slicer.log
````

3. Edit `config.yml` to set database and executable
4. Start web service `./gradlew run`
5. Test with a http client

````
virtualenv env
. env/bin/activate
pip install httpie
http -pHBhb http://localhost:8080/size left:=124932.60 bottom:=484568.840 right:=124942.60 top:=484588.840
http -pHBhb http://localhost:8080/laz left:=124932.60 bottom:=484568.840 right:=124942.60 top:=484588.840 email=someone@example.com
````

Build
-----

````
git clone git@github.com:NLeSC/ahn-pointcloud-viewer.git
cd ahn-pointcloud-viewer/server
./gradlew build
````

The distribution is in the `build/distributions` directory.

Deployment
----------

1. Unpack distribution and cd to it.
2. Create config file, use `config.yml-dist` as an example.
3. Run it

````
bin/server server config.yml
````

A web service will be started on http://localhost:8080

Generate web api documentation
------------------------------

API documentation is written in https://apiblueprint.org/ format.

API documentation can be preview with:
````
sudo npm install -g aglio
aglio -i apiary.apib -s
````

