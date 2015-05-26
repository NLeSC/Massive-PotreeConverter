package nl.esciencecenter.ahn.pointcloud.db;

import nl.esciencecenter.ahn.pointcloud.core.Selection;
import org.skife.jdbi.v2.DBI;
import org.skife.jdbi.v2.Handle;
import org.skife.jdbi.v2.util.LongMapper;

/**
 * As postgres user:
 * CREATE ROLE ahn WITH LOGIN PASSWORD '<some password>';
 * CREATE DATABASE ahn WITH OWNER ahn;
 * \c ahn
 * CREATE EXTENSION postgis;
 *
 * CREATE TABLE tiles (filename VARCHAR, geom geometry(POLYGON), points INTEGER, PRIMARY KEY (filename));
 *
 */
public class PointCloudStore {
    private final DBI jdbi;
    private int srid;

    public PointCloudStore(DBI jdbi, int srid) {
        this.jdbi = jdbi;
        this.srid = srid;
    }

    /**
     * Retrieve approximate number of points within selection.
     *
     * @param selection Selection in a pointcloud
     * @return number of points
     */
    public long getApproximateNumberOfPoints(Selection selection) {
        Handle handle = jdbi.open();
        long points = handle.createQuery("SELECT SUM(points) " +
                "FROM tiles " +
                "WHERE the_geom && ST_SetSRID(ST_MakeBox2D(" +
                "   ST_Point(:left, :bottom)," +
                "   ST_Point(:right, :top)" +
                "), :srid)")
                .bind("left", selection.getLeft())
                .bind("bottom", selection.getBottom())
                .bind("right", selection.getRight())
                .bind("top", selection.getTop())
                .bind("srid", srid)
                .map(LongMapper.FIRST)
                .first();
        handle.close();

        // TODO calculate fraction between area of requested selection and area of selected tiles
        // can be used to interpolate a better number of points
        return points;
    }

}
