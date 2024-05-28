import tornado.ioloop
import tornado.web
import tornado.log
import tornado.options
import logging
import sqlite3
import json
from datetime import datetime

class UserService(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)

    def create_db(self):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute('''
                  CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at INTEGER,
                    updated_at INTEGER
                  )
                  ''')
        conn.commit()
        conn.close()

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.conn = sqlite3.connect("users.db")
        self.conn.row_factory = sqlite3.Row

    def on_finish(self):
        self.conn.close()

class UsersHandler(BaseHandler):
    def get(self):
        page_num = int(self.get_argument('page_num', 1))
        page_size = int(self.get_argument('page_size', 10))
        offset = (page_num -1) * page_size

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",(page_size, offset))
        users = cursor.fetchall()

        users = [dict(user) for user in users]
        self.write(json.dumps({"result": True, "users":users}))

    def post(self):
        name = self.get_argument('name')
        if not name:
            self.set_status(400)
            self.write(json.dumps({"result":False, "error": "Name is required"}))
            return
        
        timestamp = int(datetime.now().timestamp() * 1000000)
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (name, created_at, updated_at) VALUES (?, ?, ?)", (name, timestamp, timestamp))
        self.conn.commit()
        user_id = cursor.lastrowid

        self.set_status(201)
        self.write(json.dumps({"result": True, "user": {"id":user_id, "name": name, "created_at": timestamp, "updated_at":timestamp}}))

class UserHandler(BaseHandler):
    def get(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id))
        user = cursor.fetchone()

        if user:
            self.write(json.dumps({"result": True, "user":dict(user)}))
        else:
            self.set_status(404)
            self.write(json.dumps({"result": False, "error": "User not found"}))

def make_app(options):
    return UserService([
        (r"/users", UsersHandler),
        (r"/users/([0-9]+)", UserHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=6001)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.create_db()
    app.listen(options.port)
    logging.info("Starting user service. PORT: {}, DEBUG: {}".format(options.port, options.debug))


    tornado.ioloop.IOLoop.current().start()
    