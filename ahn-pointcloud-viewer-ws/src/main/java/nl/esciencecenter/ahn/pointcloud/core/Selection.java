package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import nl.esciencecenter.ahn.pointcloud.validation.ValidSelection;

import javax.validation.constraints.NotNull;
import java.util.Objects;

@ValidSelection
public class Selection {
    @NotNull
    @JsonProperty
    protected Double left;

    @NotNull
    @JsonProperty
    protected Double bottom;

    @NotNull
    @JsonProperty
    protected Double right;

    @NotNull
    @JsonProperty
    protected Double top;

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
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Selection selection = (Selection) o;
        return Objects.equals(left, selection.left) &&
                Objects.equals(bottom, selection.bottom) &&
                Objects.equals(right, selection.right) &&
                Objects.equals(top, selection.top);
    }

    @Override
    public int hashCode() {
        return Objects.hash(left, bottom, right, top);
    }
}
