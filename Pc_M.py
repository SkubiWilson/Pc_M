import sys
import psutil
import cpuinfo
import GPUtil
import os
import platform
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QTableWidgetItem, QDialog, QTableWidget
from datetime import datetime
from PyQt5.QtGui import QIcon
import speedtest
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
class SplashScreen(QMainWindow):
    def __init__(self, pixmap, main_window):
        super().__init__()
        self.main_window = main_window
        # Вікно з картинкою
        self.splash_widget = QWidget()
        self.splash_layout = QVBoxLayout()
        self.splash_label = QLabel(self.splash_widget)
        self.splash_label.setAlignment(Qt.AlignCenter)
        self.splash_label.setPixmap(pixmap)
        self.splash_layout.addWidget(self.splash_label)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: transparent;")
        self.setCentralWidget(self.splash_widget)
        self.resize(590, 400)

        # Таймер для закриття вікна через 2 секунди (2000 мілісекунд)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_splash_and_show_main)
        self.timer.start(2000)

    def close_splash_and_show_main(self):
        self.close()
        self.main_window.show()



class MyWindow(QMainWindow):
    class TaskManager(QDialog):
        def __init__(self, layout):
            super().__init__()

            self.task_table = QTableWidget()
            self.task_table.setColumnCount(3)
            self.task_table.setHorizontalHeaderLabels(["Ім'я процесу", "PID", "Дії"])

            refresh_button = QPushButton("Оновити")
            refresh_button.clicked.connect(self.update_task_list)
            layout = QVBoxLayout(self)
            layout.addWidget(refresh_button)
            layout.addWidget(self.task_table)
            self.resize(590, 400)
            self.setLayout(layout)

        def update_task_list(self):
            self.task_table.setRowCount(0)
            for process in psutil.process_iter(['pid', 'name']):
                row_position = self.task_table.rowCount()
                self.task_table.insertRow(row_position)
                process_name = QTableWidgetItem(process.info.get('name', 'Unknown'))
                process_pid = QTableWidgetItem(str(process.info.get('pid', -1)))

                kill_button = QPushButton('Завершити')
                kill_button.clicked.connect(lambda _, pid=process.info.get('pid', -1): self.kill_process(pid))

                self.task_table.setItem(row_position, 0, process_name)
                self.task_table.setItem(row_position, 1, process_pid)
                self.task_table.setCellWidget(row_position, 2, kill_button)

        def kill_process(self, pid):
            try:
                process = psutil.Process(pid)
                process.terminate()
            except Exception as e:
                print(f"Error terminating process {pid}: {e}")

    def __init__(self):
        super().__init__()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        tab_widget = QTabWidget()
        task_tab = QWidget()
        tab_widget.addTab(task_tab, "Менеджер завдань")

        layout.addWidget(tab_widget)

        self.task_manager = self.TaskManager(layout)
        self.task_manager.update_task_list()

        self.setWindowTitle("Інформація про систему")
        self.setGeometry(100, 100, 600, 650)

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
        datetime_tab = QWidget()
        battery_tab = QWidget()
        network_tab = QWidget()
        task_tab = QWidget()

        tab_widget.addTab(system_tab, "Операційна система")
        tab_widget.addTab(gpu_tab, "Відеокарти")
        tab_widget.addTab(cpu_tab, "Процесор")
        tab_widget.addTab(memory_tab, "Оперативна пам'ять")
        tab_widget.addTab(disk_tab, "Вінчестер")
        tab_widget.addTab(score_tab, "Тест")
        tab_widget.addTab(datetime_tab, "Дата і час")
        tab_widget.addTab(battery_tab, "Батарея")
        tab_widget.addTab(network_tab, "Мережа")
        tab_widget.addTab(task_tab, "Менеджер завдань")

        layout.addWidget(tab_widget)

        config_button = QPushButton(self)
        config_button.clicked.connect(self.save_configuration)
        layout.addWidget(config_button)
        icon_config = QIcon("ico/save.png")
        config_button.setIcon(icon_config)
        config_button.setFixedSize(30, 30)

        theme_button = QPushButton(self)
        theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_button)
        theme_button.setFixedSize(30, 30)
        icon_theme = QIcon("ico/theme.png")
        theme_button.setIcon(icon_theme)

        update_button = QPushButton(self)
        icon_update = QIcon("ico/update.png")
        update_button.setIcon(icon_update)
        update_button.clicked.connect(self.update_all_info)
        layout.addWidget(update_button)
        update_button.setFixedSize(30, 30)

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
        self.create_datetime_tab(datetime_tab)
        self.create_battery_tab(battery_tab)
        self.create_network_tab(network_tab)
        self.create_task_tab(task_tab)  # Виклик методу для створення вкладки "Менеджер завдань"
        self.calculate_score()

        score_layout = QVBoxLayout()
        score_layout.addWidget(self.score_label)
        score_tab.setLayout(score_layout)

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
    def save_configuration(self):
        config_filename = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(config_filename, 'w') as  config_filename:
            config_filename.write("Зберігаємо інфо про конфігурацію\n")
            config_filename.write(f"Тема: {'Світла' if self.is_light_theme else 'Темна'}\n")
            config_filename.write(f"Кількість ОЗП: {self.get_memory_info():.2f} GB\n")
            config_filename.write(f"Інформація про процессор: {self.get_cpu_info()}\n")
            config_filename.write(f"Логічні диски: {self.get_disk_info()}")





    def create_network_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)
        net_label = QLabel(f"Швидкість завантаження: {self.user_net(self.get_network_info())}")
        layout.addWidget(net_label)

    def create_task_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        open_task_manager_button = QPushButton("Менеджер процесів")
        open_task_manager_button.clicked.connect(self.open_task_manager)
        layout.addWidget(open_task_manager_button)

    def open_task_manager(self):
        self.task_manager.update_task_list()
        self.task_manager.exec_()


    def create_system_tab(self, tab):
        os_info = platform.uname()
        system_info = {
            "Операційна система": os_info.system,
            "Ім'я користувача": os_info.node,
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

    def create_datetime_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)
        datetime_label = QLabel(f"Поточна дата і час: {datetime.now()}")
        layout.addWidget(datetime_label)

    def create_battery_tab(self, tab):
        layout = QVBoxLayout()
        tab.setLayout(layout)

        battery_info = self.get_battery_info()

        for key, value in battery_info.items():
            battery_label = QLabel(f"{key}: {value}")
            layout.addWidget(battery_label)

    def get_network_info(self):
        try:
            ntw = speedtest.Speedtest()
            tsdw = ntw.download()
            return tsdw if tsdw is not None else 0
        except Exception as e:
            print(f"Помилка при отриманні швидкості завантаження: {e}")
            return 0

    def user_net(self, testmb):
        suffixes = ["B", "Kb", "Mb", "Gb"]
        i = 0
        while testmb >= 1024 and i < len(suffixes) - 1:
            testmb /= 1024
            i += 1
        f = ('%.2f' % testmb).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])
    def get_gpu_info(self):
        gpus = GPUtil.getGPUs()
        gpu_info = []
        max_gpus = 2

        if not gpus:
            gpu_info.append(("Нажаль ваша відеокарта не підтримується програмою(", 0, "N/A"))

        for i, gpu in enumerate(gpus):
            if i >= max_gpus:
                break
            gpu_name = gpu.name
            gpu_memory = gpu.memoryTotal
            gpu_vendor = self.detect_video_card_vendor(gpu_name)
            gpu_info.append((gpu_name, gpu_memory, gpu_vendor))
        return gpu_info

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

    def get_battery_info(self):
        battery = psutil.sensors_battery()
        if battery is not None:
            is_plugged = battery.power_plugged
            percent = battery.percent
            power_status = "Підключено до мережі" if is_plugged else "Не підключено до мережі"
            wear_level = battery.percent - battery.secsleft / (battery.secsleft + battery.secsleftfull) * 100

            return {"Статус батареї": power_status, "Рівень заряду": f"{percent}%",
                    "Рівень зносу батареї": f"{wear_level:.2f}%"}
        else:
            return {"Статус батареї": "Невідомий", "Рівень заряду": "Невідомий", "Рівень зносу батареї": "Невідомий"}

    def format_seconds(self, seconds):
        if seconds is None:
            return "Невідомий"
        hours, remainder = divmod(seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)} годин {int(minutes)} хвилин"


    def update_all_info(self):
        self.update_system_info()
        self.update_gpu_info()
        self.update_cpu_info()
        self.update_memory_info()
        self.update_disk_info()
        self.update_datetime_info()
        self.update_battery_info()
        self.update_network_info()
        self.calculate_score()

    def update_datetime_info(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.info_labels["Дата і час"].setText(f"Поточна дата і час: {current_datetime}")

    def update_battery_info(self):
        battery_info = self.get_battery_info()
        for key, value in battery_info.items():
            self.info_labels[key].setText(f"{key}: {value}")




def main():
    app = QApplication(sys.argv)
    pixmap = QPixmap("images/Load.png")

    # Спочатку створюємо об'єкт MyWindow
    window = MyWindow()

    # Потім Splash Screen, передаючи йому вікно MyWindow
    splash = SplashScreen(pixmap, window)

    # Показуємо обидва вікна
    splash.show()
    window.hide()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()