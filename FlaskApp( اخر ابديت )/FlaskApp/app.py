from flask import Flask , render_template , request , jsonify
import numpy as np 
import pickle 
import math 
from keras.models import model_from_json





# hena 5at object mn flask o basht8l 3leeh 
my_app = Flask(__name__)



# # Escaping backslashes
# with open('C:\\Users\\m3394\\Downloads\\FlaskApp\\CGAN\\.vscode\\settings.json', 'r') as json_file:
#     loaded_model_json = json_file.read()


# # Load model
# loaded_model = model_from_json(loaded_model_json)

# # Load model weights
# loaded_model.load_weights('C:\\Users\\m3394\\Downloads\\FlaskApp\\CGAN\\gen_150.h5')

# # Compile the model (if necessary)
# loaded_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])




@my_app.route('/')
def homePage():
    return render_template("homePage.html", pagetitle="homepage")

@my_app.route("/masterPage")
def masterPage():
    return render_template("masterPage.html", pagetitle = "masterPage" , custom_css="style.css")


@my_app.route("/masterPage/sketchPage")
def sketchPage():
    
    return render_template("sketchPage.html", pagetitle = "sketchPage" , custom_css="style.css")

@my_app.route("/masterPage/uploadPage")
def uploadPage():
    return render_template("uploadPage.html", pagetitle = "uploadPage" )



if __name__ =="__main__":
    my_app.run(debug=True,host='0.0.0.0',port=9999)










# ----------------------------------------------------------------------


# @my_app.route("/formtest",methods=['POST','GET'])
# def formm_test():
#     if request.method=='POST':
#         return 'username : %s'%(request.form['username'])
#     else:
#         return''' <form action="/formtest"method="post">
#         Name: <input name="username" type = "text" /> <br/>
#         <input value ="Send" type = "submit"/>
#         </form> '''
   


# # de asmha dicorator
# @my_app.route("/")
# @my_app.route("/greet")
# @my_app.route("/greet/<name>")
# def hello(name=None):
#     return render_template("homePage.html", pagetitle = "homePage",name=name)


# # take variable ( String ) called username and print username
# @my_app.route("/user/<userName>")
# def showUsername(username):
#     return 'User %s' %userName


# take variable Int(digit) called id and print id
# @my_app.route("/idd/<int:id>")
# def showId(id):
#     return "mohamed is is %d"%id

# ----------------------------------------------------------------------




# WEBZERO CODE
# --------------------------------------------------------------------------------------

# @my_app.route('/')
# def homePage():
#     return render_template("homePage.html", pagetitle="homepage")

# @my_app.route("/masterPage")
# def masterPage():
#     return render_template("masterPage.html", pagetitle = "masterPage" , custom_css="style.css")


# @my_app.route("/masterPage/sketchPage")
# def sketchPage():
    
#     return render_template("sketchPage.html", pagetitle = "sketchPage" , custom_css="style.css")

# @my_app.route("/masterPage/uploadPage")
# def uploadPage():
#     return render_template("uploadPage.html", pagetitle = "uploadPage" )



# if __name__ =="__main__":
#     my_app.run(port=9000)




# ------------------------------------------------------------------------------










# # hena 5at object mn flask o basht8l 3leeh 
# my_app = Flask(__name__)
# @my_app.route('/')
# def homePage():
#     return "hello  at HomePage"


# ####################################################


# @my_app.route('/<name>')
# def homePageWithName(name):
#     return "hello %s  at HomePage"%name

# # #####################################################
# @my_app.route("/formtest",methods=['POST','GET'])
# def formm_test():
#     if request.method=='POST':
#         return 'username is : %s'%(request.form['username'])
#     else:
#         return render_template("check.html")


# # #############################################################

# @my_app.route('/html/<name>')
# def pageFromHtml(name=None):
#     return render_template('hello.html',name=name)

