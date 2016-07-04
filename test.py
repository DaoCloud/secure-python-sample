import unittest
from model import storage

class TestSuite(unittest.TestCase):
  def test(self):
    score = storage.score()
    self.failIf(score != 1234)

def main():
  unittest.main()

if __name__ == "__main__":
  main()
