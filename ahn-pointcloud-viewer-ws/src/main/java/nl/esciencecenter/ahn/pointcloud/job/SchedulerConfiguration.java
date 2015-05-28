package nl.esciencecenter.ahn.pointcloud.job;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableMap;
import org.hibernate.validator.constraints.NotEmpty;

public class SchedulerConfiguration {
    /**
     * Scheme of scheduler used to submit jobs
     */
    @NotEmpty
    @JsonProperty
    private String scheme;

    /**
     * Location of scheduler used to submit jobs.
     * eg. For scheme=='ssh' use 'username@hostname:port'.
     */
    @JsonProperty
    private String location;

    /**
     * Queue of scheduler used to submit jobs
     */
    @NotEmpty
    @JsonProperty
    private String queue;

    /**
     * Xenon scheduler properties
     */
    @JsonProperty
    private ImmutableMap<String, String> properties = ImmutableMap.of();

    private SchedulerConfiguration() {
    }

    public SchedulerConfiguration(String scheme, String location, String queue, ImmutableMap<String, String> properties) {
        this.scheme = scheme;
        this.location = location;
        this.queue = queue;
        this.properties = properties;
    }

    public String getScheme() {
        return scheme;
    }

    public String getLocation() {
        return location;
    }

    public String getQueue() {
        return queue;
    }

    public ImmutableMap<String, String> getProperties() {
        return properties;
    }
}
