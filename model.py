import os
import MySQLdb

class Storage(object):
  def __init__(self):
    self.db = MySQLdb.connect(
      user   = os.getenv('MYSQL_USERNAME'),
      passwd = os.getenv('MYSQL_PASSWORD'),
      db     = os.getenv('MYSQL_INSTANCE_NAME'),
      host   = os.getenv('MYSQL_PORT_3306_TCP_ADDR'),
      port   = int(os.getenv('MYSQL_PORT_3306_TCP_PORT'))
    )

    cur = self.db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS scores(score INT)")
    cur.execute("INSERT INTO scores(score) VALUES(1234)")

  def score(self):
    cur = self.db.cursor()
    cur.execute("SELECT * FROM scores")
    row = cur.fetchone()
    return row[0]
  
  def update_score(self, score):
    cur = self.db.cursor()
    cur.execute("UPDATE scores set score=%d" % score)

storage = Storage()
