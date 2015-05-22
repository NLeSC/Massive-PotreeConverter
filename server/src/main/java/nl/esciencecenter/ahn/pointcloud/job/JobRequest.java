package nl.esciencecenter.ahn.pointcloud.job;

import com.google.common.collect.ImmutableList;
import nl.esciencecenter.xenon.jobs.JobDescription;

import java.util.ArrayList;
import java.util.List;

public class JobRequest {
    private String email;
    private Double left;
    private Double bottom;
    private Double right;
    private Double top;
    private String executable = "ahn-slicer";

    public JobRequest(Double left, Double bottom, Double right, Double top, String email) {
        this.email = email;
        this.left = left;
        this.bottom = bottom;
        this.right = right;
        this.top = top;
    }

    public String getEmail() {
        return email;
    }

    public Double getLeft() {
        return left;
    }

    public Double getBottom() {
        return bottom;
    }

    public Double getRight() {
        return right;
    }

    public Double getTop() {
        return top;
    }

    public JobDescription toJobDescription() {
        JobDescription description = new JobDescription();
        description.setExecutable(executable);
        description.addArgument(String.valueOf(left));
        description.addArgument(String.valueOf(bottom));
        description.addArgument(String.valueOf(right));
        description.addArgument(String.valueOf(top));
        description.addArgument(email);

        return description;
    }
}
