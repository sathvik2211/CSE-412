import sqlite3
import requests
import random
from PyQt6.QtCore import QSize, Qt, QCoreApplication
from PyQt6.QtGui import (
    QStandardItem, 
    QPixmap, 
    QIcon
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QGroupBox,
    QMessageBox,
    QComboBox,
    QScrollArea,
    QDialog
)
import profileGUI, friendlist, SearchGui,Utilities

connect = sqlite3.connect('Project412.db')
cursor = connect.cursor()

# main windows for a photo album
class MainWindow(QMainWindow):

    def __init__(self,aid,uid):
        super().__init__()
        self.albumId = aid
        self.currentUid = uid
        QCoreApplication.instance().main_window = self
        self.photoOptionsIndex = 0
        
        # Get user name
        # Get album name
        name_query = f"SELECT fname, lname FROM Users WHERE uid = {self.currentUid}"
        cursor.execute(name_query)
        user_name = cursor.fetchone()

        # Get album name
        aname_query = f"SELECT aname FROM Albums WHERE aid = {self.albumId}"
        cursor.execute(aname_query)
        album_name = cursor.fetchone()[0]
        ##########################################################
        # create label for window title
        # Trying to show which user is logged into the application... not working
        self.window_title_label = QLabel(f"UserName: {user_name[0]} {user_name[1]}",objectName='window_title_label')
        self.window_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # create layout for album name
        album_name_layout = QHBoxLayout()
        # create label and line edit for album name
        self.album_name_label = QLabel(f"Album name: {album_name}")
        # add album name widgets to layout
        self.change_album_name_button = QPushButton("Change Album Name")
        self.change_album_name_button.clicked.connect(lambda: self.update_album_name())
        
        # add album name widgets to layout
        album_name_layout.addWidget(self.album_name_label,15)
        album_name_layout.addWidget(self.change_album_name_button,85)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.vertical_layout = QVBoxLayout(central_widget)
        # add title label and album name layout to vertical layout
        self.vertical_layout.addWidget(self.window_title_label)
        self.vertical_layout.addLayout(album_name_layout)
        # Create a horizontal layout for the "Upload" button and the "Delete" and "Delete Album" button
        button_layout = QHBoxLayout()
        self.vertical_layout.addLayout(button_layout)

        photoOptions = QComboBox()
        photoOptions.addItems(['Personal', 'Recommended', 'All'])
        photoOptions.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        photoOptions.currentIndexChanged.connect(self.displayPhotos)
        button_layout.addWidget(photoOptions)

        # Eric - Search Window button
        search_button = QPushButton("Search")
        search_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        button_layout.addWidget(search_button)
        search_button.clicked.connect(self.searchButtonEvent)

        # Eric - Friend's List button
        friend_button = QPushButton("Friends List")
        friend_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        button_layout.addWidget(friend_button)
        friend_button.clicked.connect(self.friendButtonEvent)

        # Add upload button to main window layout
        upload_button = QPushButton("Upload Photos")
        upload_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        button_layout.addWidget(upload_button)
        upload_button.clicked.connect(self.upload_photo)

        #########################################################
        # Add delete album button to main window layout
        delete_album_button = QPushButton("Delete Album")
        delete_album_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        button_layout.addWidget(delete_album_button)
        # create button to delete album and reset to default state
        delete_album_button.clicked.connect(self.delete_album)

        # Eric - Edit Profile button
        edit_button = QPushButton("Edit Profile")
        edit_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        button_layout.addWidget(edit_button)
        edit_button.clicked.connect(self.editProfileButtonEvent)

        # Eric - Log out button
        logout_button = QPushButton("Logout")
        logout_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        button_layout.addWidget(logout_button)
        logout_button.clicked.connect(self.logoutButtonEvent)

        # Create QGroupBox containing ScrollableArea that holds Posts
        photosGroupBox = QGroupBox("Photos")
        photosGroupBox.setMinimumHeight(300)
        photosVBoxLayout = QVBoxLayout()
        photosGroupBox.setLayout(photosVBoxLayout)

        contentScrollableWidget = QScrollArea()
        photosVBoxLayout.addWidget(contentScrollableWidget)
        contentScrollableWidget.setWidgetResizable(True)

        self.contentWidget = QWidget()
        contentWidgetVBoxLayout = QVBoxLayout()
        self.contentWidget.setLayout(contentWidgetVBoxLayout)
        contentScrollableWidget.setWidget(self.contentWidget)
        # Display Photos into contentWidget
        self.displayPhotos()

        self.vertical_layout.addWidget(photosGroupBox)

        footerHbox = QHBoxLayout()

       # Top 10 Contributors Section
        top10GroupBox = QGroupBox("Top 10 Contributors")
        top10Layout = QHBoxLayout()
        top10Layout.setContentsMargins(0, 10, 0, 0)
        top10GroupBox.setLayout(top10Layout)

        # Create a Two Columns to display the top 10 contributors
        top10Section1 = QWidget()
        top10VBoxLayout1 = QVBoxLayout()
        top10VBoxLayout1.setContentsMargins(0, 0, 0, 0)
        top10Section1.setLayout(top10VBoxLayout1)
        top10Section2 = QWidget()
        top10VBoxLayout2 = QVBoxLayout()
        top10VBoxLayout2.setContentsMargins(0, 0, 0, 0)
        top10Section2.setLayout(top10VBoxLayout2)

        # Query the database for the top 10 contributors
        query = "SELECT u.fname || ' ' || u.lname AS name, COUNT(*) AS num_comments FROM Comments c JOIN Photos p ON c.pid = p.pid JOIN Users u ON c.uid = u.uid WHERE c.comment IS NOT NULL GROUP BY c.uid HAVING COUNT(*) ORDER BY num_comments DESC LIMIT 10;"
        contributions = cursor.execute(query).fetchall()
        rank = 1  # Tracks Current Rank
        for contribution in contributions:
            newContributorWidget = QWidget(objectName="newContributorWidget")
            newContributorHBoxLayout = QHBoxLayout()
            newContributorWidget.setStyleSheet("#newContributorWidget{border: 1px solid grey;}")
            newContributorWidget.setLayout(newContributorHBoxLayout)

            newContributorLabel = QLabel(f"{rank}. ")
            newContributorNameLabel = QLabel(contribution[0])
            newContributorCountLabel = QLabel(str(contribution[1]))
            newContributorHBoxLayout.addWidget(newContributorLabel, 10)
            newContributorHBoxLayout.addWidget(newContributorNameLabel, 45)
            newContributorHBoxLayout.addWidget(newContributorCountLabel, 45, alignment=Qt.AlignmentFlag.AlignRight)

            # First 5 top contributors on the left vbox
            if rank <= 5:
                top10VBoxLayout1.addWidget(newContributorWidget)
            else:
                top10VBoxLayout2.addWidget(newContributorWidget)

            rank += 1

        # Add the top 10 contributors section to the main layout
        top10Layout.addWidget(top10Section1, 45)
        top10Layout.addWidget(top10Section2, 45)
        self.vertical_layout.addWidget(top10GroupBox)
        
        #end of contribution part
        
        popularTagsGroupBox = QGroupBox("Popular Tags")
        tags_layout = QHBoxLayout()
        tags_layout.setContentsMargins(0, 10, 0, 0)
        popularTagsGroupBox.setLayout(tags_layout)
       
        # Create a Two Columns to display the popular tags
        popularTagsSection1 = QWidget()
        popularTagsVBoxLayout1 = QVBoxLayout()
        popularTagsVBoxLayout1.setContentsMargins(0,0,0,0)
        popularTagsSection1.setLayout(popularTagsVBoxLayout1)
        popularTagsSection2 = QWidget()
        popularTagsVBoxLayout2 = QVBoxLayout()
        popularTagsVBoxLayout2.setContentsMargins(0,0,0,0)
        popularTagsSection2.setLayout(popularTagsVBoxLayout2)

        tagTuples = cursor.execute("SELECT tag, COUNT(*) FROM tags GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
        tagCount = 0 # Tracks Current Rank
        for tag in tagTuples:
            newTagWidget = QWidget(objectName = "newTagWidget")
            newTagHBoxLayout = QHBoxLayout()
            newTagWidget.setStyleSheet("#newTagWidget{border: 1px solid grey;}")
            newTagWidget.setLayout(newTagHBoxLayout)

            newTagLabel = QLabel(f"{tagCount+1}. ")
            newTagButton = Utilities.TagButton(tag)
            newTagButton.adjustSize()
            newTagCountLabel = QLabel(str(tag[1]))
            newTagHBoxLayout.addWidget(newTagLabel,10)
            newTagHBoxLayout.addWidget(newTagButton,45)
            newTagHBoxLayout.addWidget(newTagCountLabel,45,alignment=Qt.AlignmentFlag.AlignRight)
            # First 5 top tags on the left vbox
            if tagCount < 5:
                popularTagsVBoxLayout1.addWidget(newTagWidget)
            else:
                popularTagsVBoxLayout2.addWidget(newTagWidget)

            tagCount += 1
        # Add the popular tags section to the main layout
        tags_layout.addWidget(popularTagsSection1,45)
        tags_layout.addWidget(popularTagsSection2,45)

        footerHbox.addWidget(top10GroupBox)
        footerHbox.addWidget(popularTagsGroupBox)
        self.vertical_layout.addLayout(footerHbox)

    ################################################################################
    # Update album name
    ################################################################################
    def update_album_name(self):
        if self.albumId is not None:
            # display a text box to get the new album name
            new_name, ok_pressed = QInputDialog.getText(self, "Change Album Name", "New album name:")
            if ok_pressed and new_name != '':
                # update the album name in the database
                query = "UPDATE Albums SET aname = ? WHERE aid = ?"
                values = (new_name, self.albumId)
                cursor.execute(query, values)
                connect.commit()
                # update the album name label
                self.album_name_label.setText(f"Album name: {new_name}")
    
    #######################################################################
    # When this funciton is called, clear all photos and album.
    ############################################################################

    def delete_album(self):
        # delete all photos and captions from the album in the database
        query = f"DELETE FROM Photos WHERE aid = {self.albumId}"
        cursor.execute(query)
        connect.commit()

        # reset the album title edit to the default state
        self.album_name_label.setText(f"Album name: Album")
        self.displayPhotos(index = self.photoOptionsIndex)

    # Implements the upload photo button and allow user to upload via url
    def upload_photo(self):
        # get album id from current album
        aid = self.albumId
        
        # Photo URL
        while True:
            photo_url, ok = QInputDialog.getText(self, "Upload Photo", "Enter photo URL:")
            if not ok:
                return
            # Check if the URL is valid
            # Fix url check
            # Check if the URL is valid and starts with "http://" or "https://"
            if photo_url.startswith("http://") or photo_url.startswith("https://"):
                response = requests.get(photo_url)
                if response.status_code // 100 == 2:  
                    break
            QMessageBox.warning(self, "Invalid URL", "Use 'http://' or 'https://'")
        ## Need to implement tags
        caption, ok = QInputDialog.getText(self, "Add Caption", "Enter photo caption:")
        if not ok:
            caption = None
        
        # Generate a unique PID not in the database
        while True:
            pid = random.randint(0000, 9999)
            cursor.execute("SELECT pid FROM Photos WHERE pid = ?", (pid,))
            if not cursor.fetchone():
                break
        
        # add new photo to database
        query = "INSERT INTO Photos (pid, aid, caption, data) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (pid, aid, caption, f'"{photo_url}"'))
        
        # prompt the user to enter tags
        tags, ok = QInputDialog.getText(self, "Add Tags", "Enter tags (separated by commas):")
        if ok:
            # split the tags by comma
            tag_list = tags.split(",")
            # insert the tags into the Tags table with the pid of the newly uploaded photo
            for tag in tag_list:
                query = "INSERT INTO Tags (pid, tag) VALUES (?, ?)"
                cursor.execute(query, (pid, tag.strip()))
        
        connect.commit()

    # Move to Login Frame
    def logoutButtonEvent(self):
        self.parent().setCurrentIndex(0)
        self.deleteLater()
    # Adds a new ProfileWindow to StackFrame
    def editProfileButtonEvent(self):
        self.parent().addWidget(profileGUI.ProfileWindow(self.currentUid))
        self.parent().setCurrentIndex(2)
    # Adds a new SearchGui to StackFrame
    def searchButtonEvent(self):
        self.parent().addWidget(SearchGui.SearchGui(self.albumId,self.currentUid))
        self.parent().setCurrentIndex(2)
    # Adds a new FriendsPage to StackFrame
    def friendButtonEvent(self):
        self.parent().addWidget(friendlist.FriendsPage(self.currentUid))
        self.parent().setCurrentIndex(2)

    def displayPhotos(self, index = 0):
        self.photoOptionsIndex = index
        layout = self.contentWidget.layout()
        # Resets Layout
        while layout.count():
            item = layout.takeAt(0)
            temp = item.widget()
            if temp is not None:
                temp.deleteLater()
        photoTuples = ()
        # Display Post in the main window with captions 
        if(self.photoOptionsIndex == 0): # User Owned Photos
            photoTuples = cursor.execute("SELECT * FROM Photos WHERE aid = ?",(self.albumId,)).fetchall()
        elif(self.photoOptionsIndex == 1): # Disjuctive Search for recommended photos
            photoTuples = self.recommendedPhotos()
        elif (self.photoOptionsIndex == 2): # All Photos
            photoTuples = cursor.execute("SELECT * FROM Photos").fetchall()

        for photoTuple in photoTuples:
            if self.photoOptionsIndex == 0:
                newPost = Utilities.PostWidget(photoTuple,self.currentUid,displayDelete = True)
            else:
                newPost = Utilities.PostWidget(photoTuple,self.currentUid)
            layout.addWidget(newPost)
    # Provides top photos from other users containing the top 5 most used tags
    def recommendedPhotos(self):
    # Get top 5 tags used by User
        tagQuery = """
            SELECT Tags.tag
            FROM Tags
            JOIN Photos ON Photos.pid = Tags.pid
            JOIN Albums ON Photos.aid = Albums.aid
            WHERE Albums.uid = ?
            GROUP BY Tags.tag
            ORDER BY Count(Tags.tag) DESC
            LIMIT 5;
        """
        tags = cursor.execute(tagQuery, (self.currentUid,)).fetchall()

        queryInput = [self.currentUid]
        for tag in tags:
            queryInput.append(tag[0])

        placeholder = ",".join(['?' for i in tags])

        photoQuery = f"""
            SELECT Photos.*
            FROM Photos
            JOIN Tags ON Photos.pid = Tags.pid
            JOIN Albums ON Photos.aid = Albums.aid
            WHERE NOT Albums.uid = ?
            AND Tags.tag IN ({placeholder})
            GROUP BY Photos.pid
            ORDER BY COUNT(Photos.pid) DESC;
        """
        photoTuples = cursor.execute(photoQuery, (queryInput)).fetchall()
        return photoTuples
    
    def show_photos_with_tag(self, tag):
        # Query to get photos and captions that contain the specified tag
        query = f"""
        SELECT *
        FROM Photos p 
        JOIN Tags t ON p.pid = t.pid
        WHERE t.tag = ?;
        """

        cursor.execute(query,(tag,))
        results = cursor.fetchall()

        # Create a QDialog for the popup window
        popup_window = QDialog(self)
        popup_window.setWindowTitle(f"Photos with tag '{tag}'")
        popup_window_layout = QVBoxLayout(popup_window)
        
        tagScrollableWidget = QScrollArea()
        popup_window_layout.addWidget(tagScrollableWidget)
        tagScrollableWidget.setWidgetResizable(True)

        tagWidget = QWidget()
        tagVBoxLayout = QVBoxLayout()
        tagWidget.setLayout(tagVBoxLayout)
        tagScrollableWidget.setWidget(tagWidget)
        

        # Display photos with captions in the popup window
        for row in results:
            newPost = Utilities.PostWidget(row,self.currentUid)
            tagVBoxLayout.addWidget(newPost)

        # Show the popup window
        popup_window.exec()

# Launch the window
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
