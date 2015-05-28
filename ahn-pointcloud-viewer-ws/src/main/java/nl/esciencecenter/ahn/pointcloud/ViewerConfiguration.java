package nl.esciencecenter.ahn.pointcloud;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.dropwizard.Configuration;
import io.dropwizard.db.DataSourceFactory;
import nl.esciencecenter.ahn.pointcloud.job.XenonConfiguration;
import org.hibernate.validator.constraints.NotEmpty;
import org.hibernate.validator.constraints.Range;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;

public class ViewerConfiguration extends Configuration {
    @Valid
    @Range(min=1)
    @JsonProperty
    private long maximumNumberOfPoints;

    @Range(min=0)
    private int octreeLevels;

    @Valid
    @NotNull
    @JsonProperty
    private int srid = 28992;

    @Valid
    @NotNull
    @JsonProperty
    private DataSourceFactory database = new DataSourceFactory();

    @Valid
    @NotNull
    @JsonProperty
    private XenonConfiguration xenon;

    @NotEmpty
    @JsonProperty
    private String executable;

    private ViewerConfiguration() {
    }

    public ViewerConfiguration(long maximumNumberOfPoints, int octreeLevels, int srid, DataSourceFactory database, XenonConfiguration xenon, String executable) {
        this.maximumNumberOfPoints = maximumNumberOfPoints;
        this.octreeLevels = octreeLevels;
        this.srid = srid;
        this.database = database;
        this.xenon = xenon;
        this.executable = executable;
    }

    public int getOctreeLevels() {
        return octreeLevels;
    }

    public long getMaximumNumberOfPoints() {
        return maximumNumberOfPoints;
    }

    public int getSrid() {
        return srid;
    }

    public DataSourceFactory getDatabase() {
        return database;
    }

    public XenonConfiguration getXenon() {
        return xenon;
    }

    public String getExecutable() {
        return executable;
    }

}
