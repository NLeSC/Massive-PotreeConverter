package nl.esciencecenter.ahn.pointcloud;

import io.dropwizard.Application;
import io.dropwizard.jdbi.DBIFactory;
import io.dropwizard.setup.Environment;
import nl.esciencecenter.ahn.pointcloud.job.XenonSubmitter;
import nl.esciencecenter.ahn.pointcloud.resources.LazResource;
import nl.esciencecenter.ahn.pointcloud.resources.SizeResource;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import org.skife.jdbi.v2.DBI;

public class ViewerApplication extends Application<ViewerConfiguration> {
    public static void main(String[] args) throws Exception {
        new ViewerApplication().run(args);
    }

    @Override
    public void run(ViewerConfiguration configuration, Environment environment) throws Exception {
        final DBIFactory factory = new DBIFactory();
        final DBI jdbi = factory.build(environment, configuration.getDatabase(), "postgresql");
        final PointCloudStore store = new PointCloudStore(jdbi, configuration.getSrid());

        final SizeResource sizeResource = new SizeResource(store);
        environment.jersey().register(sizeResource);

        final XenonSubmitter submitter = new XenonSubmitter(configuration.getXenon());
        final LazResource lazResource = new LazResource(store, submitter, configuration.getMaximumNumberOfPoints());
        environment.jersey().register(lazResource);
    }
}
