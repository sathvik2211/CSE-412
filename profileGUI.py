import os
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
import hashlib

class ProfileWindow(QWidget):
    def __init__(self,currentUid):
        super().__init__()
        self.currentUid = currentUid

        self.conn = sqlite3.connect('Project412.db')
        self.cur = self.conn.cursor()
        self.default_user_data = self.get_user_by_uid(self.currentUid)
        #Set up the user profile fields
        # self.uid_edit = QLineEdit()
        # self.uid_edit.setFixedWidth(200)
        # self.uid_edit.setFixedHeight(20)
        # self.uid_edit.setReadOnly(True)

        self.fname_edit = QLineEdit()
        self.fname_edit.setFixedWidth(200)
        self.fname_edit.setFixedHeight(20)

        self.lname_edit = QLineEdit()
        self.lname_edit.setFixedWidth(200)
        self.lname_edit.setFixedHeight(20)

        self.dob_edit = QDateEdit()
        self.dob_edit.setFixedWidth(200)
        self.dob_edit.setFixedHeight(20)
        
        self.htown_edit = QLineEdit()
        self.htown_edit.setFixedWidth(200)
        self.htown_edit.setFixedHeight(20)

        self.email_edit = QLineEdit()
        self.email_edit.setFixedWidth(200)
        self.email_edit.setFixedHeight(20)
        self.email_edit.setReadOnly(True)

        self.password_edit = QLineEdit()
        self.password_edit.setFixedWidth(200)
        self.password_edit.setFixedHeight(20)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.gender_edit = QComboBox()
        self.gender_edit.addItems(['male', 'female'])
        
        # Eric - Populate Fields with current User Info
        self.set_profile(*self.default_user_data)

        # Set up the labels for the user profile fields
        #uid_label = QLabel('UID:')
        fname_label = QLabel('First Name:')
        lname_label = QLabel('Last Name:')
        dob_label = QLabel('Date of Birth:')
        htown_label = QLabel('Home Town:')
        email_label = QLabel('Email:')
        password_label = QLabel('Password:')
        gender_label = QLabel('Gender:')

        # Set up the buttons for saving and resetting the user profile
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_profile)
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset_profile)
        back_button = QPushButton('Back')
        back_button.clicked.connect(self.exitProfile)

        # Set up the layout for the user profile fields
        profile_layout = QVBoxLayout()
        # profile_layout.addWidget(uid_label)
        # profile_layout.addWidget(self.uid_edit)
        profile_layout.addWidget(fname_label)
        profile_layout.addWidget(self.fname_edit)
        profile_layout.addWidget(lname_label)
        profile_layout.addWidget(self.lname_edit)
        profile_layout.addWidget(dob_label)
        profile_layout.addWidget(self.dob_edit)
        profile_layout.addWidget(htown_label)
        profile_layout.addWidget(self.htown_edit)
        profile_layout.addWidget(email_label)
        profile_layout.addWidget(self.email_edit)
        profile_layout.addWidget(password_label)
        profile_layout.addWidget(self.password_edit)
        profile_layout.addWidget(gender_label)
        profile_layout.addWidget(self.gender_edit)

        # Set up the layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(back_button)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(profile_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Set the window properties
        self.setWindowTitle('Profile Viewer and Editor')
        self.setMinimumSize(250, 400)

    def get_user_by_uid(self, uid):
        self.cur.execute('SELECT * FROM Users WHERE uid=?', (uid,))
        return self.cur.fetchone()
    
    def set_profile(self, uid, fname, lname, email, dob, htown, password, gender):
        #self.uid_edit.setText(str(uid))
        self.fname_edit.setText(fname)
        self.lname_edit.setText(lname)
        date = QDate.fromString(dob, 'MM/dd/yyyy')
        self.dob_edit.setDate(date)
        self.htown_edit.setText(htown)
        self.email_edit.setText(email)
        self.password_edit.setText(password)
        if gender == "male":
            self.gender_edit.setCurrentIndex(0)
        elif gender == "female":
            self.gender_edit.setCurrentIndex(1)

    def get_profile(self):
        #uid = int(self.uid_edit.text())
        fname = self.fname_edit.text()
        lname = self.lname_edit.text()
        dob = self.dob_edit.date().toString('MM/dd/yyyy')
        htown = self.htown_edit.text()
        email = self.email_edit.text()
        password = self.password_edit.text()
        gender = self.gender_edit.currentText()
        return fname, lname, dob, htown, email, password, gender

    def save_profile(self):
        fname, lname, dob, htown, email, password, gender = self.get_profile()
        current_password = self.default_user_data[6]  # retrieve the current hashed password from the default_user_data
        if password == current_password:  # if password hasn't been modified
            hashed_password = current_password  # reuse the current hashed password
        else:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # hash the new password
        query = """
        UPDATE Users SET fname=?, lname=?, email=?, dofb=?, htown=?, pass=?, gender=?
        WHERE uid=?
        """
        values = (fname, lname, email, dob, htown, hashed_password, gender, self.currentUid)
        self.cur.execute(query, values)
        self.conn.commit()
        self.default_user_data = self.get_user_by_uid(self.currentUid)
        QMessageBox.information(self, 'Profile Saved', 'Your profile has been saved.')
        self.parent().findChild(QLabel,'window_title_label').setText(f"UserName: {fname}, {lname}")
        self.exitProfile()
        
    def reset_profile(self):
        #self.uid_edit.setText(str(self.currentUid))
        self.fname_edit.clear()
        self.lname_edit.clear()
        self.dob_edit.setDate(QDate.currentDate())
        self.htown_edit.clear()
        self.password_edit.clear()
        self.gender_edit.setCurrentIndex(0)
        QMessageBox.information(self, 'Profile Reset', 'Your profile has been reset.')
        #self.exitProfile()

    #Exits to MainScreen
    def exitProfile(self):
        self.parent().setCurrentIndex(2)
        self.deleteLater()

if __name__ == '__main__':
    # Create the application and window instances
    app = QApplication([])
    window = ProfileWindow()

    # Set some initial profile data
    uid, fname, lname, email, dob, htown, password, gender = window.default_user_data
    window.set_profile(uid, fname, lname, dob, htown, email, password, gender)

    # Show the window
    window.show()

    # Run the event loop
    app.exec()
