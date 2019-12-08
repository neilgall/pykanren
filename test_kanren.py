from pykanren import *

# @goal
# def what_plus_5_is_9(x):
#   return x + 5 = 9


def test_arithmetic():
  x = var()
  
  goal = unify(term(9), term(x) + term(5))

  for s in runGoal(goal):
    for k,v in s.substitutions.items():
      print(f"{k} = {list(v)}")
