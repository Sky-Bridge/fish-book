import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from pynput import keyboard

class TransparentWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 创建系统托盘图标
        self.tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("83970613_p0_master1200.jpg"), self)
        self.tray_icon.show()

        # 创建退出菜单选项
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.triggered.connect(self.exit)

        # 创建系统托盘菜单
        self.tray_menu = QtWidgets.QMenu(self)
        self.tray_menu.addAction(exit_action)

        # 设置系统托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)

        try:
            with open('page', 'rb') as f:
                page = f.read()
                self.current_line = int.from_bytes(page, 'big')
        except:
            self.current_line = 0
        self.text_lines = self.read_text_file("book.txt")

        self.label = QtWidgets.QLabel(self)
        self.label.setStyleSheet("color: black;")
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.display_text(self.text_lines[self.current_line])

        self.resize(800, 100)
        self.center_window()

        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.timeout.connect(self.check_idle_time)

        self.idle_duration = 10000
        self.idle_counter = 0
        self.idle_threshold = self.idle_duration // 1000

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        self.start_idle_timer()

    def read_text_file(self, filename):
        with open(filename, "r", encoding="UTF-8") as file:
            content = file.read().replace('\n', '')
            lines = self.split_text(content, 30)  # 修改为每行最多30个字符
        return lines

    def split_text(self, text, max_chars):
        lines = []
        current_line = ""
        for char in text:
            current_line += char
            if len(current_line) == max_chars:
                lines.append(current_line)
                current_line = ""
        if current_line:
            lines.append(current_line)
        return lines

    def display_text(self, content):
        self.label.setText(content)

    def display_time(self):
        current_time = QtCore.QTime.currentTime().toString("hh:mm:ss")
        self.label.setText(current_time)

    def on_key_press(self, key):
        if key == keyboard.Key.alt_l:
            self.alt_pressed = True
        elif key == keyboard.KeyCode.from_char('x') and self.alt_pressed:
            if self.isHidden():
                self.show()
            else:
                self.hide()
        elif not self.isHidden():
            if key == keyboard.KeyCode.from_char('a'):
                self.previous_page()
            elif key == keyboard.KeyCode.from_char('d'):
                self.next_page()

    def on_key_release(self, key):
        if key == keyboard.Key.alt_l:
            self.alt_pressed = False

    def start_idle_timer(self):
        self.idle_timer.start(1000)

    def reset_idle_timer(self):
        self.idle_counter = 0

    def check_idle_time(self):
        self.idle_counter += 1
        if self.idle_counter >= self.idle_threshold and not self.isHidden():
            self.display_time()

    def center_window(self):
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.offset)

    def closeEvent(self, event):
        self.keyboard_listener.stop()

    def previous_page(self):
        if self.current_line > 0:
            self.current_line -= 1
            self.display_text(self.text_lines[self.current_line])
            self.reset_idle_timer()

    def next_page(self):
        if self.current_line < len(self.text_lines) - 1:
            self.current_line += 1
            self.display_text(self.text_lines[self.current_line])
            self.reset_idle_timer()

    def exit(self):
        with open("page", "wb") as f:
            page_len = len(hex(self.current_line)[2:])//2 + len(hex(self.current_line)[2:])%2
            page = self.current_line.to_bytes(page_len, 'big')
            f.write(page)
        exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec_())
