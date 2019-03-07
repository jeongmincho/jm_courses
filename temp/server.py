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
        url.wfile.write("<body><p>returning empty line</p></body>")


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
        url.wfile.write("<body><p>%s</p></body>" % count_str)
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
        url.wfile.write("<body><p>%s</p></body>" % count_str)
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
        url.wfile.write("<body><p>returning empty line</p></body>")


def clear_all(url, path):
    print "arrived at clear_all"
    database = "sqlite/db/registrar.db"
    conn = create_connection(database)
    cur = conn.cursor()
    print path
    cur.execute("delete from counts")
    url.wfile.write("<body><p>all has been cleared</p></body>")
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
        "<body><p>count for %s has been cleared</p></body>" % dept)
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
        url.wfile.write("<body><p>returning empty line</p></body>")


def search_dept(url, path):
    print "arrived at search_dept"
    dept = path[0]
    # if the dept search query isn't 3-char, ignore that
    if (len(dept) != 3):
        url.wfile.write("<body><p>returning empty line</p></body>")
        return
    insert_or_incr(dept)
    for department in subj:
        if (department.get("code").lower() == dept):
            for course in department.get("courses"):
                url.wfile.write("<body><p>%s %s %s</p></body>" %
                                (department.get("code"), course.get("catalog_number"), course.get("title")))


def search_course(url, path):
    print "arrived at search_course"
    dept = path[0]
    num = path[1]
    # if either dept or num search query isn't 3-char, ignore that
    if (len(dept) != 3 or len(num) != 3):
        url.wfile.write("<body><p>returning empty line</p></body>")
        return
    insert_or_incr(dept)
    for department in subj:
        if (department.get("code").lower() == dept):
            for course in department.get("courses"):
                if (course.get("catalog_number").lower() == num):
                    url.wfile.write("<body><p>%s %s %s</p></body>" %
                                    (department.get("code"), course.get("catalog_number"), course.get("title")))


# def route_index(self, path, query):
#     """Handles routing for the application's entry point'"""
#     try:
#         return ResponseData(status=HTTP_STATUS["OK"], content_type="text_html",
#                             # Open a binary stream for reading the index
#                             # HTML file
#                             data_stream=open(os.path.join(sys.path[0],
#                                                           path[1:]), "rb"))
#     except IOError as err:
#         # Couldn't open the stream
#         raise HTTPStatusError(HTTP_STATUS["INTERNAL_SERVER_ERROR"],
#                               str(err))


class Reply(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # this is so dirty, i don't like it.
        if (self.path == '/'):
            self.path = "/index.html"
            f = open(curdir + sep + self.path)
            self.wfile.write(f.read())
            return
        else:
            path = self.path[1:].split("/")
        print path
        if (path[0] == "count"):
            return_counts(self, path)

        elif (path[0] == "clear"):
            clear_counts(self, path)

        else:
            return_search(self, path)
        return


all = []


def get_OIT(url):
    r = requests.get(url)
    if r.status_code != 200:
        return ["bad json"]
    return r.json()


def main():
    # Read OIT feed before starting the server.
    print("server is listening on port %s" % sys.argv[1])
    SocketServer.ForkingTCPServer(
        ('', int(sys.argv[1])), Reply).serve_forever()
    # SocketServer.ForkingTCPServer(('', 33332), Reply).serve_forever()


oit = 'http://etcweb.princeton.edu/webfeeds/courseofferings/?fmt=json&term=current&subject=all'
all = get_OIT(oit)
subj = all["term"][0]["subjects"]


main()
