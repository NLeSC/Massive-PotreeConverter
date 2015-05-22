package nl.esciencecenter.ahn.pointcloud.resources;


import com.codahale.metrics.annotation.Timed;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import nl.esciencecenter.ahn.pointcloud.services.PointCloudStore;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

@Path("size/{left}/{bottom}/{right}/{top}")
@Produces(MediaType.APPLICATION_JSON)
public class SizeResource extends AbstractResource {

    public SizeResource(PointCloudStore store) {
        super(store);
    }

    @GET
    @Timed
    public Size getSizeOfSelection(@PathParam("left") Double left,
                                   @PathParam("bottom") Double bottom,
                                   @PathParam("right") Double right,
                                   @PathParam("top") Double top) {

        long points = store.getApproximateNumberOfPoints(left, bottom, right, top);

        return new Size(points);
    }
}
