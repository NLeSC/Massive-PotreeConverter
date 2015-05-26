package nl.esciencecenter.ahn.pointcloud.job;

import com.google.common.collect.ImmutableMap;
import org.junit.Before;
import org.junit.Test;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

public class SchedulerConfigurationTest {
    private SchedulerConfiguration config;
    private ImmutableMap<String, String> props;

    @Before
    public void setUp() {
        props = ImmutableMap.of("somepropkey", "somepropvalue");
        config = new SchedulerConfiguration("ssh", "someone@somewhere:2222", "multi", props);
    }

    @Test
    public void testGetScheme() throws Exception {
        assertThat(config.getScheme(), is("ssh"));
    }

    @Test
    public void testGetLocation() throws Exception {
        assertThat(config.getLocation(), is("someone@somewhere:2222"));
    }

    @Test
    public void testGetQueue() throws Exception {
        assertThat(config.getQueue(), is("multi"));

    }

    @Test
    public void testGetProperties() throws Exception {
        assertThat(config.getProperties(), equalTo(props));
    }
}