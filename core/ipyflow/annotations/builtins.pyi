# -*- coding: utf-8 -*-
from ipyflow.tracing.external_call_handler import (
    ListAppend,
    ListExtend,
    ListInsert,
    ListPop,
    ListRemove,
    MutatingMethodEventNotYetImplemented,
    NamespaceClear,
    NoopCallHandler,
)

class dict:
    def clear(self) -> NamespaceClear: ...
    def pop(self) -> MutatingMethodEventNotYetImplemented: ...
    def popitem(self) -> MutatingMethodEventNotYetImplemented: ...
    def setdefault(self) -> MutatingMethodEventNotYetImplemented: ...
    def update(self) -> MutatingMethodEventNotYetImplemented: ...

class list:
    def __getitem__(self) -> NoopCallHandler: ...
    def append(self) -> ListAppend: ...
    def clear(self) -> NamespaceClear: ...
    def extend(self) -> ListExtend: ...
    def insert(self) -> ListInsert: ...
    def remove(self) -> ListRemove: ...
    def pop(self) -> ListPop: ...

class set:
    def clear(self) -> MutatingMethodEventNotYetImplemented: ...
    def difference_update(self) -> MutatingMethodEventNotYetImplemented: ...
    def discard(self) -> MutatingMethodEventNotYetImplemented: ...
    def intersection_update(self) -> MutatingMethodEventNotYetImplemented: ...
    def pop(self) -> MutatingMethodEventNotYetImplemented: ...
    def remove(self) -> MutatingMethodEventNotYetImplemented: ...
    def symmetric_difference_update(self) -> MutatingMethodEventNotYetImplemented: ...
    def update(self) -> MutatingMethodEventNotYetImplemented: ...
