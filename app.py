from os.path import join, dirname
#from dotenv import load_dotenv
import os
import flask
import flask_sqlalchemy
import flask_socketio
import time
import requests

global_user_counter = 0

MESSAGES_RECEIVED_CHANNEL = "all messages received"

app = flask.Flask(__name__)
socketio = flask_socketio.SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

#dotenv_path = join(dirname(__file__), 'sql.env')
#load_dotenv(dotenv_path)

# DATABASE
#sql_user = os.environ['SQL_USER']
#sql_pwd = os.environ['SQL_PASSWORD']
# dbuser = os.environ['USER']

#database_uri = os.getenv("DATABASE_URL") # use this for heroku launch

#database_uri = "postgresql://{}:{}@localhost/postgres".format(sql_user,sql_pwd) # use this for local testing
#app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

db = flask_sqlalchemy.SQLAlchemy(app)
db.init_app(app)
db.app = app

class NewChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pfp = db.Column(db.String(150))
    username = db.Column(db.String(32))
    message = db.Column(db.String(1000))
    userType = db.Column(db.String(4))
    userVerified = db.Column(db.String(1))

    def __init__(self, p, u, m, t, v):
        self.pfp = p
        self.username = u
        self.message = m
        self.userType = t
        self.userVerified = v

db.create_all()
db.session.commit()

def emit_all_messages(channel):
    all_pfps = [db_chat.pfp for db_chat in db.session.query(NewChat).all()]
    all_users = [db_chat.username for db_chat in db.session.query(NewChat).all()]
    all_messages = [db_chat.message for db_chat in db.session.query(NewChat).all()]
    all_types = [db_chat.userType for db_chat in db.session.query(NewChat).all()]
    all_verified = [db_chat.userVerified for db_chat in db.session.query(NewChat).all()]

    socketio.emit(channel, {
        "all_pfps": all_pfps,
        "all_users": all_users,
        "all_messages": all_messages,
        "all_types": all_types,
        "all_verified": all_verified
    })


# GLOBAL 
def checkBotMessage(string):
    bot_string = string.split(" ")
    print("BOT STRING: " + string)
    if (bot_string[0] == "!!" and bot_string[1].lower() == "help"):
        poke_bot.help()
    elif (bot_string[0] == "!!" and bot_string[1].lower() == "about"):
        poke_bot.about()
    elif (bot_string[0] == "!!" and bot_string[1].lower() == "github"):
        poke_bot.github()
    elif (bot_string[0] == "!!" and bot_string[1].lower() == "pokedex" and bot_string[2]):
        poke_bot.pokeDex(bot_string[2])
    elif (bot_string[0] == "!!" and bot_string[1].lower() == "funtranslate" and bot_string[2]):
        print(" ".join(bot_string[2:]))
        poke_bot.funtranslate(" ".join(bot_string[2:]))
    elif (bot_string[0] == "!!" and bot_string[1].lower() not in commands):
        poke_bot.noCommandFound(bot_string[1])

def isImage(message):
        contentTypes = ["image/jpg", "image/jpeg", "image/gif", "image/png"]
        try:
            if(requests.head(message).status_code == 200):
                r = requests.head(message)
                print("ITS AN IMAGE")
                if r.headers["Content-Type"] in contentTypes:
                    poke_bot.postImage(message)
        except:
            pass

def checkurl(message):
    contentTypes = ["image/jpg", "image/jpeg", "image/gif", "image/png"]
    try:
        if(requests.head(message).status_code == 200):
            r = requests.head(message)
            print("ITS AN IMAGE")
            if r.headers["Content-Type"] in contentTypes:
                return True
    except:
        return False

class ChatBot:
    def __init__(self):
        self.bot_name = "Poke Bot"
        self.bot_pfp = "https://image.flaticon.com/icons/png/512/71/71339.png"

    def about(self):
        print("This is the about section!")

        bot_message = """Hello there!  I am Poke Bot.  Try typing '!! help' for a list of 
            commands! """
        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();
        
        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def github(self):
        print("This is the about section!")

        bot_message = """Checkout the source code at: https://github.com/NJIT-CS490/project2-br96"""
        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();
        
        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def help(self):
        print("This is the help section!")
        
        bot_message = """Try these commands:<br>!! help<br>!! github<br>!! about<br>!! pokedex <em>pokemon-name</em><br>!! funtranslate <em>message</em>"""

        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();

        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def noCommandFound(self, command):
        

        bot_message = "'!! {}' is not a command".format(command)

        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();

        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def funtranslate(self, text):
        url = "https://api.funtranslations.com/translate/yoda.json?text=" + text
        response = requests.get(url)
        print("STATUS CODE: " + str(response.status_code))
        if (response.status_code == 429):
            bot_message = "Too many calls.  Please limit to 5 per hour, per the api."
        else:
            data = response.json()
            bot_message = data["contents"]["translated"]

        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();

        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def pokeDex(self, pokemon):
        selected_pokemon = pokemon
        if (selected_pokemon == ""):
            selected_pokemon = "bulbasaur"

        pokedex = requests.get("https://pokeapi.co/api/v2/pokemon/{}".format(selected_pokemon.lower()))

        if (pokedex.status_code == 404):
            bot_message = """That's not a pokemon!  Try again!"""

            db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
            db.session.commit();

            emit_all_messages(MESSAGES_RECEIVED_CHANNEL)
        else:
            poke_name = pokedex.json()["name"].upper()
            poke_id = pokedex.json()["id"]


            bot_message = "{} is the {} pokemon.".format(poke_name, poke_id)

            db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
            db.session.commit();

            emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def addDecimal(self, number):
        num_string = str(number)
        if (len(num_string) == 1):
            return "0.{}".format(num_string)
        else:
            return "{}.{}".format(num_string[:-1], num_string[-1])

    def convertTypestoString(self, arr):
        if len(arr) == 1:
            return str(arr[0])
        else:
            return "{} / {}".format(arr[0], arr[1])

    def convertToHtML(self, name, pokeid, height, weight, types):
        return """<div className='pokemon-container'>
                    <h1 className='poke-name'>NAME: {}</h1>
                    <p className='poke-id'>ID: {}</p>
                    <p className='poke-height'>HEIGHT: {} m</p>
                    <p className='poke-weight'>WEIGHT: {} kg</p>
                    <p className='poke-types'>TYPE: {}</p>
                </div>""".format(name, pokeid, height, weight, types)

    def postImage(self, message):
        bot_message = "<a href={}><img style='width: 400px' src={}></a>".format(message, message)
        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();
        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    def urlImage(self, message):
        bot_message = "<a href={}>{}</a>".format(message, message)
        db.session.add(NewChat(self.bot_pfp, self.bot_name, bot_message, "bot", "n"))
        db.session.commit();
        emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

poke_bot = ChatBot()
commands = ["help", "about", "funtranslate", "pokedex", "github"]


@app.route('/')
def hello():
    emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    return flask.render_template('index.html')

@socketio.on('connect')
def on_connect():
    emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

@socketio.on('disconnect')
def on_disconnect():
    print ('Someone disconnected!')

@socketio.on("message to server")
def message_to_client(data):
    print("Received a message.")
    message_received = {
        "name": data["name"],
        "message": data["message"]
    }
    print(data["userID"])
    print(data["name"])
    print(data["message"])
    print(data["oauthimg"])
    print(data["authorized"])
    # db.session.add(NewChat(data["name"], data["message"], "user"))

    checkurlTest = checkurl(data["message"])

    if (checkurl(data["message"])):
        print("SUCCESSFUL CHECK")
        new_message = "<a href={}>{}</a>".format(data["message"], data["message"])
        db.session.add(NewChat(data["oauthimg"], data["name"], new_message, "user", data["authorized"]))
        db.session.commit()
    else:
        db.session.add(NewChat(data["oauthimg"], data["name"], data["message"], "user", data["authorized"]))
        db.session.commit()

    emit_all_messages(MESSAGES_RECEIVED_CHANNEL)

    print(data["message"])
    print("Sending message")
    
    print("Message sent")
    checkBotMessage(data["message"])
    isImage(data["message"])

@socketio.on("oauth to server")
def return_oauth_info(data):
    print(data["userID"])
    print("OAUTH: " + data["name"])
    print("OAUTH: " + data["imgurl"])
    socketio.emit(data["userID"], {
        "imgurl": data["imgurl"],
        "name": data["name"]
    })

if __name__ == '__main__': 
    socketio.run(
        app,
        debug=True,
        host = os.getenv("HOST", "0.0.0.0"),
        port = int(os.getenv("PORT", 8080))
    )
