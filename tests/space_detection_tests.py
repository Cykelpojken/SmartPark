import pytest
def test_answer(cmdopt):
    var = 0
    if cmdopt == "type1":
        print("first")
        var = 0
    elif cmdopt == "type2":
        print("second")
        assert 1
    #assert var == 1  # to see what was printed