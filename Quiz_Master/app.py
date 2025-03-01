# To run flask and render HTML and url finder
from flask import Flask , render_template , redirect , request
from datetime import datetime,date
from models import db , user , admin , subject , chapter ,scores , quiz , questions 
from sqlalchemy import desc
import requests
from api import api

app = Flask(__name__, instance_relative_config=True)

#path to database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'


# To link the database with app
db.init_app(app)
api.init_app(app) 

# To create the table in db if they did not exist earlier 
with app.app_context():
    db.create_all()

#home page to login as a admin or user 
@app.route("/" , methods = ["GET" , "POST"])
def home():
    if request.method == "POST":
        admins = admin.query.all()
        for admi in admins:
            if request.form["username"] == admi.adminname and request.form["password"] == admi.password:
                return redirect("/admin/dash")
        users = user.query.all()
        for use in users:
            if request.form["username"] == use.username and request.form["password"] == use.password:
                return redirect(f"/user/dashboard/{use.id}")
        # failed is user to write a error message for try again
        return render_template("index.html" , failed = True)
    return render_template("index.html" , failed = False)

# registration page for users 
@app.route("/registration" , methods = ["GET","POST"])
def registration():
    if request.method == "POST":
        email = request.form['username']                            #this is user email
        name = request.form['fullname']                             #this is user name
        passwo = request.form["password"]                           #this is user password
        qual = request.form["qualification"]                        #this is user qualification
        date_str = request.form["dob"] 

        field = {
            "email":email,
            "name" : name ,
            "passwo":passwo,                                        #there are fields for api to create user
            "qual":qual,
            "dat":date_str
        }
        url = 'http://127.0.0.1:5000/api/registration'              #this is url for api
        response = requests.post(url , json= field)
        # if registered then redirect them to login page 
        if  response.status_code == 200:
            return redirect("/")
        elif  response.status_code == 409:
            return render_template("registration.html" , already=True)
    return render_template("registration.html" , already=False)

#to add subject 
@app.route('/subject/add' , methods= ["GET" , "POST"])
def subjectadd():
    if request.method == "POST":
        subname = request.form["subname"]                           #this is subject name 
        desc = request.form["desc"]                                 #this is discription of subject
        subs = subject.query.all()
        for sub in subs:
            if sub.name == subname:
                # it will raise an error if subject with same name already exists
                return render_template("addsub.html" , again = True)
        db.session.add(subject(name = subname , description = desc))
        db.session.commit()
        return redirect("/admin/dash")  # add successful meassage 
    return render_template("addsub.html" , again= False )

#to add chapter
@app.route("/chapter/add/<int:sub_id>" , methods = ["GET" , "POST"])
def chapteradd(sub_id):
    if request.method == "POST":
        name = request.form["chname"]                               #chapter name
        desc = request.form["description"]                          #chapter description
        chs = chapter.query.filter(chapter.subject_id == sub_id ).all()
        for ch in chs :
            if ch.name == name:
                #it will raise an error if chapter with same name already exists
                return render_template("addch.html" , again = True)
        db.session.add(chapter(subject_id = sub_id , name = name , description = desc ))
        db.session.commit()
        return redirect("/admin/dash")  
    return render_template("addch.html" , again= False )    

#this is admin dashboard
@app.route("/admin/dash" , methods = ["GET"])
def admindash():
    return render_template("admin_dashboard.html" ,  sub = subject.query.all() , ch = chapter.query.all() , ques = questions.query.all() , qui = quiz.query.all() )

#this is quiz page for admin
@app.route("/admin/quiz" , methods = ["GET" ])
def adminquiz():
    return render_template("admin_quiz_dash.html" , ch = chapter.query.all() , quiz= quiz.query.all() , ques = questions.query.all())

#to add question
@app.route("/add/question/<int:qui_id>" , methods=["GET" , "POST"])
def addquestion(qui_id):
    if request.method == "POST":
        quest = request.form["question"]                            #this is question statement
        o1 = request.form["o1"]                                     #this is option1
        o2 = request.form["o2"]                                     #this is option2
        o3 = request.form["o3"]                                     #this is option3
        o4 = request.form["o4"]                                     #this is option4
        ans = request.form["ans"]                                   #this is answer
        mark = request.form["mark"]                                 #this is marks for question
        db.session.add(questions(quiz_id = qui_id , marks = mark , question = quest , option1 = o1 , option2 = o2, option3 = o3, option4 = o4 , answer = ans))
        db.session.commit()
        return redirect("/admin/quiz")
    
    return render_template("addquestion.html")

#to add quiz
@app.route("/quiz/add" , methods = ["GET" , "POST"])
def addquiz():
    if request.method == "POST":
        name = request.form["name"]                                 #quiz name
        ch_id = request.form["chid"]                                #chapter id   
        date_str = request.form["date"]                             #date 
        dat = datetime.strptime(date_str ,"%Y-%m-%d" ).date()       #this is converting date str into datetime object
        ti = request.form["time"]                                   #time
        tim = datetime.strptime(ti , "%H:%M" ).time()               #this is converting time str into datetime object
        rem = request.form["rem"]                                   #remark

        db.session.add(quiz( name = name , chapter_id = ch_id , doq = dat , time = tim , remarks = rem))
        db.session.commit()
        return redirect("/admin/quiz")
    
    return render_template("addquiz.html" ,  datetime = date.today() )

#to delete ch 
@app.route("/del/ch/<int:ch_id>" ,methods = ["POST" , "GET"])
def delch(ch_id):
    ch_to_del = chapter.query.get(ch_id)                            #chapter to delete
    db.session.delete(ch_to_del)
    db.session.commit()

    return redirect("/admin/dash")

#to edit ch
@app.route("/edit/ch/<int:ch_id>" , methods=["GET" , "POST"])
def editch(ch_id):
    ch_to_edit = chapter.query.get(ch_id)                          #chapter to edit
    if request.method == "POST":
        new_name = request.form["name"]                            #new name
        new_desc = request.form["desc"]                            #new description
        ch_to_edit.name = new_name
        ch_to_edit.description = new_desc
        db.session.commit()
        return redirect("/admin/dash")
    
    return render_template("editch.html" , name=ch_to_edit.name , desc = ch_to_edit.description)

#to delete subject
@app.route("/admin/del/<int:sub_id>" , methods = ["GET" , "POST"])
def delsub(sub_id):
    sub_to_del = subject.query.get(sub_id)                         #subject to delete
    db.session.delete(sub_to_del)
    db.session.commit()
    return redirect("/admin/dash")

#to delete quiz
@app.route("/admin/del/quiz/<int:quiz_id>" , methods = ["GET","POST"])
def delquiz(quiz_id):
    quiz_to_del = quiz.query.get(quiz_id)                          #quiz to delete
    db.session.delete(quiz_to_del)
    db.session.commit()
    return redirect("/admin/quiz")

#to delete question
@app.route("/admin/delques/<int:qu_id>" , methods=["GET","POST"])
def delques(qu_id):
    question_to_del = questions.query.get(qu_id)                   #question to delete
    db.session.delete(question_to_del)
    db.session.commit()
    return redirect("/admin/quiz")

#to edit question 
@app.route("/admin/editques/<int:qu_id>" , methods = ["GET" , "POST"])
def editques(qu_id):
    q_t_e = questions.query.get(qu_id)                             #question to edit
    if request.method == "POST":
        quest = request.form["question"]                           #question
        o1 = request.form["o1"]                                    #option1
        o2 = request.form["o2"]                                    #option2
        o3 = request.form["o3"]                                    #option3
        o4 = request.form["o4"]                                    #option4
        ans = request.form["ans"]                                  #answer
        mark = request.form["mark"]                                #marks
        
        q_t_e.question = quest
        q_t_e.option1 = o1
        q_t_e.option2 = o2
        q_t_e.option3 = o3
        q_t_e.option4 = o4
        q_t_e.answer = ans
        q_t_e.marks = mark

        db.session.commit()
        return redirect("/admin/quiz")
    return render_template("editques.html" , oldquestion = q_t_e.question , oldmark = q_t_e.marks , oldo1 = q_t_e.option1,oldo2 = q_t_e.option2,oldo3 = q_t_e.option3,oldo4 = q_t_e.option4 , oldans = q_t_e.answer)

#to edit subjects
@app.route("/admin/editsub/<int:s_id>" , methods=["GET","POST"])
def editsub(s_id):
    ste = subject.query.get(s_id)                                  #subject to edit
    if request.method == "POST":
        name = request.form["name"]                                #subject name
        desc = request.form["desc"]                                #subject description

        ste.name = name
        ste.description = desc
        db.session.commit()
        return redirect("/admin/dash")

    return render_template("editsub.html" , oldname = ste.name , olddesc = ste.description)  

#search tag in admin 
@app.route("/admin/search" , methods=["GET" , "POST"])
def adminsearch(): 
    search = request.form['name']                                  #obejct to search
    sub = subject.query.filter_by(name = search).first()           #subjects
    qui = quiz.query.filter_by(name = search).first()              #quizzes
    usr = user.query.filter_by(username = search).first()          #users

    if sub != None:
        return render_template("search.html" , found = "subject" , name = sub.name , desc = sub.description)
    elif qui != None:
        return render_template("search.html" , found = "quiz" ,name =qui.name , ch_id = qui.chapter_id , date = qui.doq , duration = qui.time , remark = qui.remarks)
    elif usr != None:
        return render_template("search.html" , found="user" , usrname =usr.username ,fullname =usr.uname , quali = usr.qualification , dob = usr.dob.strftime('%d-%m-%Y')  )
    
    return render_template("search.html" , found=None)
    
#to edit quiz
@app.route("/admin/editquiz/<int:q_id>" , methods=["GET","POST"])
def quizedit(q_id):
    qte = quiz.query.get(q_id)                                      #quiz to edit
    durat = qte.time                                                #duration of quiz
    durat =  durat.strftime("%H:%M")                                #to change format of time
    if request.method == "POST":
        name = request.form["name"]                                 #quiz name
        ch_id = request.form["chid"]                                #chapter id
        date_str = request.form["date"]                             #date in string 
        remark = request.form["rem"]                                #quiz remark
        ti = request.form["time"]                                   #time duration for quiz 
        tim = datetime.strptime(ti, "%H:%M").time()                 
        dat = datetime.strptime(date_str ,"%Y-%m-%d" ).date()       #changing format of time 
        qte.name = name
        qte.chapter_id = ch_id
        qte.doq = dat
        qte.time = tim
        qte.remarks = remark

        db.session.commit()
        return redirect("/admin/quiz")
    return render_template("editquiz.html" , name = qte.name , ch_id = qte.chapter_id , date =qte.doq , duration= durat , remark = qte.remarks )
    
#to show admin summary chart
@app.route("/admin/summarychart" , methods=["GET"])
def adminchart():
    subjects  = subject.query.all()                                #subjects
    data = {}                                                      #data contain  subjects ===>  max score
    data2 = {}                                                     #data2 contain subjects ===>  number of attempts
    for sub in subjects:
        data2[sub] = 0
        chap = chapter.query.filter_by(subject_id = sub.id).all()
        max_score = 0
        for ch in chap:
            qui = quiz.query.filter_by(chapter_id = ch.id).all()
            for q in qui :
                data2[sub] += scores.query.filter_by(quiz_id = q.id).count()
                score = scores.query.filter_by(quiz_id = q.id).order_by(desc(scores.totalscore)).first()
                if score.totalscore > max_score:
                    max_score = score.totalscore
        data[sub.name] = max_score 
    subs = data.keys()
    vals = data.values()
    return render_template("adminsummary.html" , subs = list(subs) , vals = list(vals) , attempts = list(data2.values()))



                                                    # start of user side routes 


#user dashboard 
@app.route("/user/dashboard/<int:user_id>" , methods = ["GET"])
def userdash(user_id):
    current_user = user.query.get(user_id)                        #current user
    quizzes = quiz.query.all()                                    #all quizzes
    quests = questions.query.all()                                #all questions
    return render_template("userdash.html" , name = current_user.uname , quizzes = quizzes , quests = quests , user_id = current_user.id)

#to show details of quiz
@app.route("/quiz/view/<int:quiz_id>/<int:user_id>" , methods=["GET"])
def quizview(quiz_id , user_id ):
    qui = quiz.query.get(quiz_id)                                 #quiz
    chap = chapter.query.get(qui.chapter_id)                      #chapter
    sub = subject.query.get(chap.subject_id)                      #subject
    quests = questions.query.all()                                #question
    return render_template("viewquiz.html" , qui = qui , chap = chap , sub = sub , quests = quests , user_id = user_id)

#to show users past scores and attempts
@app.route("/scores/<int:user_id>" , methods=["GET"])
def scoresdetails(user_id):
    current_user = user.query.get(user_id)                         #current user
    scoresdata = scores.query.filter_by(user_id = current_user.id).all() #scores data of user
    quizs = quiz.query.all()                                       #quizzes
    quest = questions.query.all()                                  #questions
    return render_template("scoresdetails.html" , current_user=current_user , scoresdata = scoresdata , quest=quest , quizs=quizs )

#to show user summary page 
@app.route("/user/summary/<int:user_id>" , methods=["GET"])
def usersummary(user_id):
    current_user = user.query.get(user_id)
    attempts = scores.query.filter_by(user_id = user_id).all()     #scores 
    data = {}                                                      #data contains  subjects ===> number of quiz attempted
    data2 = {}                                                     #data2 contains month(in integer eg: jan is 1 )===> number of quiz attempted in that month
    for attempt in attempts:
        date_of_attempt = str(attempt.time_attempt)
        month = date_of_attempt.split("-")[1]
        if month in data2:
            data2[month] += 1
        else:
            data2[month] = 1
        qu = quiz.query.get(attempt.quiz_id)
        chap = chapter.query.get(qu.chapter_id)
        sub = subject.query.get(chap.subject_id)
        if sub.name in data:
            data[sub.name] += 1
        else :
            data[sub.name] = 1
    subs = data.keys()                                             
    attempts = data.values()                                       
    months = data2.keys()
    counts = data2.values()
    return render_template("usersummary.html" , subj = list(subs) ,months = list(months), counts = list(counts) , attempt = list(attempts) , current_user = current_user )

# to start quiz 
@app.route("/startquiz/<int:user_id>/<int:quiz_id>" , methods=["GET" , "POST"])
def startquiz(user_id , quiz_id):
    if request.method == "GET":
        current_user = user.query.get(user_id)
        current_quiz = quiz.query.get(quiz_id)
        question = questions.query.filter_by(quiz_id=current_quiz.id).all()
        maximum = 0
        for quest in question:
            maximum+= quest.marks
        time = str(current_quiz.time)
        time = time.split(":")
        insec = int(time[0])*3600 + int(time[1])*60 + int(time[2])
        return render_template("startquiz.html" , questions = list(question) , current_user = current_user , maxi = maximum , time = insec)
    mark = request.form["totalmarks"]
    max_mark = request.form["maxmarks"]
    new_score = scores(user_id = user_id , quiz_id = quiz_id , totalscore = mark , time_attempt=date.today())
    db.session.add(new_score)
    db.session.commit()
    return render_template("summaryquiz.html" , mark= mark , max_mark=max_mark , user_id = user_id )

# search 
@app.route("/user/search/<int:user_id>" , methods=["GET","POST"])
def searchuser(user_id):
    current_user = user.query.get(user_id)
    search = request.form["search"]
    search_by_score = scores.query.filter_by(user_id = user_id , totalscore = search).all()
    search_by_date = scores.query.filter_by(user_id = user_id , time_attempt = search).all()
    quizzes = quiz.query.all()
    if search_by_score != []:
        return render_template("searchresult.html" , current_user = current_user , result_by = "scores" , result = search_by_score , quizzes=quizzes)
    elif search_by_date != []:
        return render_template("searchresult.html" , current_user = current_user , result_by = "date" , result = search_by_date , quizzes= quizzes)
    else:
        return render_template("searchresult.html" , result_by = "nothing" , current_user = current_user)

if __name__ == "__main__":
    app.run(debug=True)

