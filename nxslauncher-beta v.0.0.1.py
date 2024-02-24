import subprocess
from uuid import uuid1
import minecraft_launcher_lib
from PyQt5 import QtCore, QtGui, QtWidgets
from random_username.generate import generate_username

minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory().replace('minecraft', 'nxslauncher')


class LaunchThread(QtCore.QThread):
    launch_setup_signal = QtCore.pyqtSignal(str, str)
    progress_update_signal = QtCore.pyqtSignal(int, int, str)
    state_update_signal = QtCore.pyqtSignal(bool)

    version_id = ''
    username = ''

    progress = 0
    progress_max = 0
    progress_label = ''

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)

    def launch_setup(self, version_id, username):
        self.version_id = version_id
        self.username = username

    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress(self, value):
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def run(self):
        self.state_update_signal.emit(True)

        minecraft_launcher_lib.install.install_minecraft_version(versionid=self.version_id,
                                                                 minecraft_directory=minecraft_directory,
                                                                 callback={'setStatus': self.update_progress_label,
                                                                           'setProgress': self.update_progress,
                                                                           'setMax': self.update_progress_max})

        if self.username == '':
            self.username = generate_username()[0]

        options = {
            'username': self.username,
            'uuid': str(uuid1()),
            'token': ''
        }
        subprocess.call(minecraft_launcher_lib.command.get_minecraft_command(version=self.version_id,
                                                                             minecraft_directory=minecraft_directory,
                                                                             options=options))

        self.state_update_signal.emit(False)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(296, 200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMaximumSize(QtCore.QSize(300, 200))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("pic.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label, 0, QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.username = QtWidgets.QLineEdit(self.centralwidget)
        self.username.setObjectName("Username")
        self.username.setPlaceholderText('Username')
        self.verticalLayout.addWidget(self.username)
        self.version_select = QtWidgets.QComboBox(self.centralwidget)
        self.version_select.setObjectName("Version")
        self.verticalLayout.addWidget(self.version_select)

        for version in minecraft_launcher_lib.utils.get_version_list():
            self.version_select.addItem(version['id'])

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.start_progress = QtWidgets.QProgressBar(self.centralwidget)
        self.start_progress.setProperty("value", 24)
        self.start_progress.setObjectName("start_progress")
        self.start_progress.setVisible(False)
        self.verticalLayout.addWidget(self.start_progress)
        self.start_progress.setVisible(False)
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setObjectName("pushButton")
        self.start_button.setText('PLAY')
        self.start_button.clicked.connect(self.launch_game)
        self.verticalLayout.addWidget(self.start_button)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)
        MainWindow.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def state_update(self, value):
        self.start_button.setDisabled(value)
        self.start_progress.setVisible(value)

    def update_progress(self, progress, max_progress, label):
        self.start_progress.setValue(progress)
        self.start_progress.setMaximum(max_progress)

    def launch_game(self):
        self.launch_thread.launch_setup_signal.emit(self.version_select.currentText(), self.username.text())
        self.launch_thread.start()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
