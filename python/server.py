#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example server to show the files in your root directory.
# 
#  1. Runs this server and checks whether it shows the contents of
#     your root directory:
#
#      $ python server.py
#      $ w3m http://localhost:12345/ # from a different console
#
#  2. Runs the test and checks whether the test passes:
#
#      $ python server_test.py 
#
#        <snip>
# 
#      OK
#      [I 130605 12:35:16 testing:436] PASS
#
#  3. Reads the tornado document and check how it works:
#
#      $ w3m http://www.tornadoweb.org/en/stable/
#      $ w3m http://www.tornadoweb.org/en/branch2.1/web.html
#
#  4. Use pydoc and take a look at the document and checks how
#     inline comments are genearted as user's documentation:
#
#      $ pydoc server
#      $ pydoc server.LsHandler
#
# Homework:
#
#   1. Adds a new handler called 'DfHandler' to show the output of 'df'
#      and make it accessible at http://localhost:12345/df. In addition,
#      adds the appropriate testcase for it in server_test.py. When
#      you write your code, please follow the coding style defined
#      below. Also, use the following command to see what assertions
#      are available in your testcase:
#
#       $ pydoc tornado.testing.AsyncHTTPTestCase
#
#   2. Creates a new handler called 'StatuszHandler' to show useful
#      information in your real admin work and make it accessible at
#      http://localhost:12345/statusz.
#
#   3. Creates a fake stub for command execution and write a test
#      for /bin/ls failures in LsHandlerTest.
#
# Coding style:
#
# - Each definition in top level should be separated by 2 empty lines.
# - Each line should not exceed 80 columns.
# - Comments by '#' are for code readers.
# - Comments by '"""', or docstring, are both for users and readers.
# - Functions which starts with '_' doesn't appear in pydoc so you can
#   define private functions.
# - Use ' for string literal except that it contains '.
# - All public methods/function should have docstring.
# - Strats with capital case when you put '.' at the end.
# - Describes who is the first author and copyright holder.
# - import libraries to use should be ordered in alpabetical order.
# - 2 spaces for structual indent and 4 spaces for line-wrap
# - Method/Function name starts with capital case.
# - If your method/functions accepts argument, then you should write it
#   in your docstring. Return value and expected exceptions should be
#   mentioned as well.
# - Considers code readers to make it easy to understand.
# - Tests may not follow the above policies but better to follow.
#


"""
simple web server to show the system information

This is a simple web server to execute several command line tools
and show the output for your browser.

The easiest way to use this module to run this module directly by:

 python server.py

This listen the port 12345 and handles http requests. Go to:

 http://localhost:12345/

to see the server output.
"""


__author__ = 'Masato Taruishi'
__copyright__ = 'Copyright 2013 Masato Taruishi'


import subprocess
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web


def _Escape(str):
  """Escapes byte string for html CDATA.

  Args:
    str: byte string

  Returns:
    Unicode string which is valid within html.  

  Raises:
    UnicodeDecodeError: Thrown when the specified byte string
                        can't be decoded.
  """
  return tornado.escape.xhtml_escape(tornado.escape.to_unicode(str))


class LsHandler(tornado.web.RequestHandler):
  """Shows the output of '/bin/ls'.

  This handler accepts GET requests and send the output of
  '/bin/ls -l /'

  The typical use case is as follows:

  >>> app = tornado.web.Application([(r'/', LsHandler)])
  >>> app.listen(12345)
  >>> tornado.ioloop.IOLoop.instance().start()
  """

  def get(self):
    """Handles GET requests."""
    p = subprocess.Popen(
        'LANG=ja_JP.UTF-8 /bin/ls -l /', shell=True, stdout=subprocess.PIPE)
    self.write('<pre>%s</pre>' % _Escape(p.stdout.read()))
    p.wait()


def main():
  """Starts the server."""
  tornado.options.parse_command_line()
  app = tornado.web.Application(
      [
          (r'/', LsHandler),
      ])
  app.listen(12345)
  tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
  main()
