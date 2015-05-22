package nl.esciencecenter.ahn.pointcloud.core;

import junit.framework.TestCase;

public class SizeTest extends TestCase {
    public void testIt() throws Exception {
        Size size = new Size(1234);

        assertEquals(size.getPoints(), 1234);
    }
}