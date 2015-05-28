package nl.esciencecenter.ahn.pointcloud.db;

import nl.esciencecenter.ahn.pointcloud.core.Selection;
import nl.esciencecenter.ahn.pointcloud.core.Size;
import org.junit.Before;
import org.junit.Test;
import org.skife.jdbi.v2.DBI;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assert.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class PointCloudStoreTest {
    private DBI dbi;
    private final int srid = 28992;
    private PointCloudStore store;

    @Before
    public void setUp() throws Exception {
        dbi = mock(DBI.class);
        store = new PointCloudStore(dbi, srid);
    }

    @Test
    public void testGetApproximateNumberOfPoints() throws Exception {
        TilesDAO tiles = mock(TilesDAO.class);
        when(tiles.getApproximateNumberOfPoints(124931.360, 484567.840, 126241.760, 485730.400, srid)).thenReturn(1234L);
        when(dbi.onDemand(TilesDAO.class)).thenReturn(tiles);

        Selection selection = new Selection(124931.360, 484567.840, 126241.760, 485730.400);
        Size result = store.getApproximateNumberOfPoints(selection);

        Size expected = new Size(1234L, 10, 100);
        assertThat(result, equalTo(expected));
    }
}