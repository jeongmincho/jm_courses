import SocketServer
import SimpleHTTPServer
import requests
import sqlite3
import sys
from sqlite3 import Error
from os import curdir
from os import sep


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print("connection made successfully")
        return conn
    except Error as e:
        print(e)
    return None


def insert_or_incr(query):
    database = "sqlite/db/registrar.db"
    # create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS counts(dept VARCHAR(10) PRIMARY KEY, counter INT)")
    # cur.execute("""insert or ignore into counts values ('COS',0)""")
    conn.commit()
    cur = conn.cursor()
    # print("something")
    # print(cur)
    cur.execute("insert or ignore into counts values (?,0)", (query,))
    cur.execute(
        "UPDATE counts SET counter = counter + 1 WHERE dept = ?", (query,))
    cur.execute("select * from counts")
    # print(cur.fetchall())
    conn.commit()
    cur.close()
    conn.close()


def return_counts(url, path):
    print "arrived at return_counts"
    # if there's only one word, that's potentially counts for all
    if (len(path) == 1):
        counts_all(url, path)

    # if there's two words, that's potentially counts for dept
    elif (len(path) == 2):
        counts_dept(url, path)

    # anything else, should be ignored (return empty blank line)
    else:
        url.wfile.write("<div>returning empty line</div>")


def counts_all(url, path):
    print "arrived at counts_all"
    database = "sqlite/db/registrar.db"
    # create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    print path
    cur.execute("select * from counts")
    arr = cur.fetchall()
    # print arr
    for tup in arr:
        # print tup
        count_str = tup[0] + " " + str(tup[1])
        # print count_str
        url.wfile.write("<div>%s</div>" % count_str)
    conn.commit()
    cur.close()
    conn.close()


def counts_dept(url, path):
    print "arrived at counts_dept"
    database = "sqlite/db/registrar.db"
    # create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    dept = path[1]
    print path
    cur.execute("select * from counts where dept = ?", (dept,))
    arr = cur.fetchall()
    # print arr
    for tup in arr:
        # print tup
        count_str = tup[0] + " " + str(tup[1])
        # print count_str
        url.wfile.write("<div>%s</div>" % count_str)
    conn.commit()
    cur.close()
    conn.close()


def clear_counts(url, path):
    print "arrived at clear_counts"
    # if there's only one word, that's potentially a dept search
    if (len(path) == 1):
        clear_all(url, path)

    # if there's two words, that's potentially a course search
    elif (len(path) == 2):
        clear_dept(url, path)

    # anything else, should be ignored (return empty blank line)
    else:
        url.wfile.write("<div>returning empty line</div>")


def clear_all(url, path):
    print "arrived at clear_all"
    database = "sqlite/db/registrar.db"
    conn = create_connection(database)
    cur = conn.cursor()
    print path
    cur.execute("delete from counts")
    url.wfile.write("<div>all has been cleared</div>")
    conn.commit()
    cur.close()
    conn.close()


def clear_dept(url, path):
    print "arrived at clear_dept"
    database = "sqlite/db/registrar.db"
    conn = create_connection(database)
    cur = conn.cursor()
    dept = path[1]
    print path
    cur.execute("delete from counts where dept = ?", (dept,))
    url.wfile.write(
        "<div>count for %s has been cleared</div>" % dept)
    conn.commit()
    cur.close()
    conn.close()


def return_search(url, path):
    print "arrived at return_search"
    # if there's only one word, that's potentially counts for all
    if (len(path) == 1):
        search_dept(url, path)

    # if there's two words, that's potentially counts for dept
    elif (len(path) == 2):
        search_course(url, path)

    # anything else, should be ignored (return empty blank line)
    else:
        url.wfile.write("<div>returning empty line</div>")


def search_dept(url, path):
    print "arrived at search_dept"
    dept = path[0]
    # if the dept search query isn't 3-char, ignore that
    if (len(dept) != 3):
        url.wfile.write("<div>returning empty line</div>")
        return
    insert_or_incr(dept)
    for department in subj:
        if (department.get("code").lower() == dept):
            for course in department.get("courses"):
                url.wfile.write("<div>%s %s %s</div>" %
                                (department.get("code"), course.get("catalog_number"), course.get("title")))


def search_course(url, path):
    print "arrived at search_course"
    dept = path[0]
    num = path[1]
    # if either dept or num search query isn't 3-char, ignore that
    if (len(dept) != 3 or len(num) != 3):
        url.wfile.write("<div>returning empty line</div>")
        return
    insert_or_incr(dept)
    for department in subj:
        if (department.get("code").lower() == dept):
            for course in department.get("courses"):
                if (course.get("catalog_number").lower() == num):
                    url.wfile.write("<div>%s %s %s</div>" %
                                    (department.get("code"), course.get("catalog_number"), course.get("title")))


class Reply(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        # self.send_header("Content-type", "text/html")
        # this is so dirty, i don't like it.
        self.send_response(200)
        if (self.path == '/'):
            self.path = "/index.html"
            mimetype = 'text/html'
            f = open(curdir + sep + self.path)
            self.send_header("Content-type", mimetype)
            self.end_headers()
            self.wfile.write(f.read())
        elif self.path.endswith(".css"):
            mimetype = 'text/css'
            f = open(curdir + sep + self.path)
            self.send_header("Content-type", mimetype)
            self.end_headers()
            self.wfile.write(f.read())
        elif self.path.endswith(".jpg"):
            mimetype = 'text/jpg'
            f = open(curdir + sep + self.path)
            self.send_header("Content-type", mimetype)
            self.end_headers()
            self.wfile.write(f.read())
        else:
            path = self.path[1:].split("/")
            mimetype = 'text/html'
            self.send_header("Content-type", mimetype)
            self.end_headers()
            self.wfile.write("<head><link rel=stylesheet href=style.css /></head>")
            self.wfile.write("<body><div class=container>")
            print path
            if (path[0] == "count"):
                return_counts(self, path)
            elif (path[0] == "clear"):
                clear_counts(self, path)
            else:
                return_search(self, path)
            self.wfile.write("</div></body>")
        return


all = []


def get_OIT(url):
    r = requests.get(url)
    if r.status_code != 200:
        return ["bad json"]
    return r.json()


def main():
    # Read OIT feed before starting the server.
    print("server is listening on port 33333")
    SocketServer.ForkingTCPServer(('', 33333), Reply).serve_forever()
    # SocketServer.ForkingTCPServer(('', 33332), Reply).serve_forever()


oit = 'http://etcweb.princeton.edu/webfeeds/courseofferings/?fmt=json&term=current&subject=all'
all = get_OIT(oit)
subj = all["term"][0]["subjects"]


main()
