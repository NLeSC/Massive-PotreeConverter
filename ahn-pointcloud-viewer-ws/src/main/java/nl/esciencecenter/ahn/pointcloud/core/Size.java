package nl.esciencecenter.ahn.pointcloud.core;

import org.hibernate.validator.constraints.NotEmpty;
import org.hibernate.validator.constraints.Range;

import java.util.Objects;

public class Size {
    @NotEmpty
    @Range(min=0)
    private long points = 0;

    private Size() {
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Size size = (Size) o;
        return Objects.equals(points, size.points);
    }

    @Override
    public int hashCode() {
        return Objects.hash(points);
    }
}
