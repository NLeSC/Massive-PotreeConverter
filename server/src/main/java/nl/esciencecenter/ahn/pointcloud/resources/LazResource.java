package nl.esciencecenter.ahn.pointcloud.resources;

import com.codahale.metrics.annotation.Timed;
import nl.esciencecenter.ahn.pointcloud.core.LazRequest;
import nl.esciencecenter.ahn.pointcloud.services.PointCloudStore;

import javax.validation.Valid;
import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

@Path("laz/{left}/{bottom}/{right}/{top}")
@Produces(MediaType.APPLICATION_JSON)
public class LazResource extends AbstractResource {
    private final long maximumNumberOfPoints;

    public LazResource(PointCloudStore store, long maximumNumberOfPoints) {
        super(store);
        this.maximumNumberOfPoints = maximumNumberOfPoints;
    }

    @POST
    @Timed
    public Response submitSelection(@PathParam("left") Double left,
                           @PathParam("bottom") Double bottom,
                           @PathParam("right") Double right,
                           @PathParam("top") Double top,
                           @Valid LazRequest request) {

        // Check selection is not too big
        if (store.getApproximateNumberOfPoints(left, bottom, right, top) > maximumNumberOfPoints) {
            throw new WebApplicationException("Too many points requested", Response.Status.REQUEST_ENTITY_TOO_LARGE.getStatusCode());
        }

        // TODO Submit Xenon job

        return Response.noContent().build();
    }
}
