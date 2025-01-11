# To run flask and render HTML and url finder
from flask import Flask , render_template , redirect , url_for 
# To find method of request 
from flask import request
from datetime import datetime
from models import db , user , admin , subject , chapter ,scores , quiz , questions 

app = Flask(__name__ )

#path to database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'

# To link the database with app
db.init_app(app)

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
                return render_template("user_dashboard")
        # failed is user to write a error message for try again
        return render_template("index.html" , failed = True)
    return render_template("index.html" , failed = False)

# registration page for users 
@app.route("/registration" , methods = ["GET","POST"])
def registration():
    if request.method == "POST":
        email = request.form['username']
        name = request.form['fullname']
        passwo = request.form["password"]
        qual = request.form["qualification"]
        date_str = request.form["dob"]
        dat = datetime.strptime(date_str,"%Y-%m-%d").date()

        users = user.query.all()
        for use in users :
            if use.username == email:
                return render_template("registration.html" , already=True)
        db.session.add(user(username=email , password = passwo , uname=name , qualification = qual , dob = dat))
        db.session.commit()
        # if registered then redirect them to login page 
        return redirect("/")

    return render_template("registration.html" , already=False)

@app.route('/subject/add' , methods= ["GET" , "POST"])
def subjectadd():
    if request.method == "POST":
        subname = request.form["subname"]
        desc = request.form["desc"]
        subs = subject.query.all()
        for sub in subs:
            if sub.name == subname:
                return render_template("addsub.html" , again = True)
        db.session.add(subject(name = subname , description = desc))
        db.session.commit()
        return redirect("/admin/dash")  # add successful meassage 
    return render_template("addsub.html" , again= False )

@app.route("/chapter/add/<int:sub_id>" , methods = ["GET" , "POST"])
def chapteradd(sub_id):
    if request.method == "POST":
        name = request.form["chname"]
        desc = request.form["description"]
        chs = chapter.query.filter(chapter.subject_id == sub_id ).all()
        for ch in chs :
            if ch.name == name:
                return render_template("addch.html" , again = True)
        db.session.add(chapter(subject_id = sub_id , name = name , description = desc ))
        db.session.commit()
        return redirect("/admin/dash")  # add successful meassage 
    return render_template("addch.html" , again= False )    

@app.route("/admin/dash" , methods = ["GET"])
def admindash():
    return render_template("admin_dashboard.html" ,  sub = subject.query.all() , ch = chapter.query.all() , ques = questions.query.all() , qui = quiz.query.all() )

@app.route("/admin/quiz" , methods = ["GET" ])
def adminquiz():
    return render_template("admin_quiz_dash.html" , ch = chapter.query.all() , quiz= quiz.query.all() , ques = questions.query.all())

@app.route("/add/question/<int:qui_id>" , methods=["GET" , "POST"])
def addquestion(qui_id):
    if request.method == "POST":
        quest = request.form["question"]
        o1 = request.form["o1"]
        o2 = request.form["o2"]
        o3 = request.form["o3"]
        o4 = request.form["o4"]
        ans = request.form["ans"]

        db.session.add(questions(quiz_id = qui_id , question = quest , option1 = o1 , option2 = o2, option3 = o3, option4 = o4 , answer = ans))
        db.session.commit()
        return redirect("/admin/quiz")
    return render_template("addquestion.html")

@app.route("/quiz/add" , methods = ["GET" , "POST"])
def addquiz():
    if request.method == "POST":
        ch_id = request.form["chid"]
        date_str = request.form["date"]
        dat = datetime.strptime(date_str ,"%Y-%m-%d" ).date()
        ti = request.form["time"]
        tim = datetime.strptime(ti , "%H:%M" ).time()
        rem = request.form["rem"] # i dont know the use of date and time will update later

        db.session.add(quiz(chapter_id = ch_id , doq = dat , time = tim , remarks = rem))
        db.session.commit()
        return redirect("/admin/quiz")
    return render_template("addquiz.html")

@app.route("/del/ch/<int:ch_id>" ,methods = ["POST" , "GET"])
def delch(ch_id):
    ch_to_del = chapter.query.get(ch_id)
    db.session.delete(ch_to_del)
    db.session.commit()

    return redirect("/admin/dash")

@app.route("/edit/ch/<int:ch_id>" , methods=["GET" , "POST"])
def editch(ch_id):
    ch_to_edit = chapter.query.get(ch_id)
    if request.method == "POST":
        new_name = request.form["name"]
        new_desc = request.form["desc"]

        ch_to_edit.name = new_name
        ch_to_edit.description = new_desc

        db.session.commit()
        
        return redirect("/admin/dash")
    return render_template("editch.html" , name=ch_to_edit.name , desc = ch_to_edit.description)


if __name__ == "__main__":
    app.run(debug=True)

