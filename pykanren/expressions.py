import operator
from typing import Iterable, Optional
from .term import BinaryOp, Term, term

OPERATOR_IMPLS = {
  BinaryOp.PLUS: operator.add,
  BinaryOp.MINUS: operator.sub,
  BinaryOp.TIMES: operator.mul,
  BinaryOp.DIV: operator.floordiv,
  BinaryOp.MOD: operator.mod,
  BinaryOp.AND: operator.and_,
  BinaryOp.OR: operator.or_
}

def evaluate(lhs: Term, op: BinaryOp, rhs: Term) -> Optional[Term]:
  return term(OPERATOR_IMPLS[op](lhs.value, rhs.value))


REVERSE_LHS_IMPLS = {
  BinaryOp.PLUS: operator.sub,
  BinaryOp.MINUS: operator.add,
  BinaryOp.TIMES: operator.floordiv,
  BinaryOp.DIV: operator.mul,
  BinaryOp.MOD: lambda: None,
  BinaryOp.AND: lambda x, y: x if y else [False, True],
  BinaryOp.OR: lambda x, y: [False, True] if x else y
}

def reverse_evaluate_lhs(rhs: Term, op: BinaryOp, result: Term) -> Optional[Iterable[Term]]:
  lhs = REVERSE_LHS_IMPLS[op](rhs.value, result.value)
  if lhs is None:
    return None
  elif type(lhs) is list:
    yield from (term(v) for v in lhs)
  else:
    yield term(lhs) 


REVERSE_RHS_IMPLS = {
  BinaryOp.PLUS: operator.sub,
  BinaryOp.MINUS: lambda x,y: -(x - y),
  BinaryOp.TIMES: operator.floordiv,
  BinaryOp.DIV: lambda x,y: y // x,
  BinaryOp.MOD: lambda: None,
  BinaryOp.AND: lambda x, y: x if y else [False, True],
  BinaryOp.OR: lambda x, y: x if not y else [False, True]
}

def reverse_evaluate_rhs(lhs: Term, op: BinaryOp, result: Term) -> Optional[Iterable[Term]]:
  rhs = REVERSE_RHS_IMPLS[op](lhs.value, result.value)
  if rhs is None:
    return None
  elif type(rhs) is list:
    yield from (term(v) for v in rhs)
  else:
    yield term(rhs) 
