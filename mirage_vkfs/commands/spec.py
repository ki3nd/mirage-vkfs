from mirage.commands.spec.types import (CommandSpec, Operand, OperandKind,
                                        Option)

SEARCH_SPEC = CommandSpec(
    options=(
        Option(long="--method", value_kind=OperandKind.TEXT),
        Option(long="--top-k", value_kind=OperandKind.TEXT),
        Option(long="--threshold", value_kind=OperandKind.TEXT),
    ),
    positional=(Operand(kind=OperandKind.TEXT), ),
    rest=Operand(kind=OperandKind.PATH),
)
