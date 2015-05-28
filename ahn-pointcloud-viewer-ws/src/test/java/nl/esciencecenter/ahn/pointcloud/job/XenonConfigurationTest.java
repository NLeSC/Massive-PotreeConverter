package nl.esciencecenter.ahn.pointcloud.job;

import com.google.common.collect.ImmutableMap;
import org.junit.Before;
import org.junit.Test;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

public class XenonConfigurationTest {
    private XenonConfiguration config;
    private SchedulerConfiguration scheduler;
    private ImmutableMap<String,String> props;

    @Before
    public void setUp() {
        props = ImmutableMap.of("somepropkey", "somepropvalue");
        scheduler = new SchedulerConfiguration("ssh", "someone@somewhere:2222", "multi", props);
        config = new XenonConfiguration(scheduler, props);
    }
    
    @Test
    public void testGetScheduler() throws Exception {
        assertThat(config.getScheduler(), is(scheduler));
    }

    @Test
    public void testGetProperties() throws Exception {
        assertThat(config.getProperties(), is(props));
    }
}