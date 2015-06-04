package nl.esciencecenter.ahn.pointcloud.resources;

import nl.esciencecenter.ahn.pointcloud.core.LazRequest;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import nl.esciencecenter.ahn.pointcloud.exception.TooManyPoints;
import nl.esciencecenter.ahn.pointcloud.job.XenonSubmitter;
import nl.esciencecenter.xenon.XenonException;
import nl.esciencecenter.xenon.jobs.JobDescription;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.mockito.ArgumentCaptor;

import javax.ws.rs.WebApplicationException;
import java.util.Arrays;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;
import static org.mockito.Mockito.*;


public class LazResourceTest {
    private PointCloudStore store;
    private XenonSubmitter xenon;

    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Before
    public void setUp() throws Exception {
        store = mock(PointCloudStore.class);
        xenon = mock(XenonSubmitter.class);
    }

    @Test
    public void submitSelection_nottoobig_jobsubmitted() throws TooManyPoints, XenonException {
        LazRequest request = new LazRequest(124931.360, 484567.840, 126241.760, 485730.400, "someone@example.com", 13);
        Size size = new Size(3213414L, 13, 100.0);
        when(store.getApproximateNumberOfPoints(request)).thenReturn(size);
        LazResource resource = new LazResource(store, xenon, "/usr/bin/ahn-laz-slicer");

        resource.submitSelection(request);

        ArgumentCaptor<JobDescription> argument = ArgumentCaptor.forClass(JobDescription.class);
        verify(xenon, times(1)).submit(argument.capture());
        JobDescription submittedDescription = argument.getValue();
        assertThat(submittedDescription.getExecutable(), is("/usr/bin/ahn-laz-slicer"));
        String[] expectedArguments = {
                "124931.36", "484567.84", "126241.76", "485730.4", "someone@example.com", "13"
        };
        assertThat(submittedDescription.getArguments(), equalTo(Arrays.asList(expectedArguments)));
    }

    @Test
    public void submitSelection_toomanypoints_entitytoolargeexception() throws TooManyPoints, XenonException {
        LazRequest request = new LazRequest(124931.360, 484567.840, 126241.760, 485730.400, "someone@example.com", 13);
        TooManyPoints toomanypoints = new TooManyPoints();
        when(store.getApproximateNumberOfPoints(request)).thenThrow(toomanypoints);
        LazResource resource = new LazResource(store, xenon, "/usr/bin/ahn-laz-slicer");

        thrown.expect(WebApplicationException.class);

        resource.submitSelection(request);
    }

    @Test
    public void submitSelection_requestedlevel2high_entitytoolargeexception() throws TooManyPoints, XenonException {
        LazRequest request = new LazRequest(124931.360, 484567.840, 126241.760, 485730.400, "someone@example.com", 18);
        Size size = new Size(3213414L, 13, 100.0);
        when(store.getApproximateNumberOfPoints(request)).thenReturn(size);
        LazResource resource = new LazResource(store, xenon, "/usr/bin/ahn-laz-slicer");

        thrown.expect(WebApplicationException.class);

        resource.submitSelection(request);
    }
}