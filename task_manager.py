import sys
import psutil
from PyQt5.QtWidgets import QTableWidget, QApplication, QMainWindow, QTableWidgetItem, QMenu, QAbstractItemView, \
    QMessageBox, QSlider, QWidget, QVBoxLayout, QPushButton, QDialog, QLineEdit, QLabel, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import psutil_test


class MyTable(QTableWidget):
    def __init__(self, r, c):
        super().__init__(r, c)
        self.init_ui()

    def init_ui(self):
        self.show()

    def get_current_id(self):
        return self.item(self.currentRow(), 0).text()


def get_formatted_memory(memory_in_bytes):
    if memory_in_bytes > 1024 * 1024 * 1024:
        return "%.2f GB" % (memory_in_bytes / (1024 * 1024 * 1024))
    elif memory_in_bytes > 1024 * 1024:
        return "%.2f MB" % (memory_in_bytes / (1024 * 1024))
    elif memory_in_bytes > 1024:
        return "%.2f KB" % (memory_in_bytes / 1024)
    else:
        return str(memory_in_bytes) + 'B'


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        rows = psutil_test.rows
        self.form_widget = MyTable(rows, 10)
        self.setCentralWidget(self.form_widget)
        col_headers = ['P-ID', 'P-Name', 'User', 'Virt-Mem', 'Res-Mem', 'Shd-Mem', 'Mem %', 'CPU %', 'Path', 'Priority']
        self.key = 'pid'
        self.flag = False
        self.form_widget.setHorizontalHeaderLabels(col_headers)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.change_values)
        self.form_widget.horizontalHeader().sectionClicked.connect(self.set_values)
        self.form_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.b1 = QPushButton()
        self.l1 = QLabel()
        self.s1 = QSlider(Qt.Horizontal)

    @QtCore.pyqtSlot()
    def change_values(self):

        new_list = psutil_test.getListOfProcesses()
        final_list = self.sort_list(new_list, self.key, self.flag)  # set value function to be called by button trigger
        self.form_widget.setRowCount(len(final_list))
        # print(new_list)

        for i, process in enumerate(final_list):
            self.form_widget.setItem(i, 0, QTableWidgetItem(str(process['pid'])))
            self.form_widget.setItem(i, 1, QTableWidgetItem(str(process['name'])))
            self.form_widget.setItem(i, 2, QTableWidgetItem(str(process['username'])))
            self.form_widget.setItem(i, 3, QTableWidgetItem(get_formatted_memory(process['vms'])))
            self.form_widget.setItem(i, 4, QTableWidgetItem(get_formatted_memory(process['res'])))
            self.form_widget.setItem(i, 5, QTableWidgetItem(get_formatted_memory(process['shared'])))
            self.form_widget.setItem(i, 6, QTableWidgetItem("%.2f " % (process['mem_per'])))
            self.form_widget.setItem(i, 7, QTableWidgetItem(str(process['cpu'])))
            self.form_widget.setItem(i, 8, QTableWidgetItem(str(process['path'])))
            self.form_widget.setItem(i, 9, QTableWidgetItem(str(process['priority'])))

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        kill_act = context_menu.addAction("Kill")
        change_priority = context_menu.addMenu("Change priority")
        quit_act = context_menu.addAction("Exit")

        highest_priority = change_priority.addAction("HIGHEST")
        high_priority = change_priority.addAction("HIGH")
        medium_priority = change_priority.addAction("MEDIUM")
        low_priority = change_priority.addAction("LOW")
        lowest_priority = change_priority.addAction("LOWEST")
        custom_priority = change_priority.addAction("CUSTOM")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_act:
            self.close()

        if action == kill_act:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            self.confirm_kill_process(process)

        if action == highest_priority:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            process.nice(-20)

        if action == high_priority:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            process.nice(-10)

        if action == medium_priority:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            process.nice(0)

        if action == low_priority:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            process.nice(10)

        if action == lowest_priority:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            process.nice(-20)

        if action == custom_priority:
            id = self.form_widget.get_current_id()
            process = psutil.Process(pid=int(id))
            self.set_custom_priority(process)

    def sort_list(self, sort_list, key, flag):
        return sorted(sort_list, key=lambda obj: obj[key], reverse=flag)

    def set_values(self, col):
        # print(col)
        if col == 0:
            self.flag = not self.flag
            self.key = 'pid'

        if col == 1:
            self.flag = not self.flag
            self.key = 'name'

        if col == 2:
            self.flag = not self.flag
            self.key = 'username'

        if col == 3:
            self.flag = not self.flag
            self.key = 'vms'

        if col == 4:
            self.flag = not self.flag
            self.key = 'res'

        if col == 5:
            self.flag = not self.flag
            self.key = 'shared'

        if col == 6:
            self.flag = not self.flag
            self.key = 'mem_per'

        if col == 7:
            self.flag = not self.flag
            self.key = 'cpu'

        if col == 8:
            self.flag = not self.flag
            self.key = 'path'

    def confirm_kill_process(self, process):
        message = QMessageBox.question(self, "Kill Process", "Are you sure you want to kill this process ?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if message == QMessageBox.Yes:
            process.kill()
        else:
            pass

    def set_custom_priority(self, process):
        d = QDialog()
        self.b1 = QPushButton("Set Priority", d)
        self.l1 = QLabel()
        self.l1.setText(str(process.nice()))
        self.s1 = QSlider(Qt.Horizontal)
        d.setWindowTitle("Change Priority")
        d.setGeometry(100, 100, 300, 100)
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        self.s1.setMinimum(-20)
        self.s1.setMaximum(19)
        self.s1.setValue(process.nice())
        self.s1.setTickInterval(1)
        self.s1.setTickPosition(QSlider.TicksBelow)
        self.s1.valueChanged.connect(self.slider_change)
        self.b1.clicked.connect(self.set_priority(process))
        hbox.addWidget(self.s1)
        hbox.addWidget(self.l1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.b1)
        d.setLayout(vbox)
        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()

    def slider_change(self):
        value = self.s1.value()
        self.l1.setText(str(value))

    def set_priority(self, process):
        def process_priority():
            value = self.s1.value()
            process.nice(value)
        return process_priority


app = QApplication(sys.argv)

task_mgr = TaskManager()

task_mgr.show()
task_mgr.timer.start(1000)

sys.exit(app.exec_())

