package nl.esciencecenter.ahn.pointcloud.resources;

import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;

public class AbstractResource {
    protected final PointCloudStore store;
    protected final long maximumNumberOfPoints;

    public AbstractResource(PointCloudStore store, long maximumNumberOfPoints) {
        this.store = store;
        this.maximumNumberOfPoints = maximumNumberOfPoints;
    }
}
