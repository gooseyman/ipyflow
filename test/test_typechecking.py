# -*- coding: future_annotations -*-
import logging
from typing import TYPE_CHECKING

from nbsafety.singletons import nbs
from nbsafety.data_model.code_cell import cells
from test.utils import make_safety_fixture, skipif_known_failing

if TYPE_CHECKING:
    from typing import Set
    from nbsafety.types import CellId

logging.basicConfig(level=logging.ERROR)

# Reset dependency graph before each test
# _safety_fixture, run_cell_ = make_safety_fixture(trace_messages_enabled=True)
_safety_fixture, run_cell_ = make_safety_fixture(mark_typecheck_failures_unsafe=True)


def run_cell(cell, cell_id=None, **kwargs):
    """Mocks the `change active cell` portion of the comm protocol"""
    if cell_id is not None:
        nbs().handle({
            'type': 'change_active_cell',
            'active_cell_id': cell_id
        })
    run_cell_(cell, **kwargs)


def get_cell_ids_needing_typecheck() -> Set[CellId]:
    return {cell.cell_id for cell in cells().all_cells_most_recently_run_for_each_id() if cell.needs_typecheck}


def test_int_change_to_str_triggers_typecheck():
    run_cell('a = 1', 1)
    assert not get_cell_ids_needing_typecheck()
    run_cell('b = 2', 2)
    assert not get_cell_ids_needing_typecheck()
    run_cell('logging.info(a + b)', 3)
    assert not get_cell_ids_needing_typecheck()
    run_cell('b = "b"', 4)
    assert get_cell_ids_needing_typecheck() == {3}
    nbs().check_and_link_multiple_cells()
    assert not get_cell_ids_needing_typecheck()
    assert not cells().from_id(3)._checker_result.typechecks
