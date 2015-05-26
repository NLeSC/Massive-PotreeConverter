package nl.esciencecenter.ahn.pointcloud.job;

import nl.esciencecenter.xenon.Xenon;
import nl.esciencecenter.xenon.jobs.JobDescription;
import nl.esciencecenter.xenon.jobs.Jobs;
import nl.esciencecenter.xenon.jobs.Scheduler;
import org.junit.Before;
import org.junit.Test;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;


public class XenonSubmitterTest {
    private Xenon xenon;
    private Jobs jobs;
    private Scheduler scheduler;
    private XenonSubmitter submitter;

    @Before
    public void setUp() {
        xenon = mock(Xenon.class);
        jobs = mock(Jobs.class);
        when(xenon.jobs()).thenReturn(jobs);
        scheduler = mock(Scheduler.class);
        submitter = new XenonSubmitter("multi", xenon, scheduler);
    }
    
    @Test
    public void testSubmit() throws Exception {
        JobDescription description = new JobDescription();

        submitter.submit(description);

        verify(jobs).submitJob(scheduler, description);
        assertThat(description.getQueueName(), is("multi"));
    }
}