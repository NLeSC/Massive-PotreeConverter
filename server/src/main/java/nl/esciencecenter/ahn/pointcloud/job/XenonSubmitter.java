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

    private final XenonConfiguration configuration;
    private final Xenon xenon;
    private final Scheduler scheduler;

    public XenonSubmitter(XenonConfiguration configuration) throws XenonException {
        this.configuration = configuration;

        xenon = XenonFactory.newXenon(configuration.getProperties());
        SchedulerConfiguration schedulerConf = configuration.getScheduler();
        scheduler = newScheduler();
    }

    /**
     * @return Scheduler
     * @throws XenonException
     */
    protected Scheduler newScheduler() throws XenonException {
        Credential credential = null;
        SchedulerConfiguration schedulerConf = configuration.getScheduler();
        // TODO prompt user for password/passphrases
        return xenon.jobs().newScheduler(schedulerConf.getScheme(), schedulerConf.getLocation(), credential, schedulerConf.getProperties());
    }

    public void submit(JobRequest request) throws XenonException {
        JobDescription description = request.toJobDescription();
        description.setQueueName(configuration.getScheduler().getQueue());
        Job job = xenon.jobs().submitJob(scheduler, description);
        LOGGER.info("Submitted "+ job.getIdentifier());
    }

    @Override
    public void start() throws Exception {

    }

    @Override
    public void stop() throws Exception {
        XenonFactory.endXenon(xenon);
    }
}
