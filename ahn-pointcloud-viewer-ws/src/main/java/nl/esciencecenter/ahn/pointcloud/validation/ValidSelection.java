package nl.esciencecenter.ahn.pointcloud.validation;

import javax.validation.Constraint;
import javax.validation.Payload;
import java.lang.annotation.*;

@Target({ElementType.TYPE, ElementType.ANNOTATION_TYPE })
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = { ValidSelectionValidator.class })
@Documented
public @interface ValidSelection {

    String message() default "{nl.esciencecenter.ahn.pointcloud.validation." +
            "ValidSelection.message}";

    Class<?>[] groups() default { };

    Class<? extends Payload>[] payload() default { };
}
