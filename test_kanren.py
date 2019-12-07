from pykanren import *

def test_arithmetic():
  x = var()
  
  goal = unify(term(9), term(x) + term(5))

  for r in runGoal(goal):
    print(r)
