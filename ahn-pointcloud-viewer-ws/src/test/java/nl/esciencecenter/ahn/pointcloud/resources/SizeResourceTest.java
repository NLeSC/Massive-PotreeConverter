package nl.esciencecenter.ahn.pointcloud.resources;

import nl.esciencecenter.ahn.pointcloud.core.Selection;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import nl.esciencecenter.ahn.pointcloud.db.PointCloudStore;
import org.junit.Before;
import org.junit.Test;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class SizeResourceTest {
    private PointCloudStore store;

    @Before
    public void setUp() {
        store = mock(PointCloudStore.class);
    }

    @Test
    public void testGetSizeOfSelection() throws Exception {
        Selection selection = new Selection(124931.360, 484567.840, 126241.760, 485730.400);
        when(store.getApproximateNumberOfPoints(selection)).thenReturn(100L);
        SizeResource resource = new SizeResource(store, 500L);

        Size size = resource.getSizeOfSelection(selection);

        Size expected = new Size(100L);
        assertThat(size, equalTo(expected));
    }
}