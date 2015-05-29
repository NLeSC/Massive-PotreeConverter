package nl.esciencecenter.ahn.pointcloud.db;

import nl.esciencecenter.ahn.pointcloud.core.Selection;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import nl.esciencecenter.ahn.pointcloud.exception.TooManyPoints;
import org.skife.jdbi.v2.DBI;

/**
 *
 * Create test PostGIS database with:
 * CREATE ROLE ahn WITH LOGIN PASSWORD '<some password>';
 * CREATE DATABASE ahn WITH OWNER ahn;
 * \c ahn
 * CREATE EXTENSION postgis;
 *
 * CREATE TABLE extent_raw (filepath text, tile text, level integer, numberpoints integer, geom public.geometry(Geometry, 28992));
 * CREATE TABLE extent_potree (filepath text, tile text, level integer, numberpoints integer, geom public.geometry(Geometry, 28992));
 *
 * CREATE INDEX extent_raw_geom_idx ON extent_raw USING GIST (geom);
 * CREATE INDEX extent_potree_geom_idx ON extent_potree USING GIST (geom);
 *
 * INSERT INTO extent_raw (filepath, tile, level, numberpoints, geom) VALUES ('u01cz1.laz', 'u01cz1', 13, 42132530, st_geomFromText('POLYGON((124931.360 484567.840, 124931.360 485730.400, 126241.760 485730.400, 126241.760 484567.840, 124931.360 484567.840))', 28992));
 * INSERT INTO extent_potree (filepath, tile, level, numberpoints, geom) VALUES ('r634853426428.laz', 'r634853426428', 12, 42132530, st_geomFromText('POLYGON((124931.360 484567.840, 124931.360 485730.400, 126241.760 485730.400, 126241.760 484567.840, 124931.360 484567.840))', 28992));
 *
 */
public class PointCloudStore {
    private final DBI dbi;
    private final long pointsLimit;
    private final int octreeLevels;
    private final int srid;

    public PointCloudStore(DBI dbi, int srid, long pointsLimit) {
        this.dbi = dbi;
        this.srid = srid;
        this.pointsLimit = pointsLimit;
        this.octreeLevels = dbi.onDemand(PotreeExtentsDOA.class).getMaxLevel();
    }

    /**
     * Retrieve approximate number of points within selection.
     *
     * @param selection Selection in a pointcloud
     * @return number of points
     */
    public Size getApproximateNumberOfPoints(Selection selection) throws TooManyPoints {
        RawExtentsDOA tiles = dbi.onDemand(RawExtentsDOA.class);
        long points = tiles.getApproximateNumberOfPoints(
                selection.getLeft(),
                selection.getBottom(),
                selection.getRight(),
                selection.getTop(),
                srid
                );

        // TODO calculate fraction between area of requested selection and area of selected tiles
        // can be used to interpolate a better number of points

        return new Size(points, pointsLimit, octreeLevels);
    }

}
