package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.Email;

import javax.validation.constraints.NotNull;

public class LazRequest {

    @NotNull
    @Email
    @JsonProperty
    private String email;

    public LazRequest() {
    }

    public LazRequest(String email) {
        this.email = email;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
