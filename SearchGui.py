import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import Utilities

connect = sqlite3.connect('Project412.db')
cursor = connect.cursor()

class SearchGui(QMainWindow):
    def __init__(self,albumId,currentUid):
        super(SearchGui, self).__init__()
        self.albumId = albumId 
        self.searchIndex = 0
        self.searchText = ""
        self.currentUid = currentUid

        self.displaySearch()
    
    def displaySearch(self):
        
        def changeSearch(i):
            self.searchIndex = i 
        # dynamically changes search results as user types
        def search():
            widget = self.findChild(QWidget,'contentWidget')
            layout = widget.layout()
            # Resets Layout
            while layout.count():
                item = layout.takeAt(0)
                temp = item.widget()
                if temp is not None:
                    temp.deleteLater()

            if(self.searchIndex == 0): #Users
                # Can search First Name, Last Name, or First+Last with space between
                if searchBar.text() == '':
                    userTuples = cursor.execute("SELECT uid,fname,lname FROM Users WHERE NOT uid=?;",(self.currentUid,)).fetchall()
                else:
                    searchText = '%' + searchBar.text() + '%'
                    userTuples = cursor.execute("SELECT uid,fname,lname FROM Users WHERE (fname LIKE ? OR lname LIKE ? OR fname || ' ' || lname LIKE ?) AND NOT uid=?;",(searchText,searchText,searchText,self.currentUid)).fetchall()
                for userTuple in userTuples:
                    newUserSelection = Utilities.UserWidget(userTuple,self.currentUid)
                    layout.addWidget(newUserSelection)

            elif(self.searchIndex == 1): #Tags
                # Does not require Hashtag to search
                if searchBar.text() == '':
                    pass
                splitString = searchBar.text().split()
                countValue = len(splitString)-1
                adjustedStringList = ['#'+ tag +'' for tag in splitString]
                placeholder = ",".join(['?' for i in adjustedStringList])
                photoTuples = cursor.execute(f"SELECT * FROM Photos WHERE pid IN (SELECT pid FROM Tags WHERE tag IN ({placeholder}) GROUP BY pid HAVING COUNT(*) > {countValue});",(adjustedStringList)).fetchall()
                for photoTuple in photoTuples:
                    newPost = Utilities.PostWidget(photoTuple,self.currentUid)
                    layout.addWidget(newPost)

            elif(self.searchIndex == 2): #Comments
                if searchBar.text() == '':
                    pass
                searchText = '%' + searchBar.text() + '%'
                userTuples = cursor.execute("SELECT uid,fname,lname FROM Users WHERE uid IN (SELECT uid FROM Comments WHERE comment LIKE ?) GROUP BY uid ORDER BY COUNT(uid) DESC;",(searchText,)).fetchall()
                for userTuple in userTuples:
                    newUserSelection = Utilities.UserWidget(userTuple,self.currentUid)
                    layout.addWidget(newUserSelection)

        #top Level
        topVbox = QVBoxLayout()

        # Search Bar Components
        searchBarHBox = QHBoxLayout()
        searchBarWidget = QWidget()

        backButton = QPushButton("Back")
        backButton.clicked.connect(self.backButtonEvent)
        searchBarHBox.addWidget(backButton)
       
        searchOptions = QComboBox()
        searchOptions.addItems(['Users', 'Tags', 'Comments'])
        searchOptions.currentIndexChanged.connect(changeSearch)
        searchOptions.currentIndexChanged.connect(search)

        searchBar = QLineEdit()
        searchBar.setPlaceholderText("Enter Text Here")
        # searchBar.textChanged.connect(search)

        searchButton = QPushButton("Search")
        searchButton.clicked.connect(search)


        searchBarHBox.addWidget(searchOptions)
        searchBarHBox.addWidget(searchBar)
        searchBarHBox.addWidget(searchButton)

        searchBarWidget.setLayout(searchBarHBox)

        topVbox.addWidget(searchBarWidget)
        # Content box
        contentVBox = QVBoxLayout()
        contentVBox.setAlignment(Qt.AlignmentFlag.AlignTop)
        contentVBox.setSpacing(0)
        contentVBox.setContentsMargins(0,0,0,0)

        contentWidget = QWidget(objectName="contentWidget")

        contentWidget.setLayout(contentVBox)
        # contentWidget.setStyleSheet("border: 1px solid")

        contentScrollableWidget = QScrollArea()
        contentScrollableWidget.setWidgetResizable(True)
        contentScrollableWidget.setWidget(contentWidget)

        topVbox.addWidget(contentScrollableWidget)

        topWidget = QWidget()
        topWidget.setLayout(topVbox)
        self.setCentralWidget(topWidget)
        search()
        topWidget.show()

    def backButtonEvent(self):
        self.parent().setCurrentIndex(1)
        self.deleteLater()
    
if __name__ == '__main__':
    app = QApplication([])
    window = SearchGui()
    window.setGeometry(500,100,1000,900) # x-cord, y-cord, width of window, height of window
    window.show()
    app.exec()