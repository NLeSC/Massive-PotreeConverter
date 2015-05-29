package nl.esciencecenter.ahn.pointcloud.db;


import org.skife.jdbi.v2.sqlobject.SqlQuery;

public interface PotreeExtentsDOA {
    @SqlQuery("SELECT MAX(level) FROM extent_potree")
    int getMaxLevel();
}
