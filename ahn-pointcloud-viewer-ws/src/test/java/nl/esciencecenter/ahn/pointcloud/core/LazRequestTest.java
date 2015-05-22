package nl.esciencecenter.ahn.pointcloud.core;

import junit.framework.TestCase;

import static org.hamcrest.core.Is.is;
import static org.junit.Assert.assertThat;

public class LazRequestTest extends TestCase {

    public void testGetEmail() throws Exception {
        LazRequest request = new LazRequest("someone@example.com");

        assertThat(request.getEmail(), is("someone@example.com"));
    }
}