import pytest
def add(a,b):
    return a + b
def divise(a,b):
    if b ==0:
        raise ZeroDivisionError()
    return a/b
def test_add():
    assert add(1,2)==3
def test_div():
    assert divise(1,2)==0.5
def test_div_zero():
    with pytest.raises(ZeroDivisionError):
            divise(1,0)