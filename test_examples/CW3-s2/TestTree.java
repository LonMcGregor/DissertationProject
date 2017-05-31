import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;
import org.junit.Test;

public class TestTree {

    @Test
    public void create() {
        Tree t = TestTreeInternals.makeAndCheckTree(4);
		assertEquals(t.Val(),4);
		assertNull(t.Smaller());
		assertNull(t.Greater());
    }

    @Test
    public void insertionLess() {
        Tree t = TestTreeInternals.makeAndCheckTree(4);
		assertTrue(t.Insert(3));
		assertEquals(t.Val(),4);
		assertEquals(t.Smaller().Val(), 3);
		assertNull(t.Smaller().Smaller());
		assertNull(t.Smaller().Greater());
		assertNull(t.Greater());
    }

    @Test
    public void insertionGreater() {
        Tree t = TestTreeInternals.makeAndCheckTree(4);
		assertTrue(t.Insert(5));
		assertEquals(t.Val(),4);
		assertEquals(t.Greater().Val(), 5);
		assertNull(t.Greater().Greater());
		assertNull(t.Greater().Smaller());
		assertNull(t.Smaller());
    }

    @Test
    public void insertionDeep() {
        Tree t = TestTreeInternals.makeAndCheckTree(4);
		assertTrue(t.Insert(7));
		assertTrue(t.Insert(5));
		assertTrue(t.Insert(8));
		assertTrue(t.Insert(2));
		assertTrue(t.Insert(1));
		assertTrue(t.Insert(3));
		assertTrue(t.Insert(6));
		assertEquals(t.Val(),4);
		assertEquals(t.Greater().Val(),7);
		assertEquals(t.Greater().Smaller().Val(),5);
		assertEquals(t.Greater().Greater().Val(),8);
		assertEquals(t.Smaller().Val(),2);
		assertEquals(t.Smaller().Smaller().Val(),1);
		assertEquals(t.Smaller().Greater().Val(),3);
		assertEquals(t.Greater().Smaller().Greater().Val(),6);
		assertNull(t.Greater().Smaller().Smaller());
		assertNull(t.Greater().Greater().Greater());
		assertNull(t.Greater().Greater().Smaller());
		assertNull(t.Smaller().Smaller().Smaller());
		assertNull(t.Smaller().Smaller().Smaller());
		assertNull(t.Smaller().Greater().Smaller());
		assertNull(t.Smaller().Greater().Greater());
		assertNull(t.Greater().Smaller().Greater().Greater());
		assertNull(t.Greater().Smaller().Greater().Smaller());
    }

    @Test
    public void insertionExists() {
        Tree t = TestTreeInternals.makeAndCheckTree(4);
		assertFalse(t.Insert(4));
		assertEquals(t.Val(),4);
		assertNull(t.Smaller());
		assertNull(t.Greater());
    }

    @Test
    public void insertionExistsDeep() {
        Tree t = TestTreeInternals.makeAndCheckTree(4);
		assertTrue(t.Insert(7));
		assertTrue(t.Insert(5));
		assertTrue(t.Insert(8));
		assertTrue(t.Insert(2));
		assertTrue(t.Insert(1));
		assertTrue(t.Insert(3));
		assertFalse(t.Insert(7));
		assertFalse(t.Insert(5));
		assertFalse(t.Insert(8));
		assertFalse(t.Insert(2));
		assertFalse(t.Insert(1));
		assertFalse(t.Insert(3));
		assertEquals(t.Greater().Val(),7);
		assertEquals(t.Greater().Smaller().Val(),5);
		assertEquals(t.Greater().Greater().Val(),8);
		assertEquals(t.Smaller().Val(),2);
		assertEquals(t.Smaller().Smaller().Val(),1);
		assertEquals(t.Smaller().Greater().Val(),3);
		assertNull(t.Greater().Smaller().Smaller());
		assertNull(t.Greater().Greater().Greater());
		assertNull(t.Greater().Greater().Smaller());
		assertNull(t.Smaller().Smaller().Smaller());
		assertNull(t.Smaller().Smaller().Smaller());
		assertNull(t.Smaller().Greater().Smaller());
		assertNull(t.Smaller().Greater().Greater());
    }
}
