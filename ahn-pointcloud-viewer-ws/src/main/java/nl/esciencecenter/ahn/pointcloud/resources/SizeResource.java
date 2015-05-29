package nl.esciencecenter.ahn.pointcloud.resources;


import com.codahale.metrics.annotation.Timed;
import nl.esciencecenter.ahn.pointcloud.core.Selection;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import nl.esciencecenter.ahn.pointcloud.exception.TooManyPoints;

import javax.validation.Valid;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

@Path("size")
@Produces(MediaType.APPLICATION_JSON)
public class SizeResource extends AbstractResource {

    public SizeResource(PointCloudStore store) {
        super(store);
    }

    @POST
    @Timed
    public Size getSizeOfSelection(@Valid Selection selection) throws TooManyPoints {
        return getStore().getApproximateNumberOfPoints(selection);
    }
}
