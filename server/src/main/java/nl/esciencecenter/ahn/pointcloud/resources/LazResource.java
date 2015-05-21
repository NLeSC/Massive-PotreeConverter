package nl.esciencecenter.ahn.pointcloud.resources;

import com.codahale.metrics.annotation.Timed;
import nl.esciencecenter.ahn.pointcloud.core.LazRequest;
import nl.esciencecenter.ahn.pointcloud.services.PointCloudStore;

import javax.validation.Valid;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

@Path("size/{left}/{bottom}/{right}/{top}")
@Produces(MediaType.APPLICATION_JSON)
public class LazResource extends AbstractResource {

    public LazResource(PointCloudStore store) {
        super(store);
    }

    @POST
    @Timed
    public Response submitSelection(@PathParam("left") Double left,
                           @PathParam("bottom") Double bottom,
                           @PathParam("right") Double right,
                           @PathParam("top") Double top,
                           @Valid LazRequest request) {

        // Check selection is not too big

        // Submit Xenon job

        return Response.noContent().build();
    }
}
