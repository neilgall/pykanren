from typing import Callable, Iterator, List
from .goal import Goal
from .term import Term
from .microkanren import State


def unify(lhs, rhs):
  def goal(state):
    return state.unify(lhs, rhs)
  return goal


def disunify(lhs, rhs):
  def goal(state):
    return state.disunify(lhs, rhs)
  return goal


def fresh(f: Callable[[Term], Goal]) -> Goal:
  def call(state: State) -> Iterator[State]:
    return state.with_new_var(f)
  return call


def runGoal(goal: Goal) -> Iterator[State]:
  return goal(State())
