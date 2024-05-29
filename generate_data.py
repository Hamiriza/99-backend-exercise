import os
import sqlite3
import time
import random
import names

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def init_listings_db(conn):
    cursor = conn.cursor()
    # Delete table if exists
    cursor.execute("DROP TABLE IF EXISTS 'listings';")    
    # Create table
    cursor.execute(
        "CREATE TABLE 'listings' ("
        + "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        + "user_id INTEGER NOT NULL,"
        + "listing_type TEXT NOT NULL,"
        + "price INTEGER NOT NULL,"
        + "created_at INTEGER NOT NULL,"
        + "updated_at INTEGER NOT NULL"
        + ");"
    )
    conn.commit() 

def init_users_db(conn):
    cursor = conn.cursor()
    # Delete table if exists
    cursor.execute("DROP TABLE IF EXISTS 'users';")
    # Create table
    cursor.execute(
        "CREATE TABLE 'users' ("
        + "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        + "name TEXT NOT NULL,"
        + "created_at INTEGER NOT NULL,"
        + "updated_at INTEGER NOT NULL"
        + ");"
    )
    conn.commit()

def insert_random_users(conn, num):
    insert_names_sql = "INSERT INTO users (name, created_at, updated_at) VALUES (?, ?, ?)"
    cursor = conn.cursor()
    for x in range(num):
        time_now = int(time.time() * 1e6)
        name = names.get_full_name()
        cursor.execute(insert_names_sql, (name, time_now, time_now))
        conn.commit()
        print("INSERT NAME: name: {}".format(name))

def insert_random_listings(conn, num):
    insert_listing_sql = "INSERT INTO listings (user_id, listing_type, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?)"
    cursor = conn.cursor()
    for user_id in range(1, num):
        for i in range(random.randrange(1, 5)):
            time_now = int(time.time() * 1e6)
            price = random.randrange(3000, 20000, 500)
            listing_type = random.choice(['rent', 'sale'])
            cursor.execute(insert_listing_sql, (user_id, listing_type, price, time_now, time_now))
            conn.commit()
            print("INSERT LISTING: user_id: {}, listing_type: {}, price: {}".format(user_id, listing_type, price))


if __name__ == "__main__":
    try:
        listings_conn = create_connection("./services/listings/listings.db")
        users_conn = create_connection("./services/users/users.db")
        init_listings_db(listings_conn)
        init_users_db(users_conn)

        insert_random_listings(listings_conn, 50)
        insert_random_users(users_conn, 50)
        os.chmod("./services/listings/listings.db", 0o644)
        os.chmod("./services/users/users.db", 0o644)
    except Exception as e:
        print ("Error: ", str(e))