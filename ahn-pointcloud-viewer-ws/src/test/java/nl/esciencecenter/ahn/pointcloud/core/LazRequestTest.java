package nl.esciencecenter.ahn.pointcloud.core;

import org.junit.Test;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.core.Is.is;
import static org.junit.Assert.assertThat;

public class LazRequestTest  {

    @Test
    public void testGetEmail() throws Exception {
        LazRequest request = new LazRequest(1.0, 2.0, 3.0, 4.0, "someone@example.com");

        assertThat(request.getEmail(), is("someone@example.com"));
    }

    @Test
    public void testToJobArguments() throws Exception {
        LazRequest request = new LazRequest(1.0, 2.0, 3.0, 4.0, "someone@example.com");

        String[] expected = {"1.0", "2.0", "3.0", "4.0", "someone@example.com"};

        assertThat(request.toJobArguments(), equalTo(expected));
    }
}