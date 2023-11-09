import sys
import psutil
import cpuinfo
import os
import platform
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtCore import QTimer

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Інформація про систему")

        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        tab_widget = QTabWidget()
        system_tab = QWidget()
        gpu_tab = QWidget()
        cpu_tab = QWidget()
        memory_tab = QWidget()
        disk_tab = QWidget()
        score_tab = QWidget()
        processes_tab = QWidget()

        tab_widget.addTab(system_tab, "Операційна система")
        tab_widget.addTab(gpu_tab, "Відеокарти")
        tab_widget.addTab(cpu_tab, "Процесор")
        tab_widget.addTab(memory_tab, "Оперативна пам'ять")
        tab_widget.addTab(disk_tab, "Вінчестер")
        tab_widget.addTab(score_tab, "Бал")
        tab_widget.addTab(processes_tab, "Процеси")

        layout.addWidget(tab_widget)

        theme_button = QPushButton("Змінити тему")
        theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_button)

        update_button = QPushButton("Оновити")
        update_button.clicked.connect(self.update_info)
        layout.addWidget(update_button)

        self.is_light_theme = True
        self.apply_theme()

        self.info_labels = {}
        self.score_label = QLabel()
        self.score = 0

        self.create_system_tab(system_tab)
        self.create_gpu_tab(gpu_tab)
        self.create_cpu_tab(cpu_tab)
        self.create_memory_tab(memory_tab)
        self.create_disk_tab(disk_tab)
        self.create_processes_tab(processes_tab)
        self.calculate_score()

        score_layout = QVBoxLayout()
        score_layout.addWidget(self.score_label)
        score_tab.setLayout(score_layout)

        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(3)
        self.processes_table.setHorizontalHeaderLabels(["PID", "Ім'я", "Користувач"])
        layout.addWidget(self.processes_table)
        new_width = 100
        new_height = 150
        self.processes_table.setMinimumSize(new_width, new_height)

        self.processes_update_timer = QTimer(self)
        self.processes_update_timer.timeout.connect(self.update_processes_table)
        self.processes_update_timer.start(5000)

    def toggle_theme(self):
        self.is_light_theme = not self.is_light_theme
        self.apply_theme()

    def apply_theme(self):
        if self.is_light_theme:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: white;
                }
                QTabWidget::pane {
                    background-color: white;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: #c0c0c0;
                    color: #000000;
                }
                QTabBar::tab:selected {
                    background-color: #0078d7;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: black;
                }
                QTabWidget::pane {
                    background-color: #c0c0c0;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: #303030;
                    color: white;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    color: black;
                }
                QLabel {
                    background-color: black;
                }
                QLabel {
                    color: white;
                }
                #info_text {
                    background-color: black;
                    color: #ff0000;
                }
            """)

    def create_system_tab(self, tab):
        os_info = platform.uname()
        system_info = {
            "Операційна система": os_info.system,
            "Ім'я вузла": os_info.node,
            "Версія": os_info.release,
            "Версія ядра": os_info.version,
            "Архітектура": os_info.machine,
            "Архітектура процесора": platform.architecture()[0],
        }

        layout = QVBoxLayout()
        tab.setLayout(layout)

        for key, value in system_info.items():
            info_label = QLabel(f"{key}: {value}")
            layout.addWidget(info_label)
            self.info_labels[key] = info_label

    def create_gpu_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        gpu_info = self.get_gpu_info()

        for i, gpu in enumerate(gpu_info):
            gpu_name, gpu_memory, gpu_vendor = gpu
            gpu_label = QLabel(f"Відеокарта {i + 1}")
            layout.addWidget(gpu_label)
            gpu_name_label = QLabel(f"Назва відеокарти: {gpu_name}")
            layout.addWidget(gpu_name_label)
            gpu_memory_label = QLabel(f"Кількість пам'яті відеокарти: {gpu_memory} MB")
            layout.addWidget(gpu_memory_label)
            gpu_vendor_label = QLabel(f"Виробник відеокарти: {gpu_vendor}")
            layout.addWidget(gpu_vendor_label)

    def create_cpu_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        cpu_percent, cpu_freq, physical_cores, logical_cores, cpu_name = self.get_cpu_info()

        cpu_percent_label = QLabel(f"Навантаження процесора: {cpu_percent} %")
        layout.addWidget(cpu_percent_label)
        cpu_name_label = QLabel(f"Назва процесора: {cpu_name}")
        layout.addWidget(cpu_name_label)
        cpu_freq_label = QLabel(f"Частота процесора: {cpu_freq / 1e9} GHz")
        layout.addWidget(cpu_freq_label)
        cpu_physical_cores_label = QLabel(f"Кількість фізичних ядер: {physical_cores}")
        layout.addWidget(cpu_physical_cores_label)
        cpu_logical_cores_label = QLabel(f"Кількість логічних ядер: {logical_cores}")
        layout.addWidget(cpu_logical_cores_label)

    def create_memory_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        memory_total = self.get_memory_info()

        memory_total_label = QLabel(f"Кількість оперативної пам'яті: {memory_total:.2f} GB")
        layout.addWidget(memory_total_label)

    def create_disk_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        disk_info = self.get_disk_info()

        for i, (partition_name, disk_total_gb) in enumerate(disk_info):
            disk_label = QLabel(f"Вінчестер {i + 1}")
            layout.addWidget(disk_label)
            partition_name_label = QLabel(f"Назва вінчестера: {partition_name}")
            layout.addWidget(partition_name_label)
            disk_total_label = QLabel(f"Кількість пам'яті вінчестера: {disk_total_gb:.2f} GB")
            layout.addWidget(disk_total_label)

    def create_processes_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        search_label = QLabel("Пошук/Завершення процесів:")
        search_input = QLineEdit()
        search_button = QPushButton("Знайти та Завершити")
        layout.addWidget(search_label)
        layout.addWidget(search_input)
        layout.addWidget(search_button)

        search_button.clicked.connect(lambda: self.search_and_terminate_process(search_input.text()))



    def search_and_terminate_process(self, query):
        try:
            query = int(query)
        except ValueError:
            query = query.lower()

        for process in psutil.process_iter(attrs=["pid", "name", "username"]):
            try:
                process_info = process.info
                pid = process_info['pid']
                name = process_info['name'].lower()
                username = process_info['username']

                if pid == query or name == query:
                    psutil.Process(pid).terminate()
                    QMessageBox.information(self, "Повідомлення",
                                            f"Процес з PID {pid} та ім'ям '{name}' був завершений.")
                    return

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        QMessageBox.warning(self, "Попередження", f"Процес з PID або іменем '{query}' не знайдений.")

    def get_gpu_info(self):
        gpus = []
        return gpus

    def get_cpu_info(self):
        cpu_percent = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq().current
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count()
        cpu_info = cpuinfo.get_cpu_info()
        cpu_name = cpu_info['brand_raw']
        return cpu_percent, cpu_freq, physical_cores, logical_cores, cpu_name

    def get_memory_info(self):
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024 ** 3)
        return memory_total_gb

    def get_disk_info(self):
        partitions = psutil.disk_partitions()
        disk_info = []

        for partition in partitions:
            partition_name = partition.device
            if os.path.exists(partition_name):
                disk = psutil.disk_usage(partition_name)
                disk_total_gb = disk.total / (1024 ** 3)
                disk_info.append((partition_name, disk_total_gb))
        return disk_info

    def get_processes_info(self):
        process_list = []
        for process in psutil.process_iter(attrs=["pid", "name", "username"]):
            try:
                process_info = process.info
                pid = process_info['pid']
                name = process_info['name']
                username = process_info['username']

                process_list.append((pid, name, username))

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return process_list

    def update_info(self):
        self.update_processes_table()
        self.calculate_score()

    def calculate_score(self):
        cpu_percent, _, _, _, _ = self.get_cpu_info()
        memory_total_gb = self.get_memory_info()

        cpu_weight = 0.6
        memory_weight = 0.4

        max_memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_score = (1 - (cpu_percent / 100)) * cpu_weight
        memory_score = (memory_total_gb / max_memory_gb) * memory_weight

        total_score = (cpu_score + memory_score) * 100
        self.score = total_score
        self.score_label.setText(f"Бал системи: {self.score:.2f}")

    def update_processes_table(self):
        self.processes_table.setRowCount(0)
        process_list = self.get_processes_info()

        for i, (pid, name, username) in enumerate(process_list):
            self.processes_table.insertRow(i)
            self.processes_table.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.processes_table.setItem(i, 1, QTableWidgetItem(name))
            self.processes_table.setItem(i, 2, QTableWidgetItem(username))

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()