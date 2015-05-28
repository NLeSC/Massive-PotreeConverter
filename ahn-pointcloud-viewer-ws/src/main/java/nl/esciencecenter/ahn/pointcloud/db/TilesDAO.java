package nl.esciencecenter.ahn.pointcloud.db;

import org.skife.jdbi.v2.sqlobject.Bind;
import org.skife.jdbi.v2.sqlobject.SqlQuery;

public interface TilesDAO {
    @SqlQuery("SELECT SUM(points) " +
            "FROM tiles " +
            "WHERE the_geom && ST_SetSRID(ST_MakeBox2D(" +
            "   ST_Point(:left, :bottom)," +
            "   ST_Point(:right, :top)" +
            "), :srid)")
    Long getApproximateNumberOfPoints(@Bind("left") Double left,
                                      @Bind("bottom") Double bottom,
                                      @Bind("right") Double right,
                                      @Bind("top") Double top,
                                      @Bind("srid") int srid);
}
