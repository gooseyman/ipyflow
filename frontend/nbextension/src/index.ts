
import '../style/index.css';
// import "jqueryui";

const waitingClass = 'waiting-cell';
const readyClass = 'ready-cell';
const readyMakingClass = 'ready-making-cell';
const readyMakingInputClass = 'ready-making-input-cell';
const linkedWaitingClass = 'linked-waiting';
const linkedReadyClass = 'linked-ready';
const linkedReadyMakingClass = 'linked-ready-making';

const cleanup = new Event('cleanup');

const getCellInputSection = (elem: HTMLElement) => {
    if (elem === null) {
        return null;
    }
    if (elem.firstElementChild === null) {
        return null;
    }
    if (elem.firstElementChild.firstElementChild === null) {
        return null;
    }
    return elem.firstElementChild.firstElementChild.firstElementChild;
};

const getCellOutputSection = (elem: HTMLElement) => {
    if (elem === null) {
        return null;
    }
    if (elem.children.item(1) === null) {
        return null;
    }
    return elem.children.item(1).firstElementChild;
};

const attachCleanupListener = (elem: any, evt: "mouseover" | "mouseout", listener: any) => {
    const cleanupListener = () => {
        elem.removeEventListener(evt, listener);
        elem.removeEventListener('cleanup', cleanupListener);
    };
    elem.addEventListener(evt, listener);
    elem.addEventListener('cleanup', cleanupListener);
};

const addReadyInteraction = (elem: Element,
                                   linkedElem: Element,
                                   evt: "mouseover" | "mouseout",
                                   add_or_remove: "add" | "remove",
                                   css: string) => {
    if (elem === null) {
        return;
    }
    const listener = () => {
        linkedElem.classList[add_or_remove](css);
    };
    attachCleanupListener(elem, evt, listener);
};

const addReadyInteractions = (elem: HTMLElement) => {
    addReadyInteraction(
        getCellInputSection(elem), elem, 'mouseover', 'add', linkedReadyClass
    );
    addReadyInteraction(
        getCellInputSection(elem), elem, 'mouseout', 'remove', linkedReadyClass
    );

    addReadyInteraction(
        getCellOutputSection(elem), elem, 'mouseover', 'add', linkedReadyMakingClass
    );
    addReadyInteraction(
        getCellOutputSection(elem), elem, 'mouseout', 'remove', linkedReadyMakingClass
    );
};

 const addUnsafeCellInteraction = (elem: Element, linkedElems: [string],
                                   cellsById: {[id: string]: HTMLElement},
                                   evt: "mouseover" | "mouseout",
                                   add_or_remove: "add" | "remove",
                                   css: string) => {
     const listener = () => {
         for (const linkedId of linkedElems) {
             cellsById[linkedId].classList[add_or_remove](css);
         }
     };
     elem.addEventListener(evt, listener);
     attachCleanupListener(elem, evt, listener);
 };

const clearCellState = (Jupyter: any) => {
    Jupyter.notebook.get_cells().forEach((cell: any, idx: any) => {
        cell.element[0].classList.remove(waitingClass);
        cell.element[0].classList.remove(readyMakingClass);
        cell.element[0].classList.remove(readyClass);
        cell.element[0].classList.remove(readyMakingInputClass);
        cell.element[0].classList.remove(linkedWaitingClass);
        cell.element[0].classList.remove(linkedReadyClass);
        cell.element[0].classList.remove(linkedReadyMakingClass);

        const cellInput = getCellInputSection(cell.element[0]);
        if (cellInput !== null) {
            cellInput.dispatchEvent(cleanup);
        }

        const cellOutput = getCellOutputSection(cell.element[0]);
        if (cellOutput !== null) {
            cellOutput.dispatchEvent(cleanup);
        }
    });
};

const gatherCellContentsById = (Jupyter: any) => {
    const content_by_cell_id: {[id: string]: string} = {};
    Jupyter.notebook.get_cells().forEach((cell: any) => {
        if (cell.cell_type !== 'code') {
            return;
        }
        content_by_cell_id[cell.cell_id] = cell.get_text();
    });
    return content_by_cell_id;
}

const connectToComm = (Jupyter: any) => {
    const comm = Jupyter.notebook.kernel.comm_manager.new_comm('ipyflow');
    const onExecution = (evt: any, data: {cell: any}) => {
        if (data.cell.notebook !== Jupyter.notebook) {
            return;
        }
        data.cell.element[0].classList.remove(readyClass);
        data.cell.element[0].classList.remove(readyMakingInputClass);
        comm.send({
            type: 'compute_exec_schedule',
            executed_cell_id: data.cell.cell_id,
            content_by_cell_id: gatherCellContentsById(Jupyter)
        });
    };
    const onSelect = (evt: any, data: {cell: any}) => {
        let active_cell_order_idx: number = null;
        let cur_idx = 0;
        Jupyter.notebook.get_cells().forEach((cell: any) => {
            if (data.cell.cell_id === cell.cell_id) {
                active_cell_order_idx = cur_idx;
            }
            cur_idx += 1;
        });
        comm.send({
            type: 'change_active_cell',
            active_cell_id: data.cell.cell_id,
            active_cell_order_idx: active_cell_order_idx,
        });
    };
    comm.on_msg((msg: any) => {
        // console.log('comm got msg: ');
        // console.log(msg.content.data)
        if (msg.content.data.type == 'establish') {
            Jupyter.notebook.events.on('execute.CodeCell', onExecution);
            Jupyter.notebook.events.on('select.Cell', onSelect);
        } else if (msg.content.data.type === 'compute_exec_schedule') {
            clearCellState(Jupyter);
            const waitingCells: any = msg.content.data['waiting_cells'];
            const readyCells: any = msg.content.data['ready_cells'];
            const waiterLinks: any = msg.content.data['waiter_links'];
            const readyMakerLinks: any = msg.content.data['ready_maker_links'];
            const cellsById: {[id: string]: HTMLElement} = {};
            Jupyter.notebook.get_cells().forEach((cell: any) => {
                cellsById[cell.cell_id] = cell.element[0];
            });
            for (const [id, elem] of Object.entries(cellsById)) {
                if (waitingCells.indexOf(id) > -1) {
                    elem.classList.add(waitingClass);
                    elem.classList.add(readyClass);
                    elem.classList.remove(readyMakingInputClass);
                } else if (readyCells.indexOf(id) > -1) {
                    elem.classList.add(readyMakingInputClass);
                    elem.classList.add(readyClass);

                    addReadyInteractions(elem);
                }

                if (waiterLinks.hasOwnProperty(id)) {
                    addUnsafeCellInteraction(
                        getCellInputSection(elem), waiterLinks[id], cellsById,
                        'mouseover', 'add', linkedReadyMakingClass
                    );

                    addUnsafeCellInteraction(
                        getCellOutputSection(elem), waiterLinks[id], cellsById,
                        'mouseover', 'add', linkedReadyMakingClass
                    );

                    addUnsafeCellInteraction(
                        getCellInputSection(elem), waiterLinks[id], cellsById,
                        'mouseout', 'remove', linkedReadyMakingClass
                    );

                    addUnsafeCellInteraction(
                        getCellOutputSection(elem), waiterLinks[id], cellsById,
                        'mouseout', 'remove', linkedReadyMakingClass
                    );
                }

                if (readyMakerLinks.hasOwnProperty(id)) {
                    elem.classList.add(readyMakingClass);
                    elem.classList.add(readyClass);
                    addReadyInteractions(elem);
                    addUnsafeCellInteraction(
                        getCellInputSection(elem), readyMakerLinks[id], cellsById,
                        'mouseover', 'add', linkedWaitingClass
                    );

                    addUnsafeCellInteraction(
                        getCellInputSection(elem), readyMakerLinks[id], cellsById,
                        'mouseover', 'add', linkedReadyClass,
                    );

                    addUnsafeCellInteraction(
                        getCellInputSection(elem), readyMakerLinks[id], cellsById,
                        'mouseout', 'remove', linkedWaitingClass
                    );

                    addUnsafeCellInteraction(
                        getCellInputSection(elem), readyMakerLinks[id], cellsById,
                        'mouseout', 'remove', linkedReadyClass
                    );
                }
            }
        }
    });
    comm.send({
        type: 'compute_exec_schedule',
        content_by_cell_id: gatherCellContentsById(Jupyter)
    });
    return () => {
        clearCellState(Jupyter);
        Jupyter.notebook.events.unbind('execute.CodeCell', onExecution);
        Jupyter.notebook.events.unbind('select.Cell', onSelect);
    };
}

__non_webpack_require__([
  'base/js/namespace'
], function load_ipython_extension(Jupyter: any) {
    // console.log('This is the current notebook application instance:', Jupyter.notebook);
    Jupyter.notebook.events.on('kernel_ready.Kernel', () => {
        const commDisconnectHandler = connectToComm(Jupyter);
        Jupyter.notebook.events.on('spec_changed.Kernel', () => {
            // console.log('kernel changed');
            commDisconnectHandler();
        });
    });
});
