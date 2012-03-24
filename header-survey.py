#!/usr/bin/python
import subprocess
import sys
import httplib
import urlparse
from pickle import Pickler

class HeaderFetcher:
	def __init__(self,url,headers={'User-Agent':'Go Go Gadget Browser'}):
		self.report = {}
		self.initial_url = url
		self.request_headers = headers
	
	def fetch(self):
		self.fetchheaders(self.initial_url,self.request_headers)
	
	def fetchheaders(self,url,req_headers):
		try:
			u = urlparse.urlparse(url) 
			scheme = u.scheme
			ServerConnection = None
			con = None
			if 'http' == scheme:
				ServerConnection = httplib.HTTPConnection
			elif 'https' == scheme:
				ServerConnection = httplib.HTTPSConnection
			if None != ServerConnection:
				con = ServerConnection(u.hostname,u.port,timeout=10)
				con.request("GET",url,None,req_headers)
				res = con.getresponse()
				self.report[url] = res.getheaders()
				if 301 == res.status or 302 == res.status:
					redirect_url = res.getheader('Location')
					if not redirect_url in self.report:
						if len(self.report.keys())<40:
							self.fetchheaders(redirect_url,req_headers)
		except:
			print 'problem loading',url

def loadagents():
	f = open('agents','r')
	agents = [line.strip() for line in f.readlines()]
	f.close()
	return agents

def process(infile='t10k'):
	f = open(infile,'r')
	out = open('report.pickle','w')
	agents = loadagents()
	pickler = Pickler(out)
	for line in f.readlines():
		n, h = line.strip().split(',',1)
		for ua in agents:
			fetcher = HeaderFetcher('http://'+h,{'User-Agent':ua})
			print n, h, ua
			fetcher.fetch()
			pickler.dump((n,h,ua,fetcher.report))
			for url in fetcher.report:
				print 'GET',url
				for header in fetcher.report[url]:
					print header
			print '========================'
	print 'done'
	out.flush()
	out.close()
	f.close()
			
if __name__ == '__main__':
	process(sys.argv[-1])
