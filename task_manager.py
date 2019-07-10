import sys

import psutil
from PyQt5.QtWidgets import QTableWidget, QApplication, QMainWindow, QTableWidgetItem, QMenu
from PyQt5 import QtCore
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
    if memory_in_bytes > 1024*1024*1024:
        return "%.2f GB" % (memory_in_bytes / (1024*1024*1024))
    elif memory_in_bytes > 1024*1024:
        return "%.2f MB" % (memory_in_bytes / (1024*1024))
    elif memory_in_bytes > 1024:
        return "%.2f KB" % (memory_in_bytes / 1024)
    else:
        return str(memory_in_bytes) + 'B'


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        rows = psutil_test.rows
        self.form_widget = MyTable(rows, 9)
        self.setCentralWidget(self.form_widget)
        col_headers = ['Process ID', 'Process Name', 'User', 'Virtual Memory', 'Reserved Memory', 'Shared Memory', 'Memory %', 'CPU Usage %', 'Path']
        self.key = 'pid'
        self.flag = False
        self.form_widget.setHorizontalHeaderLabels(col_headers)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.change_values)
        self.form_widget.horizontalHeader().sectionClicked.connect(self.set_values)

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

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        kill_act = context_menu.addAction("Kill")
        quit_act = context_menu.addAction("Quit")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_act:
            self.close()
        if action == kill_act:
            id = self.form_widget.get_current_id()
            print(id)
            process = psutil.Process(pid=int(id))
            print(process.cpu_percent())
            process.kill()

    def sort_list(self, sort_list, key, flag):
        return sorted(sort_list, key=lambda obj: obj[key], reverse=flag)

    def set_values(self, col):
        print(col)
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


app = QApplication(sys.argv)

task_mgr = TaskManager()

task_mgr.show()
task_mgr.timer.start(1000)

sys.exit(app.exec_())
