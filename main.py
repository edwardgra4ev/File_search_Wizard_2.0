 # sys нужен для передачи argv в QApplication
from PySide2 import QtWidgets,  QtCore
from PySide2.QtWidgets import QFileDialog, QDialog
from PySide2.QtGui import QPixmap, QFont, QIcon
import gui  # Это наш конвертированный файл дизайна
import os, datetime, re, sys
from PySide2.QtCore import Qt
import img


class ExampleApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.progressBar.setProperty("value", 0)
        self.progressBar.hide()
        self.pushButton.clicked.connect(self.director)
        self.pushButton_2.clicked.connect(self.seartch)
        self.listWidget.itemDoubleClicked.connect(self.open_file)



    def keyPressEvent (self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.seartch()

        elif event.key() in [QtCore.Qt.Key_F1] : # строка поиска
             self.lineEdit.setFocus()

        elif event.key() in [QtCore.Qt.Key_F3] : # строка даты
             self.lineEdit_2.setFocus()

        elif event.key() in [QtCore.Qt.Key_F2] : # строка поиска
             if self.checkBox.isChecked() == False:
                 self.checkBox.setChecked(True)
             elif self.checkBox.isChecked() == True:
                 self.checkBox.setChecked(False)

        elif event.key() in [QtCore.Qt.Key_F4]:
             self.director()


        elif event.key() in [QtCore.Qt.Key_F5]:
            self.cop()

    def director(self):
        global directory
        directory = QFileDialog.getExistingDirectory(options=QFileDialog.DontUseNativeDialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.hide()
        self.listWidget.clear()

    def err(self,text):
        d = QDialog()
        d.resize(384, 205)
        d.setWindowTitle('Ошибка')
        icon = QIcon()
        icon.addPixmap(QPixmap(":/newPrefix/720.png"), QIcon.Normal, QIcon.Off)
        d.setWindowIcon(icon)
        self.label = QtWidgets.QLabel(d)
        self.label.setGeometry(QtCore.QRect(0, -10, 391, 221))
        self.label.setText("")
        self.label.setPixmap(QPixmap(":/newPrefix/gandalf.png"))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(d)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 3910, 20 ))
        self.label_2.setText(text)
        font = QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()
        return

    def seartch(self):
        if 'directory' not in globals():
            self.progressBar.hide()
            text = 'Не указано где искать!'
            return self.err(text)

        if self.lineEdit.text() == '':
            self.progressBar.hide()
            text = 'Не указано что искать!'
            return self.err(text)

        if len(self.lineEdit_2.text()) < 8 or '-' not in self.lineEdit_2.text():
            self.progressBar.hide()
            text = 'Указана не корректная дата!'
            return self.err(text)
        self.progressBar.show()
        self.progressBar.setValue(0)
        text = self.lineEdit.text()
        path = (str(directory) + '/')
        search_date = self.lineEdit_2.text()
        if self.checkBox.isChecked():
            list_file = Log(path, search_date).generated_list_date()
            if list_file == []:
                self.progressBar.hide()
                return self.err('  Файлов за указанную дату не найдено!')
            run = Log(path, search_date).text_seartch_by_file
            start = run(text, list_file)
            if start == []:
                self.progressBar.hide()
                return self.err('  Файлов c нужным текстом не найдено!')
            for i in start:
                self.listWidget.addItem(i)
            self.progressBar.setValue(100)
        else:
            list_file = Log(path, search_date).generated_list()
            run = Log(path, search_date).text_seartch_by_file
            start = run(text, list_file)
            if start == []:
                self.progressBar.hide()
                return self.err('  Файлов c нужным текстом не найдено!')
            for i in start:
                self.listWidget.addItem(i)
            self.progressBar.setValue(100)


    def cop(self):
        s = self.listWidget.selectedIndexes()[0].data()
        s = str(s).split(' | ')
        b = str(s[1])
        b = b.replace('/', '\\')
        b = b.replace('╔═══════════════════════════• ✤ •═══════════════════════════╗\n', '')
        b = b.replace('  • Кол-во повторений текста: ', '').replace('\n╚═════════════════════════════════════════════════════════╝', '')
        b = b.replace('\n  • ', '')
        b = ("explorer.exe /select," + '"' + b + '"')
        os.system(b)

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
            g = os.system(b)
            if g != 0 and g != 1:
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
            g = os.system('"'+b[1]+'"')
            if g != 0 and g != 1:
                self.progressBar.hide()
                text = 'Возможно в имени файла содержаться пробелы или другие символы!'
                return self.err(text)
class Log(object):
    def __init__(self,path, search_date):

        self.path = path
        self.search_date = search_date


    def getting_file_path(self):
        """Получаем все файлы в нужной дерриктории"""
        file_list = os.listdir(self.path)  # получение списка файлов
        file_list = [os.path.join(self.path, i) for i in file_list]
        file_list = sorted(file_list, key=os.path.getmtime)  # Сортировка списка
        file_list.reverse()  # Переворачивание списка
        return file_list

    def dir_file(sel,file_list):
        """Заполнение списка нужными файлами"""
        list_text_date_file = []  # Список снужных фалов с дотой модификации
        for i in file_list:
            if ".txt" in str(i).lower() or ".log" in str(i).lower() or ".xml" in str(i).lower() \
                    or ".doc" in str(i).lower() or ".docx" in str(i).lower():
                file_create_date = datetime.datetime.fromtimestamp(os.path.getmtime(i))  #Получение даты модификации файла
                list_text_date_file.append(str(file_create_date) + '$$$' + i)
        return list_text_date_file


    def date_comparison(self,list_text_date_file):
        """Функция сравнения даты модификации файла и даты указанной пользователем"""
        if self.search_date == '':
            return list_text_date_file
        data = str(self.search_date).split('-')  # Разбиение даты
        data = data[2] + '-' + data[1] + '-' + data[0]  # изменение даты на формат ДДммГГГГ
        desired_data_file = []
        for item in list_text_date_file:
            item_changed  = item[:10]
            if data == item_changed: # Сравнение дат
                desired_data_file.append(item)
        return desired_data_file

    def generated_list_date(self):
        file_path = self.getting_file_path()
        sorted_file = self.dir_file(file_path)
        sorted_date = self.date_comparison(sorted_file)
        return sorted_date

    def generated_list(self):
        file_path = self.getting_file_path()
        sorted_file = self.dir_file(file_path)
        return sorted_file

    def text_seartch_by_file(self,text,list_file):
        """Функция поиска текста"""
        desired_file = []
        for i in list_file:
            file_item = i.split('$$$')[1]  # Разбиваем строку
            with open(file_item, "r", encoding='utf-8') as file:
                file_text = file.read().lower()  #
                text = str(text).lower()  # Переводим в маленький шрифт
                read_file = re.findall(text, file_text)
                if len(read_file) > 0:
                    i = str(i).replace('$$$', '   ')
                    desired_file.append(
                        '╔════════════════════════════════• ✤ •════════════════════════════════╗\n' +
                        '  • Кол-во повторений текста: ' + str(len(read_file)) + '\n  • '
                        + str(''.join(i)) +
                        '\n╚═══════════════════════════════════════════════════════════════════╝')
                    file.close()

        return desired_file


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()


