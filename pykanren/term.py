from dataclasses import dataclass
from enum import Enum
from typing import Any, Type
import uuid

class Term:
  def __add__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BinaryOp.PLUS)

  def __sub__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BinaryOp.MINUS)

  def __mul__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BinaryOp.TIMES)

  def __floordiv__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BinaryOp.DIV)

  def __mod__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BInaryOp.MOD)

  def __and__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BinaryOp.AND)

  def __or__(lhs, rhs):
    return BinaryExpr(lhs, term(rhs), BinaryOp.OR)


@dataclass(frozen=True)
class Empty(Term):
  def __repr__(self):
    return "None"


@dataclass(frozen=True)
class Value(Term):
  type: Type
  value: Any

  def __repr__(self):
    return f"{self.type}({self.value})"


@dataclass(frozen=True)
class Pair(Term):
  p: Term
  q: Term

  def __repr__(self):
    return f"({self.p}, {self.q})"


@dataclass(frozen=True)
class Var(Term):
  name: str

  def __repr__(self):
    return f"Var({self.name})"


class BinaryOp(Enum):
  PLUS = '+'
  MINUS = '-'
  TIMES = '*'
  DIV = '/'
  MOD = '%'
  AND = '&'
  OR = '|'


@dataclass(frozen=True)
class BinaryExpr(Term):
  lhs: Term
  rhs: Term
  op: BinaryOp

  def __repr__(self):
    return f"{self.lhs} {self.op} {self.rhs}"


def term(v):
  if isinstance(v, Term):
    return v

  if v is None:
    return Empty()

  t = type(v)
  if t is tuple:
    if len(v) != 2:
      raise TypeError("Tuple terms can only have two elements")
    else:
      return Pair(term(v[0]), term(v[1]))

  if t is list:
    return Pair(term(list[0]), term(list[1:]))

  if t not in [bool, str, int, float, tuple, list]:
    raise TypeError(f"Cannot create a term with value of type {t}")

  return Value(t, v)


def var(name=None):
  return Var(name or f"var-{uuid.uuid4()}")

