# NECESSARY REQUIREMENTS:

0.  You'll need to install NODE.JS.  $ sudo apt-get install node should get it running.

1.  Clone the following repository:
    > git clone https://github.com/NJIT-CS490/project2-br96
    * Note: This will only work if you are a member of the NJIT-CS490 GITHUB.

    cd into the repository

2.  Run the following commands:
      - npm install
      - pip install flask-socketio
      - pip install eventlet
      - npm install -g webpack
      - npm install --save-dev webpack
      - npm install socket.io-client --save
      - sudo yum install postgresql postgresq-server postgresql-devel postgresql-contrib postgresql-docs
      - pip install psycopg2-binary
      - pip install Flask-SQLAlchemy==2.1

3.  You'll need to create a user in Postgres.  Do the following:
      - sudo service postgresql initdb
      - sudo service postgresql start
      - Enter psql by typing in $ psql and type the following:
        - CREATEUSER name WITH PASSWORD 'password' CREATEDB CREATEUSER;
        * You can check to see if your user exists with \du
        * Remember the name and password that you set

4.  Create a file in the current folder called "sql.env" and type following:
      $ echo SQL_USER=name >> sql.env
      $ echo SQL_PASSWORD=password >> sql.env
      $ echo DATABASE_URI="postgresql://name:password@localhost/postgres"
        * where name and password are the name and password you created in psql

5.  As a side measure, you can also run the following:
      - $ pip install -r requirements.txt
        * this will install the necessary dependencies, primarily for flask, if anything was missing

6.  Create a file called Procfile and enter the following:
      $ echo "web: python app.py"

7.  Run the command:
      $ pip freeze > requirements.txt
        * this will override the existing requirements previously cloned and enter in new ones

8.  To setup Heroku, run the following:
      - create a heroku account at Heroku.com
      - $ install heroku with:
        - $ npm install -g heroku
      - $ heroku login -i
      - $ heroku create
      - $ git add (add files, if you changed any)
      - $ git commit -m "init"
        * push to your github repository.  Heroku may require 1 commit / 1 push with:
          - $ git remote add origin (your repository)
          - $ git push origin master
      - $ git push heroku master

9.  Access: https://dashboard.heroku.com/apps and set up your config variables:
      SQL_USER=name
      SQL_PASSWORD=password
        *SQL_USER / SQL_PASSWORD are the keys, and name / password are the values

# ISSUES ENCOUNTERED

1.  Messages were delaying MASSIVELY after around 15 messages sent.  I found out the issue was
    with REACT.useEffect() running a second time on every call, essentially calling it exponentially, by a factor of 2^n.  This issue was resolved by sending the message directly 
    to the database and emitting all previous messages at the same time, meaning I only had to update my array of messages once per message send with React.useEffect().

2.  Changing the color of the bot message compared to the user message proved to have some 
    difficulty.  I settled on creating a new column in the database called "usertype" which stored a 4 letter variable either: "user" | "bot".  The usertype would be emitted alongside
    the message array, and the usertype variable would be passed into the className of each message.  This allowed me to style each message respectively, based on className="user" or 
    className="bot".

3.  The following issue was only present on a local server, but it was impossible to run 2 
    clients at the same without the database lagging behind.  If a message was sent from 1 client, it would take several seconds for the client to update or even not at all.  This issue didn't persist on AWS Cloud 9 as it ran on a dedicated port: 8080.  By updating the 
    HOST and PORT on app.py to something other then their default values, the lag became non-existent, allowing for a smooth message send and receive.

4.  I wanted to pass lists to my messages, however after sending to the server and retrieving 
    from the database, my messages would render with HTML tags included in the messages.  This was ofcourse unintended behavior as I wanted to apply the tags as actual tags.  React would treat the messages as strings by default.  A cool little attribute called "dangerouslySetInnerHTML" would allow for React to parse my string and utilize the necessary tags that I set up.  This is used in Message.jsx, and allowed for me to create a list in my mesages.  The drawback of this is that anyone can send HTML code via the message input.

5.  Unfortunately, funtranslation api only allows for 5 API calls per hour / 60 per day.  This
    means that if a user sends something with !! funtranslate "quote", they may receive nothing 
    because the server has nothing to send other than an error message in the console.  It was necessary to find the status code of the error which happened to be 429 in this case, and setup a default error to display to the user when this Status Code is returned.  

# PROJECT IMPROVEMENTS 

1.  At the moment, styling is dependent on the user having a 16:9 screen.  A future improvement
    would involve making the styling dynamic, specific to the device it is accessed on.  This 
    can be done solely in CSS, and would make use of the % unit rather than px.  px is fine if
    you're looking for same size consistency across all platforms, but it is in no way user friendly, say for example you want to access the app on your phone.  The sizing persists from desktop to laptop to phone, creating an unpleasant experience.

2.  I would be able to display all current users in the chat in a sidebar, or somewhere on the
    screen with the use of a second database.  Similar to the messages, on connection I would add the user to the database, and emit the list of users to all clients, in order to keep active track of all connected clients.  The process would be the reverse on client disconnection, where the user is removed from the database and the new list of users is emitted to all active clients.

3.  Custom chatrooms, tailored to topics, similarly to Slack would both improve performance 
    as well as user readability.  The users would be divided rather than utilizing an "all purpose / general" room like the one that currently exists.  Similar to before, we would need to route to different pages rather than the default ("/").  Implementing a database for each room would also be necessary so as to not retrieve all existing concurrent chats, defeating the purpose of rooms.