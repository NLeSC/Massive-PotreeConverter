package nl.esciencecenter.ahn.pointcloud.job;

import io.dropwizard.lifecycle.Managed;
import nl.esciencecenter.xenon.Xenon;
import nl.esciencecenter.xenon.XenonException;
import nl.esciencecenter.xenon.XenonFactory;
import nl.esciencecenter.xenon.credentials.Credential;

import nl.esciencecenter.xenon.jobs.Job;
import nl.esciencecenter.xenon.jobs.JobDescription;
import nl.esciencecenter.xenon.jobs.Scheduler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class XenonSubmitter implements Managed {
    protected static final Logger LOGGER = LoggerFactory.getLogger(XenonSubmitter.class);

    /**
     * Queue of scheduler to which job description will be submitted
     */
    private final String queue;
    private final Xenon xenon;
    private final Scheduler scheduler;

    public XenonSubmitter(XenonConfiguration configuration) throws XenonException {
        xenon = XenonFactory.newXenon(configuration.getProperties());
        scheduler = newScheduler(configuration.getScheduler());
        queue = configuration.getScheduler().getQueue();
    }

    public XenonSubmitter(String queue, Xenon xenon, Scheduler scheduler) {
        this.queue = queue;
        this.xenon = xenon;
        this.scheduler = scheduler;
    }

    /**
     * @return Scheduler
     * @throws XenonException
     */
    protected Scheduler newScheduler(SchedulerConfiguration schedulerConf) throws XenonException {
        // TODO prompt user for password/passphrases
        Credential credential = null;
        return xenon.jobs().newScheduler(schedulerConf.getScheme(), schedulerConf.getLocation(), credential, schedulerConf.getProperties());
    }

    /**
     * Submit job to the Xenon job queue
     *
     * @param description Job description
     * @return Job representing the running job.
     * @throws XenonException
     */
    public Job submit(JobDescription description) throws XenonException {
        description.setQueueName(queue);
        return xenon.jobs().submitJob(scheduler, description);
    }

    @Override
    public void start() throws Exception {

    }

    @Override
    public void stop() throws Exception {
        XenonFactory.endXenon(xenon);
    }
}
