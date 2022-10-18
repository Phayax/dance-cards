import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
from PyQt5.QtWidgets import QListWidget, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QAbstractItemView, \
    QListWidgetItem, QFileDialog


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method

        self.current_path = None

        self.setMinimumSize(400, 400)
        self.list_widget = QListWidget()
        self.button_load_folder = QPushButton("Load Folder")
        self.button_load_folder.clicked.connect(self.click_load_folder)

        self.button_select_all = QPushButton("Select All")
        self.button_deselect_all = QPushButton("Deselect All")
        self.button_create = QPushButton("Create Multipage PDF")
        self.button_select_all.clicked.connect(self.list_select_all)
        self.button_deselect_all.clicked.connect(self.list_deselect_all)
        self.button_create.clicked.connect(self.create_multipage)

        h_layout = QHBoxLayout()
        sub_v_layout = QVBoxLayout()
        h_layout.addWidget(self.list_widget)
        h_layout.addLayout(sub_v_layout)
        # sub_v_layout.addWidget(QPushButton("testtext"))
        # sub_v_layout.addWidget(QPushButton("test 2"))
        sub_v_layout.addWidget(self.button_select_all)
        sub_v_layout.addWidget(self.button_deselect_all)
        sub_v_layout.addWidget(self.button_load_folder)
        sub_v_layout.addWidget(self.button_create)

        widget = QWidget()
        widget.setLayout(h_layout)
        self.setCentralWidget(widget)

        # self.list_widget.addItem("test")
        # self.list_widget.addItem("blubb")
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)

        # set font size
        #list_widget.setFont(QFont('Arial', 20))

        # load ui file
        # uic.loadUi('debugtool.ui', self) # Load the .ui file

        self.show()  # Show the GUI

    def click_load_folder(self):
        #dialog = QFileDialog
        #dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        #dialog.show()
        # We can't get the native Windows Dialog to show us files and directories, but only allow selecting files
        # So we have the choice to either only show folders and select them, or use non native Dialog, which gives
        # an unusual dialog for the user.
        # Currently using native Dialog but without showing files
        path_str = QFileDialog.getExistingDirectory(self, "Select Directory", ) #options=QFileDialog.Option.DontUseNativeDialog)
        path = Path(path_str)
        self.current_path = path
        self.load_list_from_folder(path)


    def load_list_from_folder(self, path: Path):
        self.list_widget.clear()
        for file in sorted(path.glob("*.pdf")):
            list_item = QListWidgetItem(file.stem)
            list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            list_item.setCheckState(QtCore.Qt.Checked)
            self.list_widget.addItem(list_item)

    def list_select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(QtCore.Qt.Checked)

    def list_deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(QtCore.Qt.Unchecked)

    def create_multipage(self):
        selection = [self.current_path.parent / f"{self.list_widget.item(i).text()}.pdf" for i in range(self.list_widget.count()) if self.list_widget.item(i).checkState() == QtCore.Qt.Checked]
        for line in selection:
            print(line)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
