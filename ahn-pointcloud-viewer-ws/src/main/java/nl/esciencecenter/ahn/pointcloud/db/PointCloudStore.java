package nl.esciencecenter.ahn.pointcloud.db;

import nl.esciencecenter.ahn.pointcloud.core.Selection;
import org.skife.jdbi.v2.DBI;

/**
 *
 * Create test PostGIS database with:
 * CREATE ROLE ahn WITH LOGIN PASSWORD '<some password>';
 * CREATE DATABASE ahn WITH OWNER ahn;
 * \c ahn
 * CREATE EXTENSION postgis;
 *
 * CREATE TABLE tiles (
 *  filename VARCHAR PRIMARY KEY,
 * points INT,
 * the_geom GEOMETRY(POLYGON, 28992)
 * );
 * CREATE INDEX tiles_the_geom_idx ON tiles USING GIST (the_geom);
 *
 * INSERT INTO tiles (filename, points, the_geom) VALUES ('u01cz1.laz', 42132530, st_geomFromText('POLYGON((124931.360 484567.840, 124931.360 485730.400, 126241.760 485730.400, 126241.760 484567.840, 124931.360 484567.840))', 28992));
 *
 */
public class PointCloudStore {
    private final DBI dbi;
    private int srid;

    public PointCloudStore(DBI dbi, int srid) {
        this.dbi = dbi;
        this.srid = srid;
    }

    /**
     * Retrieve approximate number of points within selection.
     *
     * @param selection Selection in a pointcloud
     * @return number of points
     */
    public long getApproximateNumberOfPoints(Selection selection) {
        TilesDAO tiles = dbi.onDemand(TilesDAO.class);
        long points = tiles.getApproximateNumberOfPoints(
                selection.getLeft(),
                selection.getBottom(),
                selection.getRight(),
                selection.getTop(),
                srid
                );

        // TODO calculate fraction between area of requested selection and area of selected tiles
        // can be used to interpolate a better number of points

        // see ../python/db_tiles.py for table structure
        // points/maxpoints = k
        // k <1 use raw data
        // k > use potree level, level = maxLevels-(k-1)
        // coverage = 100/2^(k-1)
        return points;
    }

}
