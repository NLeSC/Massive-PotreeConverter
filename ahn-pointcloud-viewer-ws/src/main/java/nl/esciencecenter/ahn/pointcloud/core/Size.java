package nl.esciencecenter.ahn.pointcloud.core;

import org.hibernate.validator.constraints.NotEmpty;
import org.hibernate.validator.constraints.Range;

public class Size {
    @NotEmpty
    @Range(min=0)
    private long points = 0;

    public Size() {
    }

    public Size(long points) {
        this.points = points;
    }

    public void setPoints(long points) {
        this.points = points;
    }

    public long getPoints() {
        return points;
    }
}
