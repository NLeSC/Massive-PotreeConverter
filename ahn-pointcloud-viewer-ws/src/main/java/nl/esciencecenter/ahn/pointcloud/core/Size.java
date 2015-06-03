package nl.esciencecenter.ahn.pointcloud.core;

import nl.esciencecenter.ahn.pointcloud.exception.TooManyPoints;
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
     * Contruct size object based on points and limits.
     *
     * @param points Number of points based on raw extents
     * @param pointsLimit Maximum number of points (based on raw extents) allowed
     * @param octreeLevels Number of levels of the Potree octree.
     * @throws TooManyPoints
     */
    public Size(long points, long pointsLimit, int octreeLevels) throws TooManyPoints {
        this.points = points;

        // see ../python/db_tiles.py for table structure
        // points/maxpoints = k
        // k <1 use raw data
        // k > use potree level, level = octreeLevels-(k-1)
        // coverage = 100/2^(k-1)

        double k = points / pointsLimit;
        if (k < 1) {
            this.level = octreeLevels + 1;
            this.coverage = 100.0;
        } else {
            this.level = (int) (octreeLevels - (k - 1));
            this.coverage = 100 / (2 ^ ((int) k - 1));
            if (level < 0) {
                throw new TooManyPoints();
            }
        }
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
        if (this == o) { return true;}
        if (o == null || getClass() != o.getClass()) {return false;}
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
