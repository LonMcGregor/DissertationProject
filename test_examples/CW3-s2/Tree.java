public class Tree {

	public Tree Left;
	public Tree Right;	
	public int value;

	public Tree(int value){
        this.value = value;
	}

	public Tree Smaller(){
        return TreeInternals.Smaller(this);
	}

	public Tree Greater(){
        return TreeInternals.Greater(this);
	}
	
	public int Val(){
        return TreeInternals.Val(this);
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
