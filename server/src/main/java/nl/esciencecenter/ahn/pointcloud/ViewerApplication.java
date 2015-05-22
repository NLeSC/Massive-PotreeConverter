package nl.esciencecenter.ahn.pointcloud;

import io.dropwizard.Application;
import io.dropwizard.assets.AssetsBundle;
import io.dropwizard.jdbi.DBIFactory;
import io.dropwizard.servlets.assets.AssetServlet;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;
import nl.esciencecenter.ahn.pointcloud.resources.LazResource;
import nl.esciencecenter.ahn.pointcloud.resources.SizeResource;
import nl.esciencecenter.ahn.pointcloud.services.PointCloudStore;
import org.skife.jdbi.v2.DBI;

public class ViewerApplication extends Application<ViewerConfiguration> {
    public static void main(String[] args) throws Exception {
        new ViewerApplication().run(args);
    }

    @Override
    public void initialize(Bootstrap<ViewerConfiguration> bootstrap) {
        // TODO put distribution of js app into src/main/resources/assets/
        bootstrap.addBundle(new AssetsBundle("/assets/", "/"));
    }

    @Override
    public void run(ViewerConfiguration configuration, Environment environment) throws Exception {
        final DBIFactory factory = new DBIFactory();
        final DBI jdbi = factory.build(environment, configuration.getDataSourceFactory(), "postgresql");
        final PointCloudStore store = new PointCloudStore(jdbi, configuration.getSrid());

        final SizeResource sizeResource = new SizeResource(store);
        environment.jersey().register(sizeResource);

        final LazResource lazResource = new LazResource(store, configuration.getMaximumNumberOfPoints());
        environment.jersey().register(lazResource);
    }
}
