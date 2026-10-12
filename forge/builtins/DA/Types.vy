from typing import Generic, TypeVar

from forge.models import Optional, variant
from forge.builtins import DamlCaseAccessor, no_derive

A = TypeVar("A")
B = TypeVar("B")
T1 = TypeVar("T1")
T10 = TypeVar("T10")
T11 = TypeVar("T11")
T12 = TypeVar("T12")
T13 = TypeVar("T13")
T14 = TypeVar("T14")
T15 = TypeVar("T15")
T16 = TypeVar("T16")
T17 = TypeVar("T17")
T18 = TypeVar("T18")
T19 = TypeVar("T19")
T2 = TypeVar("T2")
T20 = TypeVar("T20")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")


@no_derive
@variant
class Either(Generic[A, B]):
    def Left(value: A): pass
    def Right(value: B): pass


@no_derive
struct Tuple2(Generic[T1, T2]):
    _1: T1
    _2: T2


@no_derive
struct Tuple3(Generic[T1, T2, T3]):
    _1: T1
    _2: T2
    _3: T3


@no_derive
struct Tuple4(Generic[T1, T2, T3, T4]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4


@no_derive
struct Tuple5(Generic[T1, T2, T3, T4, T5]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5


@no_derive
struct Tuple6(Generic[T1, T2, T3, T4, T5, T6]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6


@no_derive
struct Tuple7(Generic[T1, T2, T3, T4, T5, T6, T7]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7


@no_derive
struct Tuple8(Generic[T1, T2, T3, T4, T5, T6, T7, T8]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8


@no_derive
struct Tuple9(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9


@no_derive
struct Tuple10(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10


@no_derive
struct Tuple11(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11


@no_derive
struct Tuple12(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12


@no_derive
struct Tuple13(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13


@no_derive
struct Tuple14(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14


@no_derive
struct Tuple15(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14
    _15: T15


@no_derive
struct Tuple16(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14
    _15: T15
    _16: T16


@no_derive
struct Tuple17(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14
    _15: T15
    _16: T16
    _17: T17


@no_derive
struct Tuple18(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14
    _15: T15
    _16: T16
    _17: T17
    _18: T18


@no_derive
struct Tuple19(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14
    _15: T15
    _16: T16
    _17: T17
    _18: T18
    _19: T19


@no_derive
struct Tuple20(Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20]):
    _1: T1
    _2: T2
    _3: T3
    _4: T4
    _5: T5
    _6: T6
    _7: T7
    _8: T8
    _9: T9
    _10: T10
    _11: T11
    _12: T12
    _13: T13
    _14: T14
    _15: T15
    _16: T16
    _17: T17
    _18: T18
    _19: T19
    _20: T20


@DamlCaseAccessor("Left")
def left(value: Either[A, B]) -> Optional[A]:
    pass


@DamlCaseAccessor("Right")
def right(value: Either[A, B]) -> Optional[B]:
    pass
