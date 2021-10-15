# -*- coding: future_annotations -*-
from typing import cast, TYPE_CHECKING
from nbsafety.run_mode import ExecutionMode
from nbsafety.singletons import nbs
from nbsafety.tracing.mutation_event import resolve_mutating_method
from nbsafety.utils import CommonEqualityMixin

if TYPE_CHECKING:
    from typing import Optional
    from nbsafety.analysis.symbol_ref import Atom
    from nbsafety.data_model.data_symbol import DataSymbol


class ResolvedDataSymbol(CommonEqualityMixin):
    def __init__(
        self,
        dsym: DataSymbol,
        atom: Atom,
        next_atom: Optional[Atom],
        liveness_timestamp: Optional[int] = None,
    ) -> None:
        self.dsym = dsym
        self.atom = atom
        self.next_atom = next_atom
        self.liveness_timestamp = liveness_timestamp

    def __hash__(self):
        return hash((
            self.dsym,
            self.atom,
            self.next_atom,
            self.liveness_timestamp,
        ))

    @property
    def is_called(self):
        return self.atom.is_callpoint

    @property
    def is_last(self):
        return self.next_atom is None

    @property
    def is_reactive(self):
        return self.atom.is_reactive or nbs().mut_settings.exec_mode == ExecutionMode.REACTIVE

    @property
    def is_dead(self):
        return self.liveness_timestamp is None

    @property
    def is_live(self):
        return not self.is_dead

    @property
    def is_deep(self) -> bool:
        # for live symbols, if it is used in its entirety
        assert self.is_live
        if self.is_reactive:
            return True
        if self.next_atom is None:
            return True
        elif not self.next_atom.is_callpoint:
            return False
        elif self.is_mutating:  # self.next_atom.is_callpoint
            return False
        else:
            return True

    @property
    def is_shallow(self) -> bool:
        # for live symbols, if only a portion (attr or subscript) is used
        assert self.is_live
        return not self.is_deep

    @property
    def is_mutating(self) -> bool:
        assert self.is_live
        if not self.next_atom.is_callpoint:
            return False
        return resolve_mutating_method(self.dsym.obj, cast(str, self.next_atom.value)) is not None

    @property
    def is_unsafe(self) -> bool:
        assert self.is_live
        if self.next_atom is None:
            return False
        if self.next_atom.is_callpoint:
            if self.is_mutating and self.is_reactive:
                return True
            else:
                return False
        if isinstance(self.dsym.obj, (list, tuple)) and isinstance(self.next_atom.value, int) and self.next_atom.value >= len(self.dsym.obj):
            return True
        if isinstance(self.dsym.obj, dict) and self.next_atom.value not in self.dsym.obj:
            return True
        if not isinstance(self.dsym.obj, (dict, list, tuple)) and isinstance(self.next_atom.value, str) and not hasattr(self.dsym.obj, self.next_atom.value):
            # TODO: fix this once we can distinguish between attrs and subscripts in the chain
            return True
        return False

    def is_stale_at_position(self, pos: int):
        return self.dsym.is_stale_at_position(pos)