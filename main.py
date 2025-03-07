from PyQt6.QtWidgets import QApplication, QStackedWidget
import LoginGui

if __name__ == '__main__':
    app = QApplication([])
    window = QStackedWidget()
    # Stack index = 0
    login = LoginGui.Login()
    window.addWidget(login)

    window.setGeometry(500,100,1000,900)
    window.show()
    app.exec()
