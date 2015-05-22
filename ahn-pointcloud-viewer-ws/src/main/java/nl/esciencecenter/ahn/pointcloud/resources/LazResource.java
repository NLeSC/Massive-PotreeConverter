package nl.esciencecenter.ahn.pointcloud.resources;

import com.codahale.metrics.annotation.Timed;
import nl.esciencecenter.ahn.pointcloud.core.LazRequest;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import nl.esciencecenter.ahn.pointcloud.job.JobRequest;
import nl.esciencecenter.ahn.pointcloud.job.XenonSubmitter;
import nl.esciencecenter.xenon.XenonException;

import javax.validation.Valid;
import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

@Path("laz/{left}/{bottom}/{right}/{top}")
@Produces(MediaType.APPLICATION_JSON)
public class LazResource extends AbstractResource {
    private final long maximumNumberOfPoints;
    private XenonSubmitter submitter;

    public LazResource(PointCloudStore store, XenonSubmitter submitter, long maximumNumberOfPoints) {
        super(store);
        this.submitter = submitter;
        this.maximumNumberOfPoints = maximumNumberOfPoints;
    }

    @POST
    @Timed
    public Response submitSelection(@PathParam("left") Double left,
                           @PathParam("bottom") Double bottom,
                           @PathParam("right") Double right,
                           @PathParam("top") Double top,
                           @Valid LazRequest request) throws XenonException {

        // Check selection is not too big
        if (store.getApproximateNumberOfPoints(left, bottom, right, top) > maximumNumberOfPoints) {
            throw new WebApplicationException("Too many points requested", Response.Status.REQUEST_ENTITY_TOO_LARGE.getStatusCode());
        }

        // Submit as Xenon job
        JobRequest jobRequest = new JobRequest(left, bottom, right, top, request.getEmail());
        submitter.submit(jobRequest);

        return Response.noContent().build();
    }
}
