from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, TypeVar
from .goal import Goal
from .expressions import evaluate, reverse_evaluate_lhs, reverse_evaluate_rhs
from .term import BinaryExpr, Empty, Pair, Term, Value, Var, var


Substitutions = Dict[Term, Term]
T = TypeVar('T')


def flatmap(xs: Iterable[T], f: Callable[[T], Iterable[T]]) -> Iterable[T]:
  for x in xs:
    for y in f(x):
      yield y


def union(x: dict, y: dict) -> dict:
  z = dict(x)
  z.update(y)
  return z


@dataclass(frozen=True)
class State:
  substitutions: Dict[Var,Term] = field(default_factory=dict)
  vars: List[Var] = field(default_factory=list)


  def substituting(self, new_subs: Dict[Term, Term]) -> "State":
    return State(union(self.substitutions, new_subs), self.vars)


  def with_new_var(self, consumer: Callable[[Term], Goal]) -> Iterable["State"]:
    new_var = var()
    new_state = State(self.substitutions, self.vars + [new_var])
    goal = consumer(new_var)
    return goal(new_state)


  def walk(self, t: Term) -> Term:
    def substitue(term: Term) -> Term:
      sub = self.substitutions.get(term)
      return term if sub is None else self.walk(sub)

    if t is Var:
      return substitue(t)
    elif t is Pair:
      return Pair(substitue(t.lhs), substitue(t.rhs))
    elif t is BinaryExpr:
      return evaluate(substitue(t.lhs), t.op, substitue(t.rhs))
    else:
      return t


  def maybe_unify(self, lhs: Term, rhs: Term) -> (bool, Iterable[Substitutions]):
      lhs_t = type(lhs)
      rhs_t = type(rhs)
      
      if lhs_t is Empty and rhs_t is Empty:
        return (True, [])

      elif lhs_t is Value and rhs_t is Value:
        return (lhs.value == rhs.value, [])
      
      elif lhs_t is Pair and rhs_t is Pair:
        ps_ok, ps = self.maybe_unify(lhs.p, rhs.p)
        if not ps_ok: return (False, None)
        qs_ok, qs = self.maybe_unify(rhs.q, rhs.q)
        if not qs_ok: return (False, None)
        return (True, flatmap(ps, lambda p: (union(p,q) for q in qs)))

      elif lhs_t is Var:
        return (True, [{ lhs: rhs }])

      elif rhs_t is Var:
        return (True, [{ rhs: lhs }])

      elif lhs_t is BinaryExpr:
        if type(lhs.lhs) is Var:
          r = reverse_evaluate_lhs(lhs.rhs, lhs.op, rhs)
          return (r is not None, [{ lhs.lhs: r }])
        
        elif type(lhs.rhs) is Var:
          r = reverse_evaluate_rhs(lhs.lhs, lhs.op, rhs)
          return (r is not None, [{ lhs.rhs: r }])

      elif rhs_t is BinaryExpr:
        if type(rhs.lhs) is Var:
          r = reverse_evaluate_lhs(rhs.rhs, rhs.op, lhs)
          return (r is not None, [{ rhs.lhs: r }])

        elif type(rhs.rhs) is Var:
          r = reverse_evaluate_rhs(rhs.lhs, rhs.op, lhs)
          return (r is not None, [{ rhs.rhs: r }])

      return (False, [])


  def unify(self, lhs: Term, rhs: Term) -> Iterable["State"]:
    unified, new_substitutions = self.maybe_unify(self.walk(lhs), self.walk(rhs))
    if unified:
      for s in new_substitutions:
        yield self.substituting(s)


  def disunify(self, lhs: Term, rhs: Term) -> Iterable["State"]:
    unified, new_substitutions = self.maybe_unify(self.walk(lhs), self.walk(rhs))
    if not unified:
      yield self


  def __repr__(self):
    return "[%s]" % ",".join(f"{x}={y}" for x,y in self.substitutions.items())
