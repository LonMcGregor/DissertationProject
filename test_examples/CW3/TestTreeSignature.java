import static org.junit.Assert.fail;
import org.junit.Test;

public class TestTreeSignature {

    @Test
    public void signature_check() {
        try {
            Tree t = new Tree(0);
            t.Smaller();
            t.Greater();
            t.Val();
            t.Insert(1);
        } catch (Exception e) {
            fail("Signature of solution does not conform");
        }
    }

}
