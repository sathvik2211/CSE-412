from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sqlite3
import requests

connect = sqlite3.connect('Project412.db')
cursor = connect.cursor()

class UserWidget(QWidget):
    def __init__(self, userTuple,uid):
        super(UserWidget,self).__init__()
        self.searchedUserID = userTuple[0]
        self.firstName = userTuple[1]
        self.lastName = userTuple[2]
        self.currentUserID = uid
        self.hBoxLayout = QHBoxLayout()
        self.setLayout(self.hBoxLayout)
        self.createUserWidget()

    def createUserWidget(self):
        friendTuple = cursor.execute("SELECT * FROM Friends WHERE uid=? AND fuid=?;",(self.currentUserID,self.searchedUserID)).fetchone()
        fullName = QLabel(text=f"{self.firstName} {self.lastName}")
        self.hBoxLayout.addWidget(fullName)
        if not friendTuple:
            friendButton = QPushButton("Follow")
            friendButton.clicked.connect(self.followUser)
            self.hBoxLayout.addWidget(friendButton,alignment=Qt.AlignmentFlag.AlignRight)
        else:
            friendText = QLabel("Already Following")
            self.hBoxLayout.addStretch(1)
            self.hBoxLayout.addWidget(friendText,alignment=Qt.AlignmentFlag.AlignRight)
            friendButton = QPushButton("Unfollow")
            friendButton.clicked.connect(self.unfollowUser)
            self.hBoxLayout.addWidget(friendButton,alignment=Qt.AlignmentFlag.AlignRight)
    
    def followUser(self): 
        from datetime import date
        todayDate = date.today()
        formatedDate = str(todayDate.month) + "/" + str(todayDate.day) + "/" + str(todayDate.year)
        cursor.execute("INSERT INTO Friends VALUES (?,?,?)",(self.currentUserID,self.searchedUserID,formatedDate))
        connect.commit()
        self.resetLayout()
        
    def unfollowUser(self):
        cursor.execute("DELETE FROM Friends WHERE uid=? AND fuid=?",(self.currentUserID,self.searchedUserID))
        connect.commit()
        self.resetLayout()
    # Resets Layout to reflect changes to Database
    def resetLayout(self):
        for i in reversed(range(self.layout().count())):
            widget = self.layout().takeAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.createUserWidget()

class PostWidget(QWidget):
    def __init__(self, photoTuple,currentUid,displayDelete = False):
        super(PostWidget,self).__init__()
        self.photoId = photoTuple[0]
        self.albumId = photoTuple[1]
        self.caption = photoTuple[2]
        self.data = photoTuple[3]
        self.tags = []
        self.currentUserID = currentUid
        self.displayDelete = displayDelete
        self.createPost()

    def createPost(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.addWidget(self.loadHeader())
        vBoxLayout.addWidget(self.loadPhoto())
        vBoxLayout.addWidget(self.loadTags())
        vBoxLayout.addWidget(self.loadChoices())
        vBoxLayout.addWidget(self.loadComments())
        vBoxLayout.setSpacing(0)
        self.setLayout(vBoxLayout)
    
    def loadHeader(self):
        def deletePost():
            cursor.execute("DELETE FROM Photos WHERE pid = ?",(self.photoId,))
            connect.commit()
            self.deleteLater()
        headerWidget = QWidget(objectName = 'headerWidget')
        hBoxLayout = QHBoxLayout()
        headerWidget.setLayout(hBoxLayout)
        headerWidget.setStyleSheet("#headerWidget{border: 1px solid grey;}")
        captionLabel = QLabel(self.caption)
        #Obtains font object assigned to widget and modify size
        font = captionLabel.font()
        font.setPointSize(16)
        captionLabel.setFont(font)
        hBoxLayout.addWidget(captionLabel)
        
        if self.displayDelete:
            deleteButton = QPushButton("Delete Photo")
            deleteButton.clicked.connect(deletePost)
            hBoxLayout.addWidget(deleteButton, alignment = Qt.AlignmentFlag.AlignRight)

        return headerWidget
        
    def loadPhoto(self):
        imageLabel = QLabel(objectName = 'imageLabel')
        imageLabel.setStyleSheet("#imageLabel{border: 1px solid grey;}")
        pixmap = QPixmap()
        # Sends request to obtain image data and loads it into pixmap
        pixmap.loadFromData(requests.get(self.data[1:-1]).content)
        scalledPixmap = pixmap.scaled(512, 512, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imageLabel.setPixmap(scalledPixmap)
        return imageLabel
    
    def loadChoices(self):
        # Dynamically alternates between Like and Dislike and changes values in like value
        def likePhotoController():
            if likeButton.text() == 'Like':
                cursor.execute("INSERT INTO Likes VALUES(?,?)",(self.photoId,self.currentUserID))
                connect.commit()
                likeButton.setText("Dislike") 
            else:
                cursor.execute("DELETE FROM Likes WHERE pid = ? AND uid = ?",(self.photoId,self.currentUserID))
                connect.commit()
                likeButton.setText("Like")
            likeCount = cursor.execute("SELECT Count(pid) FROM Likes WHERE pid = ?",(self.photoId,)).fetchone()
            likeLabel.setText(f"Likes: {likeCount[0]}")
        # Dynamically alternates between Adding new comment or deleting existing comment
        def newCommentController(text):
            if newCommentButton.text() == 'Add Comment':
                text, ok = QInputDialog.getText(self,"New Comment","Insert Comment:")
                if ok:
                    from datetime import date
                    todayDate = date.today()
                    formatedDate = str(todayDate.month) + "/" + str(todayDate.day) + "/" + str(todayDate.year)
                    cursor.execute("INSERT INTO Comments(pid,uid,comment,date) VALUES(?,?,?,?)",(self.photoId,self.currentUserID,text,formatedDate))
                    connect.commit()
                    newCommentButton.setText("Delete Comment")
                    self.reloadComments()
            else:
                cursor.execute("DELETE FROM Comments WHERE pid = ? AND uid = ?",(self.photoId,self.currentUserID))
                connect.commit()
                newCommentButton.setText("Add Comment")
                self.reloadComments()

        choiceWidget = QWidget(objectName = 'choiceWidget')
        choiceWidget.setStyleSheet("#choiceWidget{border: 1px solid grey;}")
        hBoxLayout = QHBoxLayout()
        # Show Likes
        likeLabel = QLabel()
        likeCount = cursor.execute("SELECT Count(pid) FROM Likes WHERE pid = ?",(self.photoId,)).fetchone()
        likeLabel.setText(f"Likes: {likeCount[0]}")
        hBoxLayout.addWidget(likeLabel,10)

        # Create Like Button
        likeButton = QPushButton()
        likeButton.clicked.connect(likePhotoController)
        likeResults = cursor.execute("SELECT * FROM Likes WHERE pid = ? AND uid = ?",(self.photoId,self.currentUserID)).fetchone()
        if likeResults is None: 
            likeButton.setText("Like")  
        else:
            likeButton.setText("Dislike") 
        hBoxLayout.addWidget(likeButton,45)

        # Create NewComment Button
        newCommentButton = QPushButton()
        newCommentButton.clicked.connect(newCommentController)
        commentResults = cursor.execute("SELECT * FROM Comments WHERE pid = ? AND uid = ?",(self.photoId,self.currentUserID)).fetchone()
        if commentResults is None: 
            newCommentButton.setText("Add Comment")
        else:
            newCommentButton.setText("Delete Comment")

        hBoxLayout.addWidget(newCommentButton,45)

        choiceWidget.setLayout(hBoxLayout)
        return choiceWidget

    def loadTags(self): 
        tagWidget = QWidget(objectName = 'tagWidget')
        gridLayout = QGridLayout()
        gridLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tagWidget.setStyleSheet("#tagWidget{border: 1px solid grey;}")

        columnAmount = 6
        gridLayout.addItem(QSpacerItem(0,0),0,columnAmount-1) #sets max columns by placing empty item at max column

        tagTuples = cursor.execute("SELECT tag FROM Tags WHERE pid=?;",(self.photoId,)).fetchall() 

        for tagTuple in tagTuples:
            newTagButton = TagButton(tagTuple)
            gridLayout.addWidget(newTagButton)
            self.tags.append(newTagButton)

        tagWidget.setLayout(gridLayout)
        return tagWidget

    def loadComments(self):
        commentWidget = QWidget(objectName='commentWidget')
        vBoxLayout = QVBoxLayout()
        commentWidget.setStyleSheet("#commentWidget{border: 1px solid grey;}")
        vBoxLayout.setSpacing(0)
        
        commentTuples = cursor.execute("SELECT * FROM Comments WHERE pid=?",(self.photoId,)).fetchall() 
        for commentTuple in commentTuples:
            newCommentWidget = SingleCommentWidget(commentTuple)
            newCommentWidget.layout().setContentsMargins(0,0,0,0)
            vBoxLayout.addWidget(newCommentWidget)
        commentWidget.setLayout(vBoxLayout)
        return commentWidget
    
    def reloadComments(self):
        self.findChild(QWidget,"commentWidget").deleteLater()
        self.layout().addWidget(self.loadComments())

class TagButton(QPushButton):
    def __init__(self, tagTuple):
        super(TagButton,self).__init__(tagTuple[0])
        self.tag = tagTuple[0]
        self.clicked.connect(self.displayTagPhotos) # temp

    def displayTagPhotos(self): #need to implement
        main_window = QCoreApplication.instance().main_window
        main_window.show_photos_with_tag(self.tag)

class SingleCommentWidget(QWidget):
    def __init__(self, commentTuple):
        super(SingleCommentWidget,self).__init__()
        self.cid = commentTuple[0]
        self.pid = commentTuple[1]
        self.uid = commentTuple[2]
        self.comment = commentTuple[3]
        self.date = commentTuple[4]
        self.createComment()

    def createComment(self):
        self.setObjectName("CommentWidget")
        vBoxLayout = QVBoxLayout()
        
        headerWidget = QWidget()
        headerHBoxLayout = QHBoxLayout()

        headerHBoxLayout.setContentsMargins(0,0,0,0)

        headerWidget.setStyleSheet("""border: 1px solid; 
                            border-top-color: light gray; 
                            border-left-color: light gray;
                            border-right-color: light gray;""")

        nameTuple = cursor.execute("SELECT fname,lname FROM Users WHERE uid=?;",(self.uid,)).fetchone() 
        nameLabel = QLabel(nameTuple[0]+" "+nameTuple[1])
        dateLabel = QLabel(self.date)
        commentLabel = QLabel(self.comment)

        headerHBoxLayout.addWidget(nameLabel)
        headerHBoxLayout.addWidget(dateLabel,alignment = Qt.AlignmentFlag.AlignRight)
        headerWidget.setLayout(headerHBoxLayout)
        vBoxLayout.addWidget(headerWidget)
        vBoxLayout.addWidget(commentLabel)

        self.setLayout(vBoxLayout)
