package nl.esciencecenter.ahn.pointcloud.core;

import org.hibernate.validator.constraints.Range;

import javax.validation.constraints.NotNull;
import java.util.Objects;

public class Size {
    @NotNull
    @Range(min=0)
    private long points = 0;

    @NotNull
    @Range(min=0, max=24)
    private int level;

    @NotNull
    @Range(min=0, max=100)
    private double coverage;

    private Size() {
    }

    public Size(long points, int level, double coverage) {
        this.points = points;
        this.level = level;
        this.coverage = coverage;
    }

    /**
     * Number of points
     * @return
     */
    public long getPoints() {
        return points;
    }

    /**
     * Level in octree used for number of points
     *
     * @return
     */
    public int getLevel() {
        return level;
    }

    /**
     * Percent coverage based on level.
     * Highest level is 100%.
     * Each level halves the number of points.
     *
     * @return
     */
    public double getCoverage() {
        return coverage;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Size size = (Size) o;
        return Objects.equals(points, size.points) &&
                Objects.equals(level, size.level) &&
                Objects.equals(coverage, size.coverage);
    }

    @Override
    public int hashCode() {
        return Objects.hash(points, level, coverage);
    }
}
