from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QFileDialog, QDialog
from PySide6.QtGui import QPixmap, QFont, QIcon
import gui
import os
import datetime
import re
import sys
from PySide6.QtCore import Qt
import asyncio
import subprocess


class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.path = None
        self.list_file = []
        self.progressBar.setProperty("value", 0)
        self.progressBar.hide()
        self.pushButton.clicked.connect(self.director)
        self.pushButton_2.clicked.connect(self.preparation_for_the_search)
        self.listWidget.itemDoubleClicked.connect(self.open_file)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.preparation_for_the_search()
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
        self.progressBar.setProperty("value", 0)
        self.progressBar.hide()
        self.listWidget.clear()

    def err(self, text):
        """Вывод сообщения об ошибке"""
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
        self.label_2.setGeometry(QtCore.QRect(0, 0, 3910, 20 ))
        self.label_2.setText(text)
        font = QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def getting_file_path(self) -> list:
        """Получаем все файлы в нужной дерриктории"""
        file_list = os.listdir(self.path)  # получение списка файлов
        file_list = [os.path.join(self.path, i) for i in file_list]
        file_list = sorted(file_list, key=os.path.getmtime)  # Сортировка списка
        file_list.reverse()  # Переворачивание списка
        return file_list

    def dir_file(self) -> list:
        """Заполнение списка нужными файлами"""
        file_list = self.getting_file_path()
        list_text_date_file = []  # Список нужных фалов с датой модификации
        for i in file_list:
            if ".txt" in str(i).lower() or ".log" in str(i).lower() or ".xml" in str(i).lower() \
                    or ".doc" in str(i).lower() or ".docx" in str(i).lower():
                # Получение даты модификации файла
                file_create_date = datetime.datetime.fromtimestamp(os.path.getmtime(i))
                list_text_date_file.append(f"{str(file_create_date)}$$${i}")
        return list_text_date_file

    def date_comparison(self, list_text_date_file: list) -> list:
        """
        Функция сравнения даты модификации файла и даты указанной пользователем
        """
        if self.lineEdit_2.text() == '':
            return list_text_date_file
        data = str(self.lineEdit_2.text()).split('-')  # Разбиение даты
        data = f'{data[2]}-{data[1]}-{data[0]}'  # изменение даты на формат ДДммГГГГ
        desired_data_file = []
        for item in list_text_date_file:
            item_changed = item[:10]
            if data == item_changed: # Сравнение дат
                desired_data_file.append(item)
        return desired_data_file

    def generated_list_date(self):
        sorted_file = self.dir_file()
        self.list_file = self.date_comparison(sorted_file)

    def generated_list(self):
        self.list_file = self.dir_file()

    async def read_file(self, file: str, text: str, i: str) -> str:
        with open(file, mode='r', encoding='utf-8') as file:
            file_text = file.read()
            file_text = file_text.lower()
            text = str(text).lower()  # Переводим в маленький шрифт
            read_file = re.findall(text, file_text)
            if len(read_file) > 0:
                i = str(i).replace('$$$', '   ')
                string = (
                    '╔════════════════════════════════• ✤ •════════════════════════════════╗\n' +
                    '  • Кол-во повторений текста: ' + str(len(read_file)) + '\n  • '
                    + str(''.join(i)) +
                    '\n╚═══════════════════════════════════════════════════════════════════╝')
                self.listWidget.addItem(string)
                await self.process_progress_bar()

    async def text_search_by_file(self, text: str) -> None:
        """Функция поиска текста"""
        self.desired_file = []
        self.progressBar.show()
        self.progressBar.setValue(1)
        st_list = []
        for i in self.list_file:
            file_item = i.split('$$$')[1]  # Разбиваем строку
            st_list.append([file_item, text, i])
        x = [self.read_file(i[0], i[1], i[2]) for i in st_list]
        await asyncio.gather(*x)
        self.progressBar.setValue(100)

    async def process_progress_bar(self):
        self.progressBar.setValue((self.listWidget.count() / len(self.list_file)) * 100)

    def preparation_for_the_search(self):
        """Функция подготовки к поиску"""
        if self.path is None or self.path == '':
            self.progressBar.hide()
            return self.err('Не указано где искать!')

        if len(self.lineEdit.text()) < 3:
            self.progressBar.hide()
            return self.err('Поле поиска должно быть >= 3')

        text = self.lineEdit.text()

        if self.checkBox.isChecked():
            date_search = re.search(r'\d\d-\d\d-\d\d\d\d', self.lineEdit_2.text())
            if date_search is None:
                self.progressBar.hide()
                return self.err('Указана не корректная дата!')
            self.generated_list_date()
            if self.list_file == []:
                self.progressBar.hide()
                return self.err(' Файлов за указанную дату не найдено!')

            asyncio.run(self.text_search_by_file(text))
            # asyncio.run(self.process_progress_bar())
            # asyncio.run(self.text_search_by_file(text))

        else:
            self.generated_list()
            asyncio.run(self.text_search_by_file(text))

    def open_file(self):
        if self.checkBox_2.isChecked():
            s = self.listWidget.selectedIndexes()[0].data()
            b = s.replace('/', '\\')
            b = b.replace('╔════════════════════════════════• ✤ •════════════════════════════════╗\n', '')
            b = b.replace('  • Кол-во повторений текста: ', '').replace(
                '\n╚═══════════════════════════════════════════════════════════════════╝', '')
            b = b.replace('\n  • ', '')
            b = b.split('   ')
            b = (r"start notepad++ " + '"'+b[1]+'"')
            try:
                os.startfile(b)
            except:
                    self.progressBar.hide()
                    text = 'Возможно в имени файла содержаться пробелы или другие символы!'
                    return self.err(text)

        else:

            s = self.listWidget.selectedIndexes()[0].data()
            b = s.replace('/', '\\')
            b = b.replace('╔════════════════════════════════• ✤ •════════════════════════════════╗\n', '')
            b = b.replace('  • Кол-во повторений текста: ', '').replace(
                '\n╚═══════════════════════════════════════════════════════════════════╝', '')
            b = b.replace('\n  • ', '')
            b = b.split('   ')
            try:
                os.startfile('"'+b[1]+'"')
            except:
                self.progressBar.hide()
                text = 'Возможно в имени файла содержаться пробелы или другие символы!'
                return self.err(text)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()