package nl.esciencecenter.ahn.pointcloud;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.dropwizard.Configuration;
import org.hibernate.validator.constraints.NotEmpty;

import javax.validation.Valid;

public class ViewerConfiguration extends Configuration {
    @Valid
    @NotEmpty
    @JsonProperty
    private long maximumNumberOfPoints = 400*10^6;
}
