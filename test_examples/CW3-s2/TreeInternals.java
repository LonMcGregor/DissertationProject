public class TreeInternals {
    
	public static Tree Smaller(Tree t){
		return t.Left;
	}

	public static Tree Greater(Tree t){
		return t.Right;
	}
	
	public static int Val(Tree t){
		return t.value;
	}
}
