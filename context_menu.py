from PyQt5.QtWidgets import QMenu, QAction, QApplication


def open_context_menu(self, pos):
    menu = QMenu()
    copy_action = QAction("Copy", self)
    copy_action.triggered.connect(self.copy_selected_row)
    menu.addAction(copy_action)
    menu.exec_(self.table.viewport().mapToGlobal(pos))


def copy_selected_row(self):
    selected = self.table.selectedItems()
    if selected:
        row = selected[0].row()
        data = "\t".join(
            self.table.item(row, col).text() for col in range(self.table.columnCount())
        )
        QApplication.clipboard().setText(data)
