package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dropwizard.jackson.Jackson;
import nl.esciencecenter.ahn.pointcloud.exception.TooManyPoints;
import org.junit.Test;

import static io.dropwizard.testing.FixtureHelpers.fixture;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

public class SizeTest {
    private static final ObjectMapper MAPPER = Jackson.newObjectMapper();

    @Test
    public void serializesToJSON() throws Exception {
        final Size input = new Size(42132530L, 8, 100.0);

        final String result = MAPPER.writeValueAsString(input);

        final String expected = MAPPER.writeValueAsString(MAPPER.readValue(fixture("fixtures/size.json"), Size.class));
        assertThat(result, equalTo(expected));
    }

    @Test
    public void contruct_100coverage() throws TooManyPoints {
        final Size result = new Size(100L, 200L, 9);

        final Size expected = new Size(100L, 10, 100.0);
        assertThat(result, equalTo(expected));
    }

    @Test
    public void construct_16coverage() throws TooManyPoints {
        final Size result = new Size(100L, 20L, 9);

        final Size expected = new Size(100L, 5, 16.0);
        assertThat(result, equalTo(expected));
    }

    @Test(expected=TooManyPoints.class)
    public void construct_toomanypoints() throws TooManyPoints {
        new Size(100L, 2L, 3);
    }
}