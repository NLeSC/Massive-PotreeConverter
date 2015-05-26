package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dropwizard.jackson.Jackson;
import org.junit.Test;

import static io.dropwizard.testing.FixtureHelpers.fixture;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

public class SizeTest {
    private static final ObjectMapper MAPPER = Jackson.newObjectMapper();

    @Test
    public void testGetPoints() throws Exception {
        Size size = new Size(1234);

        assertThat(size.getPoints(), equalTo(1234L));
    }

    @Test
    public void serializesToJSON() throws Exception {
        final Size input = new Size(42132530);

        final String result = MAPPER.writeValueAsString(input);

        final String expected = MAPPER.writeValueAsString(MAPPER.readValue(fixture("fixtures/size.json"), Size.class));
        assertThat(result, equalTo(expected));
    }
}