
import org.junit.Test;

public class TestTree {

    @Test
    public void create() {
        Tree t = new Tree(4);
		assertEquals(t.Val(),4);
		assertNull(t.Smaller());
		assertNull(t.Greater());
    }

}
