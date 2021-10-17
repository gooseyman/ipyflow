# -*- coding: future_annotations -*-
import ast
import logging
import traceback
from typing import TYPE_CHECKING, cast

from nbsafety.analysis.reactive_vars import AugmentedSymbol
from nbsafety.singletons import nbs
from nbsafety.data_model.code_cell import cells
from nbsafety.tracing.ast_eavesdrop import AstEavesdropper
from nbsafety.tracing.stmt_inserter import StatementInserter
from nbsafety.tracing.stmt_mapper import StatementMapper

if TYPE_CHECKING:
    from typing import Dict, Optional, Set, Tuple
    from nbsafety.types import CellId


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class SafetyAstRewriter(ast.NodeTransformer):
    def __init__(self, cell_id: Optional[CellId]):
        self._cell_id: Optional[CellId] = cell_id
        self._reacive_var_positions: Set[Tuple[int, int]] = set()
        self._blocking_var_positions: Set[Tuple[int, int]] = set()

    def register_reactive_var_position(self, sym_type: AugmentedSymbol, lineno: int, col_offset: int) -> None:
        if sym_type == AugmentedSymbol.reactive:
            self._reacive_var_positions.add((lineno, col_offset))
        elif sym_type == AugmentedSymbol.blocking:
            self._blocking_var_positions.add((lineno, col_offset))
        else:
            raise ValueError('augmented symbol prefixed with "%s" not handled yet' % sym_type.marker)

    def visit(self, node: ast.AST):
        assert isinstance(node, ast.Module)
        try:
            mapper = StatementMapper(
                self._cell_id,
                nbs().statement_cache[cells().exec_counter()],
                nbs().ast_node_by_id,
                nbs().parent_node_by_id,
                nbs().reactive_variable_node_ids,
                nbs().reactive_attribute_node_ids,
                nbs().blocking_variable_node_ids,
                nbs().blocking_attribute_node_ids,
                self._reacive_var_positions,
                self._blocking_var_positions,
            )
            orig_to_copy_mapping = mapper(node)
            cells().current_cell().to_ast(override=cast(ast.Module, orig_to_copy_mapping[id(node)]))
            # very important that the eavesdropper does not create new ast nodes for ast.stmt (but just
            # modifies existing ones), since StatementInserter relies on being able to map these
            node = AstEavesdropper(orig_to_copy_mapping).visit(node)
            node = StatementInserter(self._cell_id, orig_to_copy_mapping).visit(node)
        except Exception as e:
            nbs().set_exception_raised_during_execution(e)
            traceback.print_exc()
            raise e
        return node
