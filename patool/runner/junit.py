def execute_test(tmp_dir, path_solutions, solutions, path_tests, tests):
    pass
    # todo determine test classname
    # todo java -cp .:junit.jar:hamcrest-core.jar org.junit.runner.JUnitCore test_classname
    return -1, "no test run"


def solution_uploaded(solution):
    """a @solution is uploaded, compile
     into relevant executable format"""
    pass
    # todo javac *.java
    # todo mv originals -> compiled


def test_uploaded(test):
    """a @test is uploaded, compile
    and reference junit jars"""
    pass
    # todo javac -cp .:junit.jar *.java
    # todo mv originals -> compiled


def process_results(content):
    """Process @content of results of running test
    to clean up any unwanted information"""
    return content
