package nl.esciencecenter.ahn.pointcloud;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.dropwizard.Configuration;
import io.dropwizard.db.DataSourceFactory;
import org.hibernate.validator.constraints.Range;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import java.util.Objects;

public class ViewerConfiguration extends Configuration {
    @Valid
    @Range(min=1)
    @JsonProperty
    private long maximumNumberOfPoints;

    @Valid
    @NotNull
    @JsonProperty
    private int srid = 28992;

    @Valid
    @NotNull
    @JsonProperty
    private DataSourceFactory database = new DataSourceFactory();

    public ViewerConfiguration() {
    }

    public long getMaximumNumberOfPoints() {
        return maximumNumberOfPoints;
    }

    public void setMaximumNumberOfPoints(long maximumNumberOfPoints) {
        this.maximumNumberOfPoints = maximumNumberOfPoints;
    }

    public DataSourceFactory getDataSourceFactory() {
        return database;
    }

    public void setDataSourceFactory(DataSourceFactory database) {
        this.database = database;
    }

    public int getSrid() {
        return srid;
    }

    public void setSrid(int srid) {
        this.srid = srid;
    }
}
