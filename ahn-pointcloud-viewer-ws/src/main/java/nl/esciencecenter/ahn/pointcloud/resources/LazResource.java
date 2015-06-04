package nl.esciencecenter.ahn.pointcloud.resources;

import com.codahale.metrics.annotation.Timed;
import nl.esciencecenter.ahn.pointcloud.core.LazRequest;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import nl.esciencecenter.ahn.pointcloud.exception.TooManyPoints;
import nl.esciencecenter.ahn.pointcloud.job.XenonSubmitter;
import nl.esciencecenter.xenon.XenonException;
import nl.esciencecenter.xenon.jobs.JobDescription;

import javax.validation.Valid;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.WebApplicationException;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

@Path("laz")
@Produces(MediaType.APPLICATION_JSON)
public class LazResource extends AbstractResource {
    private final String executable;
    private final XenonSubmitter submitter;

    public LazResource(PointCloudStore store, XenonSubmitter submitter, String executable) {
        super(store);
        this.submitter = submitter;
        this.executable = executable;
    }

    @POST
    @Timed
    public Size submitSelection(@Valid LazRequest request) throws XenonException {

        // Check selection is not too big
        Size size = null;
        try {
            size = getStore().getApproximateNumberOfPoints(request);
        } catch (TooManyPoints tooManyPoints) {
            throw new WebApplicationException("Too many points requested", Response.Status.REQUEST_ENTITY_TOO_LARGE.getStatusCode());
        }
        if (request.getLevel() > size.getLevel()) {
            throw new WebApplicationException("Too many points requested", Response.Status.REQUEST_ENTITY_TOO_LARGE.getStatusCode());
        }

        // Submit as Xenon job
        JobDescription description = new JobDescription();
        description.setArguments(request.toJobArguments());
        description.setExecutable(executable);
        submitter.submit(description);

        return size;
    }
}
