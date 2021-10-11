from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QFileDialog, QDialog
from PySide6.QtGui import QPixmap, QFont, QIcon
import gui
import os
import re
import sys
from PySide6.QtCore import Qt
import asyncio
from typing import Optional
import datetime


class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.path = None
        self.progressBar.setProperty("value", 0)
        self.progressBar.hide()
        now = datetime.datetime.now()
        self.lineEdit_2.setText(str(now.strftime("%d-%m-%Y")))
        self.pushButton.clicked.connect(self.director)
        self.pushButton_2.clicked.connect(self.start)
        self.listWidget.itemDoubleClicked.connect(self.open_file)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.start()
        # строка поиска
        elif event.key() in [QtCore.Qt.Key_F1]:
            self.lineEdit.setFocus()
        # строка даты
        elif event.key() in [QtCore.Qt.Key_F3]:
            self.lineEdit_2.setFocus()
        # искать по дате
        elif event.key() in [QtCore.Qt.Key_F2]:
            if self.checkBox.isChecked() == False:
                self.checkBox.setChecked(True)
            elif self.checkBox.isChecked() == True:
                self.checkBox.setChecked(False)
        # выбор дерриктории
        elif event.key() in [QtCore.Qt.Key_F4]:
            self.director()

    def director(self):
        """Функция выбора директории"""
        self.path = QFileDialog.getExistingDirectory(options=QFileDialog.DontUseNativeDialog)

    def err(self, text):
        """Вывод сообщения об ошибке"""
        self.pushButton_2.setEnabled(True)
        dialog = QDialog()
        dialog.resize(384, 205)
        dialog.setWindowTitle('Ошибка')
        icon = QIcon()
        icon.addPixmap(QPixmap(":/newPrefix/720.png"), QIcon.Normal, QIcon.Off)
        dialog.setWindowIcon(icon)
        self.label = QtWidgets.QLabel(dialog)
        self.label.setGeometry(QtCore.QRect(0, -10, 391, 221))
        self.label.setText("")
        self.label.setPixmap(QPixmap(":/newPrefix/gandalf.png"))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(dialog)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 3910, 20))
        self.label_2.setText(text)
        font = QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def open_file(self):
        if self.checkBox_2.isChecked():
            select = self.listWidget.selectedIndexes()[0].data()
            file = re.search(r"File: (.+)\n", select).group(1)
            try:
                os.startfile(f'start notepad++ "{file}"')
            except OSError:
                text = 'Возможно в имени файла содержаться пробелы или другие символы!'
                return self.err(text)
        else:
            select = self.listWidget.selectedIndexes()[0].data()
            file = re.search(r"File: (.+)\n", select).group(1)
            try:
                os.startfile(f'"{file}"')
            except OSError:
                text = 'Возможно в имени файла содержаться пробелы или другие символы!'
                return self.err(text)

    def list_widget_add_item(self, item):
        self.listWidget.addItem(item)

    def start(self):
        self.progressBar.show()
        self.progressBar.setValue(0)
        self.listWidget.clear()
        self.pushButton_2.setEnabled(False)
        # Проверям что указан путь к файлам
        if self.path is None or self.path == '':
            self.progressBar.hide()
            self.err('Не указано где искать!')
            return
        # Првоеряем что длинна текста 3 или более
        if len(self.lineEdit.text()) < 3:
            self.progressBar.hide()
            return self.err('Поле поиска должно быть >= 3')
        # Если ищем по дате
        if self.checkBox.isChecked():
            date_search = re.search(r'\d\d-\d\d-\d\d\d\d', self.lineEdit_2.text())
            # проверяем что дата указан верно
            if date_search is None:
                self.progressBar.hide()
                return self.err('Указана не корректная дата!')
            # получаем файлы по дате модификации
            files = GetFilesByPath(self.path, self.lineEdit_2.text()).create_files_tuple()
            # проверям что список не пустой
            if files == ():
                self.progressBar.hide()
                return self.err('Файлов за указанную дату не найдено!')
            # запускаем функию поиска
            asyncio.run(self.search(files))
            return
        else:
            # Получаем файлы
            files = GetFilesByPath(self.path).create_files_tuple()
            # Проверяем что они не пусты
            if files == ():
                self.progressBar.hide()
                return self.err('Файлы не найдены!')
            else:
                # запускаем поиск
                asyncio.run(self.search(files))
                return

    async def process_progress_bar(self, value):
        self.progressBar.setValue(value)

    async def search(self, files) -> None:
        """
        Функция поиска текста
        Ищет текст в файле а так же заполняет прогресс бар и лист виджет
        """
        value = len(files) / 100
        text = self.lineEdit.text()
        for file in files:
            file = str(file).replace('/', '\\')
            with open(file, 'r', encoding='utf-8') as fl:
                count = 0
                for line in fl.readlines():
                    if text in line:
                        count += 1
                if count > 0:

                    item = f"╔═══════════════════════════════• ✤ •═══════════════════════════════╗\n" \
                           f"  • Кол-во повторений текста: {count}\n" \
                           f"  • File: {file}\n" \
                           f"╚═════════════════════════════════════════════════════════════════╝"
                    self.listWidget.addItem(item)
            value = self.progressBar.value() + value
            await self.process_progress_bar(value)
        # Включаем кнопку и заполняем прогресс бар
        self.pushButton_2.setEnabled(True)
        await self.process_progress_bar(100)


class GetFilesByPath:
    """Класс который ищетнужные файлы в указанной дирректории"""
    def __init__(self, path, date: Optional[str] = None):
        self.path = path
        self.date = date
        self.files = self.create_files_tuple()

    def _getting_file_path(self) -> tuple:
        """Получаем все файлы в нужной дерриктории"""
        file_list = os.listdir(self.path)  # получение списка файлов
        file_list = [os.path.join(self.path, i) for i in file_list]
        file_list = sorted(file_list, key=os.path.getmtime)  # Сортировка списка
        file_list.reverse()  # Переворачивание списка
        return tuple(file_list)

    def _filtering_files_by_format(self) -> dict:
        """Ищем файлы с нужным расширением и создаем словарь {файл: дата модификации}"""
        files_tuple = self._getting_file_path()
        files_and_modification_date = {}
        for file in files_tuple:
            if re.search(r"\.(txt|log|xml|doc|docx)", file):
                file_create_date = datetime.datetime.fromtimestamp(os.path.getmtime(file))
                files_and_modification_date.update({file: str(file_create_date)})
        return files_and_modification_date

    def create_files_tuple(self) -> tuple:
        """
        Функция сравнения даты модификации файла и даты указанной пользователем.
        Если дата не передана возращает tuple всех файлов
        """
        files_and_modification_date = self._filtering_files_by_format()
        if self.date is None:
            files = []
            for file in files_and_modification_date.keys():
                files.append(file)
            return tuple(files)

        elif '-' in self.date:
            date = self.date.split('-')
            new_date = f'{date[2]}-{date[1]}-{date[0]}'
            # Сравниваем даты
            files = []
            for file, file_date in files_and_modification_date.items():
                if file_date[:10] == new_date:
                    files.append(file)
            return tuple(files)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
