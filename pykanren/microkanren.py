from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Optional
from .goal import Goal
from .expressions import evaluate, reverse_evaluate_lhs, reverse_evaluate_rhs
from .term import BinaryExpr, Pair, Term, Var, var


def union(x: dict, y: dict) -> dict:
  z = dict(x)
  z.update(y)
  return z


States = Iterator["State"]


@dataclass
class State:
  subtitutions: Dict[Var,Term] = field(default_factory=dict)
  vars: List[Var] = field(default_factory=list)


  def subtituting(self, new_subs: Dict[Term, Term]) -> "State":
    return State(union(self.subtitutions, new_subs), self.vars)


  def with_new_var(self, consumer: Callable[[Term], Goal]) -> States:
    new_var = var()
    new_state = State(self.subtitutions, self.vars + [new_var])
    goal = consumer(new_var)
    return goal(new_state)


  def walk(self, t: Term) -> Term:
    def substitue(term: Term) -> Term:
      sub = self.subtitutions.get(term)
      return term if sub is None else self.walk(sub)

    if t is Var:
      return substitue(t)
    elif t is Pair:
      return Pair(substitue(t.lhs), substitue(t.rhs))
    elif t is BinaryExpr:
      return evaluate(substitue(t.lhs), t.op, substitue(t.rhs))
    else:
      return t


  def maybe_unify(self, lhs: Term, rhs: Term) -> Optional[Callable[[], States]]:
    def unified() -> States:
      yield from ()

    def state(subs: Dict[Term, Term]) -> Callable[[], States]:
      def call():
        yield subs

      lhs_t = type(lhs)
      rhs_t = type(rhs)
      
      if lhs_t is Empty and rhs_t is Empty:
        return unified

      elif lhs_t is Value and rhs_t is Value:
        return unified if lhs.value == rhs.value else None
      
      elif lhs_t is Pair and rhs_t is Pair:
        ps = self.maybe_unify(lhs.p, rhs.p)
        if ps is None: return None
        qs = self.maybe_unify(rhs.q, rhs.q)
        if qs is None: return None
        for p in ps():
          for q in qs():
            return state(union(p, q))

      elif lhs_t is Var:
        return state({ lhs: rhs })

      elif rhs_t is Var:
        return state({ rhs: lhs })

      elif lhs_t is BinaryExpr:
        if type(lhs.lhs) is Var:
          r = reverse_evaluate_lhs(lhs.rhs, lhs.op, rhs)
          return None if r is None else state({ lhs.lhs: r })
        
        elif type(lhs.rhs) is Var:
          r = reverse_evaluate_rhs(lhs.lhs, lhs.op, rhs)
          return None if r is None else state({ lhs.rhs: r })

      elif rhs_t is BinaryExpr:
        if type(rhs.lhs) is Var:
          r = reverse_evaluate_lhs(rhs.rhs, rhs.op, lhs)
          return None if r is None else state({ rhs.lhs: r })

        elif type(rhs.rhs) is Var:
          r = reverse_evaluate_rhs(rhs.lhs, rhs.op, lhs)
          return None if r is None else state({ rhs.rhs: r })


  def unify(self, lhs: Term, rhs: Term) -> States:
    unified = self.maybe_unify(self.walk(lhs), self.walk(rhs))
    if unified is None:
      yield from ()
    else:
      yield from (this.subtituting(s) for s in unified())


  def disunify(self, lhs: Term, rhs: Term) -> States:
    unified = self.maybe_unify(self.walk(lhs), self.walk(rhs))
    if unified is None:
      yield this
    else:
      yield from ()

  def __repr__(self):
    return "[%s]" % ",".join(f"%x=%y" for x,y in self.subtitutions)
