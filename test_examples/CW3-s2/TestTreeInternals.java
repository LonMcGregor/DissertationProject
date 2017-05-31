import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import org.junit.Test;

public class TestTreeInternals {

    @Test
    public static Tree makeAndCheckTree(int val) {
        Tree t = new Tree(val);
		assertEquals(t.Val(),val);
		assertNotNull(t.Smaller());
        return t;
    }

}
