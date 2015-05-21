package nl.esciencecenter.ahn.pointcloud.core;

import org.hibernate.validator.constraints.NotEmpty;

public class Size {
    @NotEmpty
    private long points;

    public Size(long points) {
        this.points = points;
    }
}
