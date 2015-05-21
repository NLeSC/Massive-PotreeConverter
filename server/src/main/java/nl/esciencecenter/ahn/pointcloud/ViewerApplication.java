package nl.esciencecenter.ahn.pointcloud;

import io.dropwizard.Application;
import io.dropwizard.setup.Environment;

public class ViewerApplication extends Application<ViewerConfiguration> {
    public static void main(String[] args) throws Exception {
        new ViewerApplication().run(args);
    }

    @Override
    public void run(ViewerConfiguration configuration, Environment environment) throws Exception {

    }
}
