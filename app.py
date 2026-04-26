from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QHBoxLayout,
    QPushButton
)
import sys
import numpy as np
from abc import ABC, abstractmethod


class NumDelegate(QStyledItemDelegate):
    """
    менеджер для ячеек таблицы, центрирует пользовательский ввод и не дает вводить что то, кроме цифр,
    точки, запятой, знака минуса
    """
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignCenter) 
        # центровка во время ввода
        regex = QRegularExpression(r"^-?\d+([.,]\d+)?$")
        # разрешение регулярным выражением
        validator = QRegularExpressionValidator(regex)
        editor.setValidator(validator)
        return editor
    def initStyleOption(self, option, index):
        """настройка внешнего вида ячейки"""
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter
        # центровка введенного текста
    
class InputTable(QTableWidget):
    """
    кастомная таблица для ввода данных
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # super используется, чтобы не переписывать код в случае смены класса
        # parent=None для возможности существования таблицы как самостоятельного объекта,
        # так и части дерева наследования редактора ui
        self._setup_base()

    def _setup_base(self):
        """
        создание таблицы c первым столбцом по умолчанию
        """
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["№"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # растяжение таблицы на все возможное пространство
        self.setItemDelegate(NumDelegate(self))

    def set_columns(self, column_names: list[str]):
        """
        пользовательская настройка столбцов
        """
        self.setRowCount(0)
        # сброс таблицы
        self.setColumnCount(len(column_names) + 1)
        headers = ["№"] + column_names
        self.setHorizontalHeaderLabels(headers)

    def add_data_row(self):
        """
        добавление строки, нумерация строк в первом столбце
        """
        row_index = self.rowCount()
        self.insertRow(row_index)
        num_item = QTableWidgetItem(str(row_index + 1))
        # создание ячейки с номером измерения
        num_item.setTextAlignment(Qt.AlignCenter)
        # центрирование значения
        num_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        # защита от дурака, чтобы пользователь не ломал нумерацию
        self.setItem(row_index, 0, num_item)
        # установка ячейки в 1 столбец

    def remove_data_row(self):
        """
        удаление выделенной строки, если нет выделения, удаляет последнюю
        """
        if self.rowCount() == 0:
            return
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
        else:
            self.removeRow(self.rowCount() - 1)
        self._update_numbering()

    def keyPressEvent(self, event):
        """
        удалениеданных из ячейки
        """
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            selected_items = self.selectedItems()
            for item in selected_items:
                if item.column() != 0:
                    # проверка, чтобы не стереть нумерацию
                    item.setText("")
        else:
            # чтобы не ломать остальные клавишы, передаем их родительскому классу
            super().keyPressEvent(event)

    def _update_numbering(self):
        """
        пересчет нумерации
        """
        for row in range(self.rowCount()):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.setItem(row, 0, num_item)

    def get_column_data(self, col_index):
        """
        получение данных из столбца с игнорированием пустых ячеек
        """
        data = []
        for row in range(self.rowCount()):
            item = self.item(row, col_index)
            if item and item.text().strip():
                val_str = item.text().replace(",", ".")
                data.append(float(val_str))
        return data
    

class test(QMainWindow):
    """тест вышенаписанного"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("тест таблицы")
        self.resize(500, 400)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.table = InputTable()
        self.table.set_columns(["x", "y"])
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("добавление строки")
        self.btn_add.clicked.connect(self.table.add_data_row)
        self.btn_print = QPushButton("вывод данных")
        self.btn_print.clicked.connect(self.print_data)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_print)
        layout.addLayout(btn_layout)
        self.table.add_data_row()
        self.table.add_data_row()
        btn_layout = QHBoxLayout()
        self.btn_remove = QPushButton("удаление строки")
        self.btn_remove.clicked.connect(self.table.remove_data_row)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_print)
        
        layout.addLayout(btn_layout)
    def print_data(self):
        """вывод данных"""
        print("-" * 20)
        try:
            # 1 = x, 2 = y
            x_data = self.table.get_column_data(1)
            y_data = self.table.get_column_data(2)
            print("Массив x:", x_data)
            print("Массив y:", y_data)
        except ValueError as e:
            print("Ошибка конвертации:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window =  test()
    window.show()
    sys.exit(app.exec())
