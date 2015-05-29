package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.Email;
import org.hibernate.validator.constraints.Range;

import javax.validation.constraints.NotNull;

public class LazRequest extends Selection {

    @NotNull
    @Range(min=0, max=24)
    @JsonProperty
    private int level;

    @NotNull
    @Email
    @JsonProperty
    private String email;

    private LazRequest() {
    }

    public LazRequest(Double left, Double bottom, Double right, Double top, String email, int level) {
        super(left, bottom, right, top);
        this.email = email;
        this.level = level;
    }

    public String getEmail() {
        return email;
    }

    public int getLevel() {
        return level;
    }

    public String[] toJobArguments() {
        String[] arguments = {
            String.valueOf(getLeft()),
            String.valueOf(getBottom()),
            String.valueOf(getRight()),
            String.valueOf(getTop()),
            email,
            String.valueOf(level)
        };

        return arguments;
    }
}
