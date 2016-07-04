import os
import flask
from model import storage

application = flask.Flask(__name__)

@application.route('/')
def index():
  score = storage.score()
  storage.update_score(score + 1)
  return "You got score %d!" % score

if __name__ == "__main__":
  application.run(host='0.0.0.0', port=3000)
