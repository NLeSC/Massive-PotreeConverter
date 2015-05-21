package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.hibernate.validator.constraints.Email;

import javax.validation.constraints.NotNull;

public class LazRequest {

    @NotNull
    @Email
    @JsonProperty
    private String email;
}
