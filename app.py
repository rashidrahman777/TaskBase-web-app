from flask import Flask, render_template, redirect, url_for, request, session, escape
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_mail import Mail, Message

app = Flask(__name__)

app.secret_key = os.urandom(24)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rahmanrashid391@gmail.com'
app.config['MAIL_PASSWORD'] = '******'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#config database  
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Users.db"
app.config['SQLALCHEMY_BINDS'] =  {'Taskbase' : "sqlite:///TaskBase.db"}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TaskBase(db.Model):
    __bind_key__ = 'Taskbase'
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    Task = db.Column(db.String(500), nullable=False)
    deadline = db.Column(db.String(20), nullable=False)
    Date_created = db.Column(db.DateTime, nullable=True, default=datetime.now().replace(microsecond=0))              #  or datetime.utcnow --> for GMT means global audiance
    Status = db.Column(db.String(20), nullable=False)

    # def __repr__(self) -> str:
    #     return f"{self.name} - {self.Task} - {self.deadline}"

class Users(db.Model):                                  # main uri database
    # __bind_key__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    passwords = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return '<User %r %r>' % (self.username, self.passwords)

# @app.before_request
# def before_request():
#     g.user = None

#     if 'user' in  session:
#         g.user = session['user']

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("Uusername")
        passwords = request.form.get("Upassword")
        session["user_s"] = username

        pwCheck = Users.query.filter_by(username=username.lower()).first()
    # #    pwCheckg = User.query.filter_by(username='guest').first()

    # #    lusers = Users(username=username, passwords=passwords)
    # #    db.session.add(lusers)
    # #    db.session.commit()

    # #    if (pwCheck.email == passwords and username == 'admin') or (pwCheckg.email == passwords and username == 'guest'):
        if pwCheck.passwords == passwords:  	                #  and pwCheck.username == username --> not working
            allTaskBase = TaskBase.query.all()
            return render_template("home.html",allTaskBase=allTaskBase)
        else:
            return render_template("login.html", logintry="Login Failure")
    else:
        if "user_s" in session:
            return redirect(url_for('home'))
        return render_template("login.html")  

    # #    session.pop('user', None)

    #     if (request.form['Upassword'] == '1234'  and request.form["Uusername"] == 'admin') or (request.form['Upassword'] == '2345'  and request.form["Uusername"] == 'guest1') or (request.form['Upassword'] == '3456'  and request.form["Uusername"] == 'guest2'):
    #         session['user'] = request.form['Uusername']
    #         return redirect(url_for('home'))

    # return render_template('login.html')


@app.route("/home", methods=['GET','POST'])
def home():
    # if g.user:
    if "user_s" in session:
        allTaskBase = TaskBase.query.all()
        return render_template("home.html", allTaskBase=allTaskBase)
        # return render_template('home.html', user=session['user'])
    else:
        return redirect(url_for('login'))                           # redirect or  render_template
        # return render_template('login.html')

    

@app.route("/Admin", methods=['GET','POST'])
def Admin():
    # if g.user:
    if "user_s" in session and session["user_s"] == "rashid":                                                    # fixing left (for only admin allow) --> fixed
        if request.method == 'POST':
            name = request.form['Ename']
            Task = request.form['Etask']
            deadline = request.form['datetime']
            Status = request.form['EStatus']
            taskbase = TaskBase(name=name.lower(), Task=Task, deadline=deadline, Status=Status)
            db.session.add(taskbase)
            db.session.commit()

            emailCheck = Users.query.filter_by(username=name.lower()).first()
            msg = Message('Task for '+ name , sender = 'rahmanrashid391@gmail.com', recipients = [emailCheck.email])
            msg.body = Task
            mail.send(msg)

            allTaskBase = TaskBase.query.all()
            return render_template("home.html", allTaskBase=allTaskBase)
        allTaskBase = TaskBase.query.all()
        return render_template("Admin.html", allTaskBase=allTaskBase)
    else:
        return redirect(url_for('login')) 

        # return redirect(url_for('login'))                               # redirect or  render_template
        # # return render_template('login.html')


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user_s', None)
   return redirect(url_for('login'))


@app.route('/delete/<int:sno>')
def delete(sno):
    if session["user_s"] == "rashid":
        taskbase = TaskBase.query.filter_by(sno=sno).first()
        db.session.delete(taskbase)
        db.session.commit()
        # return redirect("/home")
        allTaskBase = TaskBase.query.all()
        return render_template("home.html", allTaskBase=allTaskBase)
    allTaskBase = TaskBase.query.all()
    return render_template("home.html", allTaskBase=allTaskBase)


@app.route('/update/<string:name>')
def update(name):
    # u_ser = TaskBase.query.filter_by(sno=sno)
    if name.lower() == session["user_s"]:
        taskbase = TaskBase.query.filter_by(name=name).update(dict(Status='Completed'))
        db.session.commit()
        return redirect(url_for("home"))
    return redirect(url_for("home"))


# # experiment with flask mail (send_mail and mail.html )     --> finally added with admin route
# @app.route("/send_mail", methods=['GET','POST'])
# def send_mail():
#     if "user_s" in session and session["user_s"] == "rashid":
#         if request.method == 'POST':
#             name = request.form.get('Ename')
#             message = request.form.get('Etask')
            
#             emailCheck = Users.query.filter_by(username=name.lower()).first()
#             msg = Message('Task for '+ name , sender = 'rahmanrashid391@gmail.com', recipients = [emailCheck.email])
#             msg.body = message
#             mail.send(msg)

#         return render_template("mail.html")
#     return redirect(url_for('login'))
# # end of experiment    


if __name__ == "__main__":
    app.run(debug=True, port=8000)
