package nl.esciencecenter.ahn.pointcloud.job;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableMap;

import javax.validation.Valid;
import java.util.Map;

public class XenonConfiguration {
    /**
     * Scheduler configuration used to submit jobs
     */
    @Valid
    @JsonProperty
    private SchedulerConfiguration scheduler;

    /**
     * Xenon global properties
     */
    @JsonProperty
    private ImmutableMap<String, String> properties = ImmutableMap.of();

    private XenonConfiguration() {
    }

    public XenonConfiguration(SchedulerConfiguration scheduler, ImmutableMap<String, String> properties) {
        this.scheduler = scheduler;
        this.properties = properties;
    }

    public SchedulerConfiguration getScheduler() {
        return scheduler;
    }

    public Map<String, String> getProperties() {
        return properties;
    }
}
