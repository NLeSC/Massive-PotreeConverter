AHN pointcloud viewer web service
=================================

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