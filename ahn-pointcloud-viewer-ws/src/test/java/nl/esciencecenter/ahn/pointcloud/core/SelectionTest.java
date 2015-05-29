package nl.esciencecenter.ahn.pointcloud.core;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.dropwizard.jackson.Jackson;
import org.junit.Test;

import static io.dropwizard.testing.FixtureHelpers.fixture;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;

public class SelectionTest {
    private static final ObjectMapper MAPPER = Jackson.newObjectMapper();

    @Test
    public void deserializesFromJSON() throws Exception {
        final Selection result = MAPPER.readValue(fixture("fixtures/selection.json"), Selection.class);

        final Selection expected = new Selection(124931.360, 484567.840, 126241.760, 485730.400);
        assertThat(result, equalTo(expected));
    }
}