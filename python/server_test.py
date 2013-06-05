#!/usr/bin/python


__author__ = 'Masato Taruishi'
__copyright__ = 'Copyright 2013 Masato Taruishi'


import server
import tornado.testing
import tornado.web
import unittest


class LsHandlerTest(tornado.testing.AsyncHTTPTestCase):

  def get_app(self):
    return tornado.web.Application([(r'/', server.LsHandler)])

  def test_toppage_should_contain_vmlinuz(self):
    self.http_client.fetch(self.get_url('/'), self.stop)
    res = self.wait()
    self.assertIn('vmlinuz', res.body)


def all():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(LsHandlerTest))
  return suite


if __name__ == '__main__':
  tornado.testing.main()
