from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, TypeVar, Union
    from nbsafety.analysis.attr_symbols import SymbolRef
    from nbsafety.data_model.timestamp import Timestamp
    CellId = Union[str, int]
    SupportedIndexType = Union[str, int, Tuple[Union[str, int], ...]]
    TimestampOrCounter = TypeVar('TimestampOrCounter', Timestamp, int)
