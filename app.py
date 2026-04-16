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
    QLineEdit
)
import sys


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

    def StyleOption(self, option, index):
        """настройка внешнего вида ячейки"""
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter
        # центровка введенного текста
