# using sqlalchemy to create database
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#users of the database
class user(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String , unique =True , nullable = False)
    password = db.Column(db.String , nullable = False)
    uname = db.Column(db.String , nullable = False)
    qualification = db.Column(db.String , nullable = False)
    dob = db.Column(db.Date , nullable=False)
# one to many with scores
    scores = db.relationship("scores" , backref = "user")

#already added quiz master
class admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer , primary_key = True)
    adminname = db.Column(db.String , unique =True , nullable = False)
    password = db.Column(db.String , nullable = False)

#subjects in dataabase
class subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String , unique =True , nullable = False)
    description = db.Column(db.String , nullable = False)

    #relation if relation in subject with chapter it means one to many relationship
    chapters = db.relationship("chapter" , backref="subject" ,cascade="all, delete-orphan")


#chapter of a subject 
class chapter(db.Model):
    __tablename__ = "chapter"
    id = db.Column(db.Integer , primary_key = True)
    subject_id = db.Column(db.ForeignKey("subject.id" , ondelete = "CASCADE") , nullable = False )
    name = db.Column(db.String , unique =True , nullable = False)
    description = db.Column(db.String , nullable = False)
# one to many relationship with quiz
    quizzes = db.relationship("quiz" , backref= "chapter" , cascade="all, delete")


#class quiz 
class quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String , unique = True)
    chapter_id = db.Column( db.ForeignKey("chapter.id" , ondelete = "CASCADE" ) , nullable = False)
    doq = db.Column(db.Date , nullable = False)
    time = db.Column(db.Time , nullable = False) #(hh:mm)
    remarks = db.Column(db.String , nullable = True)
# one to many relationship with question
    questions = db.relationship('questions' , backref = 'quiz' , cascade="all, delete-orphan")
    score = db.relationship('scores' , backref = "quiz" , cascade="all, delete-orphan")

class questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer , primary_key = True)
    quiz_id = db.Column( db.ForeignKey("quiz.id" , ondelete = "CASCADE" ) , nullable=False)
    question = db.Column(db.String , nullable = False) # make question title and add on dashboard
    option1 = db.Column(db.String , nullable = False)
    option2 = db.Column(db.String , nullable = False)
    option3 = db.Column(db.String , nullable = False)
    option4 = db.Column(db.String , nullable = False)
    answer = db.Column(db.String , nullable = False)
    marks = db.Column(db.Integer , nullable = False)

class scores(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer , primary_key = True)

    quiz_id = db.Column( db.ForeignKey("quiz.id" , ondelete = "CASCADE") , nullable=False)
    user_id = db.Column( db.ForeignKey("user.id" , ondelete = "CASCADE") , nullable = False)
    time_attempt = db.Column(db.Date)
    totalscore = db.Column(db.Integer)
# one to many relationship with quiz which means one quiz can have many scores

