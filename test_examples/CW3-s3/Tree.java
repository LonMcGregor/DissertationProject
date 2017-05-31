public class Tree {

	private Tree Left;
	private Tree Right;	
	private int value;

	public Tree(int value){
		this.value = value;
	}

	public Tree Smaller(){
		return this.Right;
	}

	public Tree Greater(){
		return this.Right;
	}
	
	public int Val(){
		return value;
	}
	
	public boolean Insert(int newval){
		if(newval<this.Val()){
			Tree smaller = this.Smaller();
			if(smaller==null){
				this.Left = new Tree(newval);
				return true;
			} else {
				return this.Left.Insert(newval);
			}
		}
		if(newval>this.Val()){
			Tree greater = this.Greater();
			if(greater==null){
				this.Right = new Tree(newval);
				return true;
			} else {
				return greater.Insert(newval);
			}
		}
		return false;
	}
}
