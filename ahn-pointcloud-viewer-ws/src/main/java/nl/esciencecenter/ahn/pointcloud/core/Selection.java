package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import nl.esciencecenter.ahn.pointcloud.validation.ValidSelection;

import javax.validation.constraints.NotNull;
import java.util.Objects;

@ValidSelection
public class Selection {
    @NotNull
    @JsonProperty
    private Double left;

    @NotNull
    @JsonProperty
    private Double bottom;

    @NotNull
    @JsonProperty
    private Double right;

    @NotNull
    @JsonProperty
    private Double top;

    public Selection(Double left, Double bottom, Double right, Double top) {
        this.left = left;
        this.bottom = bottom;
        this.right = right;
        this.top = top;
    }

    protected Selection() {
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

    @Override
    public boolean equals(Object o) {
        if (this == o) {return true;}
        if (o == null || getClass() != o.getClass()) {return false;}
        Selection selection = (Selection) o;
        return Objects.equals(getLeft(), selection.getLeft()) &&
                Objects.equals(getBottom(), selection.getBottom()) &&
                Objects.equals(getRight(), selection.getRight()) &&
                Objects.equals(getTop(), selection.getTop());
    }

    @Override
    public int hashCode() {
        return Objects.hash(getLeft(), getBottom(), getRight(), getTop());
    }
}
