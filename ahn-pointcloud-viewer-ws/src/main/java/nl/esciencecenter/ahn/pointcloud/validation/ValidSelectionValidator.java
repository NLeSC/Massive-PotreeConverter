package nl.esciencecenter.ahn.pointcloud.validation;

import nl.esciencecenter.ahn.pointcloud.core.Selection;

import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

public class ValidSelectionValidator implements ConstraintValidator<ValidSelection, Selection> {


    @Override
    public void initialize(ValidSelection constraintAnnotation) {

    }

    @Override
    public boolean isValid(Selection value, ConstraintValidatorContext context) {
        // OK if left < right + bottom < top
        boolean isValid = true;
        if (value.getBottom() == null || value.getLeft() == null || value.getRight() == null || value.getTop() == null) {
            // unable to validate ranges with nulls, let field validations trigger violations
            return true;
        }
        // don't use default message, because violation can be vertical or horizontal
        context.disableDefaultConstraintViolation();
        if (value.getLeft() > value.getRight()) {
            context.buildConstraintViolationWithTemplate("Right must be bigger than left").addConstraintViolation();
            isValid = false;
        }
        if (value.getBottom() > value.getTop()) {
            context.buildConstraintViolationWithTemplate("Top must be bigger than bottom").addConstraintViolation();
            isValid = false;
        }

        return isValid;
    }
}
