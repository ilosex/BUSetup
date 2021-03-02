#! /usr/bin/python3
import sys

from PyQt5 import QtWidgets

from UI import MyUI_Qt5
import src


def main():

    control_unit = src.SettingsTools.AgrodroidBU(src.default_ssh_config)
    app = QtWidgets.QApplication([])
    application = MyUI_Qt5.UI(control_unit)
    application.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
