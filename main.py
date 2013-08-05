import CssParser

import urllib2

response = urllib2.urlopen('http://getbootstrap.com/dist/css/bootstrap.css')
data = response.read()

result = CssParser.parse(data)

print result