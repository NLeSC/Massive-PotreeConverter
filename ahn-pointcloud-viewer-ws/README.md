AHN pointcloud viewer web service
=================================

Uses a PostGIS database to approximate number of points in selected area 
and starts a script to create a laz file of the selection.

Build
-----

````
git clone git@github.com:NLeSC/ahn-pointcloud-viewer.git
cd ahn-pointcloud-viewer/server
./gradlew build
````

The distribution is in the `build/distributions` directory.

Development
-----------

Run web service:

First create config file `config.yml`, use `config.yml-dist` as an example.
See `main/test/resources/example.sql` for example PostGIS database.

````
./gradlew run 
````

Perform tests with test and coverage reports in `build/reports` directory.
````
./gradlew test jacocoTestReport
````

Deployment
----------

1. Unpack distribution and cd to it.
2. Create config file, use `config.yml-dist` as an example.
3. Run it

````
bin/server server config.yml
````

A web service will be started on http://localhost:8080

Generate api documentation
--------------------------

API documentation is written in https://apiblueprint.org/ format.

API documentation can be previewed with:
````
sudo npm install -g aglio
aglio -i apiary.apib -s
````

