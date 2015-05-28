package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.Email;

import javax.validation.constraints.NotNull;

public class LazRequest extends Selection {

    @NotNull
    @Email
    @JsonProperty
    private String email;

    private LazRequest() {
    }

    public LazRequest(Double left, Double bottom, Double right, Double top, String email) {
        super(left, bottom, right, top);
        this.email = email;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String[] toJobArguments() {
        String[] arguments = {
            String.valueOf(getLeft()),
            String.valueOf(getBottom()),
            String.valueOf(getRight()),
            String.valueOf(getTop()),
            email
        };

        return arguments;
    }
}
