package nl.esciencecenter.ahn.pointcloud;

import com.google.common.collect.ImmutableMap;
import io.dropwizard.db.DataSourceFactory;
import io.dropwizard.jersey.setup.JerseyEnvironment;
import io.dropwizard.setup.Environment;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import nl.esciencecenter.ahn.pointcloud.job.SchedulerConfiguration;
import nl.esciencecenter.ahn.pointcloud.job.XenonConfiguration;
import nl.esciencecenter.ahn.pointcloud.resources.AbstractResource;
import org.junit.Test;

import static org.mockito.Mockito.*;

public class ViewerApplicationTest {

    @Test
    public void testRegisterResources() throws Exception {
        ImmutableMap<String, String> props = ImmutableMap.of();
        SchedulerConfiguration scheduler = new SchedulerConfiguration("local", "/", "multi", props);
        XenonConfiguration xenon = new XenonConfiguration(scheduler, props);
        DataSourceFactory database = mock(DataSourceFactory.class);

        ViewerConfiguration config = new ViewerConfiguration(5, 28992, database, xenon, "/bin/hostname");
        Environment env = mock(Environment.class);
        JerseyEnvironment jersey = mock(JerseyEnvironment.class);
        when(env.jersey()).thenReturn(jersey);
        PointCloudStore store = mock(PointCloudStore.class);

        ViewerApplication app = new ViewerApplication();
        app.registerResources(config, env, store);

        verify(jersey, times(2)).register(any(AbstractResource.class));
    }
}