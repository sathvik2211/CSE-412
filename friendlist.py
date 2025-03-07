import os
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import datetime

class Friend:
    def __init__(self, uid, fname, lname):
        self.uid = uid
        self.fname = fname
        self.lname = lname


class FriendsPage(QWidget):
    def __init__(self, current_user_id):
        super().__init__()
        self.current_user_id = current_user_id
        # Get the path to the current directory and the database file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'Project412.db')

        # Create a connection to the SQLite database
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        # Fetch the friends of the current user
        self.friends = []
        self.cursor.execute(f"SELECT fuid FROM Friends WHERE uid = {self.current_user_id}")
        rows = self.cursor.fetchall()
        friend_ids = [row[0] for row in rows]

        # Fetch the details of the user's friends from the Users table
        self.cursor.execute(f"SELECT uid, lname, fname FROM Users WHERE uid IN ({','.join(map(str, friend_ids))})")
        rows = self.cursor.fetchall()
        for row in rows: 
            uid = row[0]
            fname = row[1]
            lname = row[2]
            self.friends.append(Friend(uid, fname, lname))

        # Create the UI elements for the friends page
        friends_label = QLabel('Friends')
        friends_label.setFont(QFont('Arial', 16))

        self.friends_list = QListWidget()
        for friend in self.friends:
            item = QListWidgetItem()
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f'{friend.uid} {friend.lname}, {friend.fname}'))
            # button = QPushButton('Add Friend')
            # button.clicked.connect(lambda _, uid=friend.uid: self.add_friend(self.current_user_id, uid))
            # layout.addWidget(button)
            # layout.setAlignment(button, Qt.AlignmentFlag.AlignRight)
            widget = QWidget()
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.friends_list.addItem(item)
            self.friends_list.setItemWidget(item, widget)

        # Create a list of recommended friends by retrieving data from the database
        recommend_label = QLabel('Recommendations')
        recommend_label.setFont(QFont('Arial', 16))

        self.recommend_list = QListWidget()
        self.cursor.execute(f"""
        SELECT a.uid, a.lname, a.fname
        FROM  users a
        INNER JOIN Friends ff ON a.uid = ff.fuid
        INNER JOIN Friends f ON ff.uid = f.fuid
        WHERE f.uid = {self.current_user_id} AND ff.fuid NOT IN (
        SELECT fuid 
        FROM Friends 
        WHERE uid = {self.current_user_id})
        AND a.uid != {self.current_user_id}
        """)

        rows = self.cursor.fetchall()
        for row in rows:
            uid = row[0]
            lname = row[1]
            fname = row[2]
            item = QListWidgetItem()
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f'{uid} {lname}, {fname}'))
            button = QPushButton('Add Friend')
            button.clicked.connect(lambda _, uid=uid, item=item: (self.add_friend(self.current_user_id, uid), self.recommend_list.takeItem(self.recommend_list.row(item))))
            layout.addWidget(button)
            layout.setAlignment(button, Qt.AlignmentFlag.AlignRight)
            widget = QWidget()
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.recommend_list.addItem(item)
            self.recommend_list.setItemWidget(item, widget)

        # Set up the layout for the friends page
        friends_layout = QVBoxLayout()
        friends_layout.addWidget(friends_label)
        friends_layout.addWidget(self.friends_list)

        recommend_layout = QVBoxLayout()
        recommend_layout.addWidget(recommend_label)
        recommend_layout.addWidget(self.recommend_list)

        main_layout = QHBoxLayout()
        main_layout.addLayout(friends_layout)
        main_layout.addLayout(recommend_layout)

        # Eric - Back button
        backButton = QPushButton("Back")
        backButton.clicked.connect(self.backButtonEvent)
        main_layout.addWidget(backButton)

        self.setLayout(main_layout)

        # Set the window properties
        self.setWindowTitle('Friends Page')
        self.resize(600, 400)


    def add_friend(self, uid, fuid):
        fdate = datetime.date.today()
        self.cursor.execute(f"INSERT INTO Friends (uid, fuid, fdate) VALUES (?, ?, ?)", (uid, fuid, fdate))
        self.connection.commit()
        # Refresh the friend list to show the newly added friend
        self.refresh_friends_list()

    def refresh_friends_list(self):
        # Clear the current list of friends
        self.friends_list.clear()

        # Fetch the friends of the current user
        self.friends = []
        self.cursor.execute(f"SELECT fuid FROM Friends WHERE uid = {self.current_user_id}")
        rows = self.cursor.fetchall()
        friend_ids = [row[0] for row in rows]

        # Fetch the details of the user's friends from the Users table
        self.cursor.execute(f"SELECT uid, lname, fname FROM Users WHERE uid IN ({','.join(map(str, friend_ids))})")
        rows = self.cursor.fetchall()
        for row in rows:
            uid = row[0]
            fname = row[1]
            lname = row[2]
            self.friends.append(Friend(uid, fname, lname))

        # Update the friends list UI with the new data
        for friend in self.friends:
            item = QListWidgetItem()
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f'{friend.uid} {friend.lname}, {friend.fname}'))
            # button = QPushButton('Add Friend')
            # button.clicked.connect(lambda _, uid=self.current_user_id, fuid=friend.uid: self.add_friend(uid, fuid))
            # layout.addWidget(button)
            # layout.setAlignment(button, Qt.AlignmentFlag.AlignRight)
            widget = QWidget()
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.friends_list.addItem(item)
            self.friends_list.setItemWidget(item, widget)

    def closeEvent(self, event):
        # This function is called when the window is closed
        self.connection.close()
        event.accept()

    def backButtonEvent(self):
        self.parent().setCurrentIndex(1)
        self.deleteLater()

if __name__ == '__main__':
    app = QApplication([])
    friends_page = FriendsPage(current_user_id=1)  # Replace with the ID of the current user
    friends_page.show()
    app.exec()