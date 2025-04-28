import itertools
import sys
from pathlib import Path
from datetime import datetime

import PyPDF2
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
from PyQt5.QtWidgets import QListWidget, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QAbstractItemView, \
    QListWidgetItem, QFileDialog, QFrame, QCheckBox, QLabel, QRadioButton, QGroupBox, QMessageBox, QLineEdit, \
    QToolButton

from multi import get_page_indices, NupTexDocument


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class QHLine(QFrame):
    """
    Code from: https://stackoverflow.com/a/41068447
    """
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    """
        Code from: https://stackoverflow.com/a/41068447
    """
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method

        self.current_single_path = None
        self.current_full_path = None

        self.setMinimumSize(400, 600)


        self.group_pdf_select = QGroupBox()
        self.group_pdf_select.setTitle("Pfad zum PDF")
        self.lineEdit_full_pdf = QLineEdit()
        self.lineEdit_full_pdf.setPlaceholderText("Bitte PDF auswählen")
        self.lineEdit_single_pdfs = QLineEdit()
        self.lineEdit_single_pdfs.setPlaceholderText("Bitte Ordner auswählen")
        self.toolButton_full = QToolButton()
        self.toolButton_full.setText("...")
        self.toolButton_full.clicked.connect(self.click_load_full)
        self.toolButton_single = QToolButton()
        self.toolButton_single.setText("...")
        self.toolButton_single.clicked.connect(self.click_load_folder)
        group_full_vbox = QVBoxLayout()
        group_full_vbox.addWidget(QLabel("Gesamtes PDF:"))
        full_pdf_hbox = QHBoxLayout()
        group_full_vbox.addLayout(full_pdf_hbox)
        full_pdf_hbox.addWidget(self.lineEdit_full_pdf)
        full_pdf_hbox.addWidget(self.toolButton_full)
        group_full_vbox.addSpacing(10)
        group_full_vbox.addWidget(QLabel("Ordner mit einzelnen PDFs:"))
        single_pdfs_hbox = QHBoxLayout()
        single_pdfs_hbox.addWidget(self.lineEdit_single_pdfs)
        single_pdfs_hbox.addWidget(self.toolButton_single)
        group_full_vbox.addLayout(single_pdfs_hbox)




        self.group_pdf_select.setLayout(group_full_vbox)

        self.group_list = QGroupBox()
        self.group_list.setTitle("Verfügbare Tänze")
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.list_widget_item_clicked)
        vbox = QVBoxLayout()
        vbox.addWidget(self.list_widget)
        self.group_list.setLayout(vbox)

        self.button_load_full_pdf = QPushButton("Load Full PDF")
        self.button_load_full_pdf.clicked.connect(self.click_load_full)
        self.button_load_folder = QPushButton("Load Folder")
        self.button_load_folder.clicked.connect(self.click_load_folder)

        self.button_select_all = QPushButton("Alle Auswählen")
        self.button_deselect_all = QPushButton("Keine Auswählen")
        self.button_create = QPushButton("Create Multipage PDF")
        self.button_select_all.clicked.connect(self.list_select_all)
        self.button_deselect_all.clicked.connect(self.list_deselect_all)
        self.button_create.clicked.connect(self.create_multipage)
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        left_v_layout = QVBoxLayout()
        sub_v_layout = QVBoxLayout()
        h_layout.addLayout(left_v_layout)
        h_layout.addLayout(sub_v_layout)
        v_layout.addWidget(self.group_pdf_select)
        v_layout.addLayout(h_layout)

        #left_v_layout.addWidget(self.group_pdf_select)
        left_v_layout.addWidget(self.group_list)

        # h_layout.addWidget(QVLine())
        # sub_v_layout.addWidget(QPushButton("testtext"))
        # sub_v_layout.addWidget(QPushButton("test 2"))
        sub_v_layout.addWidget(self.button_select_all)
        sub_v_layout.addWidget(self.button_deselect_all)
        # sub_v_layout.addWidget(self.button_load_full_pdf)
        # sub_v_layout.addWidget(self.button_load_folder)
        sub_v_layout.addStretch(1)
        sub_v_layout.addWidget(QHLine())
        sub_v_layout.addStretch(1)
        #size_label = QLabel("Größe")
        #size_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        #size_label.setAlignment(QtCore.Qt.AlignCenter)
        #sub_v_layout.addWidget(size_label)
        self.size_group_box = QGroupBox()
        self.size_group_box.setTitle("Größe")
        vbox = QVBoxLayout()
        self.nup_2_radio = QRadioButton("2x2 (A6)")
        self.nup_2_radio.setChecked(True)
        self.nup_3_radio = QRadioButton("3x3 (A7)")
        self.nup_4_radio = QRadioButton("4x4 (A8)")

        vbox.addWidget(self.nup_2_radio)
        vbox.addWidget(self.nup_3_radio)
        vbox.addWidget(self.nup_4_radio)
        self.size_group_box.setLayout(vbox)
        sub_v_layout.addWidget(self.size_group_box)

        self.fold_group_box = QGroupBox()
        self.fold_group_box.setTitle("Falz")
        vbox = QVBoxLayout()

        self.fold_short_radio = QRadioButton("Kurze Seite")
        self.fold_short_radio.setChecked(True)
        self.fold_long_radio = QRadioButton("Lange Seite")

        vbox.addWidget(self.fold_short_radio)
        vbox.addWidget(self.fold_long_radio)
        self.fold_group_box.setLayout(vbox)
        sub_v_layout.addWidget(self.fold_group_box)

        sub_v_layout.addStretch(1)
        sub_v_layout.addWidget(self.button_create)
        sub_v_layout.addStretch(1)

        widget = QWidget()
        widget.setLayout(v_layout)
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
        self.set_initial_pdfs_if_available()
        self.set_buttons_if_pdfs_fit()

    def set_initial_pdfs_if_available(self):
        split_path = Path("./split/")
        if split_path.exists() and split_path.is_dir():
            if list(split_path.glob("*.pdf")):
                self.current_single_path = split_path
                self.load_list_from_folder(split_path)
                self.lineEdit_single_pdfs.setText(str(self.current_single_path.resolve()))
        full_pdf_path = Path("./cards.pdf")
        if full_pdf_path.exists():
            self.current_full_path = full_pdf_path
            self.lineEdit_full_pdf.setText(str(self.current_full_path.resolve()))

        self.set_buttons_if_pdfs_fit()

    def list_widget_item_clicked(self, item: QListWidgetItem):
        print(f"Item: {item.text()} clicked.")
        # if item.checkState() == QtCore.Qt.CheckState.Checked:
        #     item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        # elif item.checkState() == QtCore.Qt.CheckState.Unchecked:
        #     item.setCheckState(QtCore.Qt.CheckState.Checked)

    def fitting_pdfs_loaded(self) -> bool:
        if not self.current_single_path:
            return False
        if not self.current_full_path:
            return False
        if not self.current_full_path.is_file():
            return False
        if not self.current_single_path.is_dir():
            return False
        if len(list(self.current_single_path.glob("*.pdf"))) == 0:
            return False
        reader_full_pdf = PyPDF2.PdfReader(str(self.current_full_path))
        full_length = len(reader_full_pdf.pages)
        single_summed_lengths = 0
        for file in self.current_single_path.glob("*.pdf"):
            reader_single_pdf = PyPDF2.PdfReader(str(file))
            single_summed_lengths += len(reader_single_pdf.pages)
        if full_length - 1 == single_summed_lengths:
            return True
        else:
            QMessageBox.warning(self, "PDFs passen nicht zueinander", f"Das ausgewählte PDF und der Ordner mit den einzelnen PDFs passen leider nicht zueinander. Es wird erwartet, dass alle einzelnen PDFs genau eine Seite weniger sind als das gesamte PDF(aufgrund einer nötigen Leerseite).\nIn diesem Fall waren es aber {full_length} Seiten im gesamten PDF und {single_summed_lengths} in der Summe der einzelnen PDFs!.\nDie beste Lösung ist sowohl das gesamte PDF, als auch die einzelnen PDFs nocheinmal zu erstellen/herunterzuladen.")
            return False

    def set_buttons_if_pdfs_fit(self):
        if self.fitting_pdfs_loaded():
            self.button_select_all.setEnabled(True)
            self.button_deselect_all.setEnabled(True)
            self.button_create.setEnabled(True)
        else:
            self.button_select_all.setEnabled(False)
            self.button_deselect_all.setEnabled(False)
            self.button_create.setEnabled(False)

    def click_load_full(self):
        path_str = QFileDialog.getOpenFileName(self, "Select Full File PDF", filter="*.pdf")
        self.current_full_path = Path(path_str[0])
        self.lineEdit_full_pdf.setText(str(self.current_full_path.resolve()))
        self.set_buttons_if_pdfs_fit()



    def click_load_folder(self):
        # We can't get the native Windows Dialog to show us files and directories, but only allow selecting files
        # So we have the choice to either only show folders and select them, or use non native Dialog, which gives
        # an unusual dialog for the user.
        # Currently using native Dialog but without showing files
        path_str = QFileDialog.getExistingDirectory(self, "Select Directory", ) #options=QFileDialog.Option.DontUseNativeDialog)
        path = Path(path_str)
        self.current_single_path = path
        self.lineEdit_single_pdfs.setText(str(self.current_single_path.resolve()))
        self.load_list_from_folder(path)
        self.set_buttons_if_pdfs_fit()


    def load_list_from_folder(self, path: Path):
        self.list_widget.clear()
        for file in sorted(path.glob("*.pdf")):
            list_item = QListWidgetItem()
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, QCheckBox(file.stem))
            self.list_widget.itemWidget(list_item).setCheckState(QtCore.Qt.CheckState.Checked)

            # list_item = QListWidgetItem(file.stem)
            # list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            # list_item.setCheckState(QtCore.Qt.Checked)
            # self.list_widget.addItem(list_item)

    def list_select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.itemWidget(self.list_widget.item(i)).setCheckState(QtCore.Qt.CheckState.Checked)

    def list_deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.itemWidget(self.list_widget.item(i)).setCheckState(QtCore.Qt.CheckState.Unchecked)

    def create_multipage(self):
        selection = [self.current_single_path / f"{self.list_widget.itemWidget(self.list_widget.item(i)).text()}.pdf" for i in range(self.list_widget.count()) if self.list_widget.itemWidget(self.list_widget.item(i)).checkState() == QtCore.Qt.CheckState.Checked]
        if not selection:
            return
        # for line in selection:
        #     print(line)
        if self.nup_2_radio.isChecked():
            nup_factor = 2
        elif self.nup_3_radio.isChecked():
            nup_factor = 3
        elif self.nup_4_radio.isChecked():
            nup_factor = 4
        else:
            raise ValueError("at least one size must be selected!")

        if self.fold_short_radio.isChecked():
            fold_edge = "short"
        elif self.fold_long_radio.isChecked():
            fold_edge = "long"
        else:
            raise ValueError("at least on fold radio buttons must be selected!")

        dance_dict = get_page_indices(single_pdf_path=self.current_single_path, full_pdf_path=self.current_full_path)
        ntc = NupTexDocument(dance_dict=dance_dict, nup_pdf_source=self.current_full_path)
        date_string = datetime.now().strftime("%y-%m-%d_%H-%M")
        ntc.layout_dances(output_file=Path(f"{date_string}_multi_cards_{nup_factor}x{nup_factor}_fold_{fold_edge}_.tex"), dance_list=selection, fold_edge=fold_edge,
                          nup_factor=nup_factor)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
