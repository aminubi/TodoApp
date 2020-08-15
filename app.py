from flask import Flask,redirect,url_for,render_template,request
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_login import login_user,logout_user,current_user,UserMixin,LoginManager,login_required
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__)
app.config['SECRET_KEY']= 'thisiskey'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#Position all of this after the db and app have been initialised
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=88)])
class RegForm(FlaskForm):
     username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
     password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=88)])


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    schedule = db.Column(db.String(500))
    complete = db.Column(db.Boolean)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(88), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return "<h1>Welcome to Todo-App</h1>" 

@app.route('/process', methods=['POST'])
def process():
    form = LoginForm()
    #username = request.form.get("username")
    #password_id = request.form.get('password_id')
    username = form.username.data 
    password_id = form.password.data
    user = User.query.filter_by(username=username).first()
    db.session.commit()
    if username == user.username and check_password_hash(user.password, password_id):
        login_user(user)
        return redirect(url_for("home"))
    else:
        return redirect('login')

@app.route('/reghandle', methods=['POST'])
def reghandle():
    form =RegForm()
    password_id = form.password.data
    hashed_password =generate_password_hash(password_id, method='sha256')
    username = form.username.data 
    
    regform = User(username=username, password=hashed_password)
    db.session.add(regform)
    db.session.commit()
    return redirect('login')


@app.route('/home')
@login_required
def home():
    todo_list = Todo.query.all()
    #print(todo_list)
    return render_template('base.html', todo_list=todo_list, name=current_user.username)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/sign_up')
def sign_up():
   form = RegForm()
   return render_template('sign_up.html', form=form)

@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    schedule = request.form.get("schedule")
    new_todo = Todo(title=title, schedule=schedule, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))
    

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete 
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo) 
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('login'))


if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    db.create_all()
    #new_todo = Todo(title="todo 1", schedule="Jul/05/2020", complete=False)
    #db.session.add(new_todo)
    #db.session.commit() 

    app.run(port=5000,debug=True)