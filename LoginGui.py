import sys
import sqlite3
import hashlib
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QLabel, QStackedWidget, QWidget, QMainWindow
from PyQt6.uic import loadUi
from datetime import datetime
import MainScreen


class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("login.ui", self)
        self.loginbutton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.createAccButton.clicked.connect(self.gotocreate)
        self.error = self.findChild(QLabel, "error")
        self.currentUser = None

    def loginfunction(self):
        email = self.email.text()
        password = self.password.text()
        if len(email) == 0 or len(password) == 0:
            self.error.setText("Please input all fields")
        else:
            connection = sqlite3.connect("Project412.db")
            cur = connection.cursor()
            query = "SELECT uid,pass FROM Users WHERE email=?"
            cur.execute(query, (email,))
            results = cur.fetchone()
            if results is not None and results[1] == hashlib.sha256(password.encode()).hexdigest():
                aid = cur.execute("SELECT aid FROM Albums WHERE uid = ?", (results[0],)).fetchone()
                mainScreen = MainScreen.MainWindow(aid[0], results[0])
                self.parent().addWidget(mainScreen)
                self.parent().setCurrentIndex(1)
                self.error.setText("")
            else:
                self.error.setText("Invalid username or password")

    def gotocreate(self):
        # Change displayed Widget to CreateAccount
        createAcc = CreateAcc()
        self.parent().addWidget(createAcc)
        self.parent().setCurrentIndex(1)


class CreateAcc(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("create.ui", self)
        self.signUp.clicked.connect(self.create_acc_function)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.error = self.findChild(QLabel, "error")
        self.con_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.gobacklogin.clicked.connect(self.goToLogin)
    def create_acc_function(self):
        email = self.email.text()
        password = self.password.text()
        fname = self.fname.text()
        lname = self.lname.text()
        dob = self.dob.text()
        confirmpassword = self.con_password.text()
        album_name = self.album_name_input.text()

        if len(email) == 0 or len(password) == 0 or len(fname) == 0 or len(lname) == 0 or len(dob) == 0:
            self.error.setText("Please fill in all inputs")
        elif password != confirmpassword:
            self.error.setText("Passwords do not match")
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            connection = sqlite3.connect("Project412.db")
            cur = connection.cursor()

            # Check if email already exists in the database
            cur.execute("SELECT * FROM Users WHERE email=?", (email,))
            result = cur.fetchone()
            if result:
                self.error.setText("Email already exists")
            else:
                user_info = [fname, lname, email, dob, hashed_password]
                cur.execute('INSERT INTO Users (fname,lname,email,dofb,pass) VALUES (?,?,?,?,?)', user_info)
                connection.commit()

                uid = cur.lastrowid

                if album_name:
                    album_info = [uid, album_name, datetime.now().strftime('%m/%d/%Y')]
                    cur.execute('INSERT INTO Albums (uid,aname,date) VALUES (?,?,?)', album_info)
                    connection.commit()

                connection.close()

                self.error.setText("Account created successfully")
                self.goToLogin()

    def goToLogin(self):
        # Change displayed Widget to Login
        self.parent().setCurrentIndex(0)
        self.deleteLater()


if __name__ == '__main__':
    app = QApplication([])
    window = QStackedWidget()
    # Stack index = 0
    login = Login()
    window.addWidget(login)
    # Stack index = 1
    createAcc = CreateAcc()
    window.addWidget(createAcc)
    window.setGeometry(500, 100, 1000, 900)  # x-cord, y-cord, width of window, height of window
    window.show()
    app.exec()
