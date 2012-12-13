import socket
import threading
import time
import os, signal, sys
import simplejson
import lxml.html
import urllib
	
server = "irc.rizon.net"
channels = ["#icebot", "#globalwaves"]
botnick = "GWbot"
port = 6667
debug = "1"
password = ""
comms = "!listen || !onair"
# iurl = 'http://pub1.globalwaves.tk:8000/status_json.xsl'
# self.icejson = simplejson.load(urllib.urlopen(iurl))

def joinchan(chan):
	irc.send("JOIN "+ chan +"\n")
	
def GetNick(text):
	ni = text.split('!')
	nick = ni[0].strip(':')
	return nick
	
def GetChan(text):
	ch = text.split("#")
	cha = ch[1].split()
	chan = "#"+cha[0]
	return chan

def notice(nick, text):
	irc.send("NOTICE "+nick+" :"+text+"\r\n")
	

	
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :GW bot\n") # user authentication
irc.send("NICK "+ botnick +"\n")

for channel in channels:
	joinchan(channel)

class MyThread(threading.Thread):	
	
	def update(self):
		self.iurl = 'http://pub1.globalwaves.tk:8000/status_json.xsl'
		self.icejson = simplejson.load(urllib.urlopen(self.iurl))
		
	def CountAll(self,stream):
		try:
			a = int(self.icejson["/gw-"+stream+"/mp3"]["listeners"])
		except:
			a = 0
		try:
			b = int(self.icejson["/gw-"+stream+"/ogg"]["listeners"])
		except:
			b = 0
		try:
			c = int(self.icejson["/gw-"+stream+"/aacp"]["listeners"])
		except:
			c = 0
		
		d = a+b+c
		return d
		
	def cons(self):	
		while 1:
			inp = raw_input("")
			if inp == "/shutdown":
				for channel in channels:
					irc.send("PRIVMSG "+channel+" :Shutting down!\r\n")
				time.sleep(2)
				os.kill(os.getpid(), signal.SIGINT)
				
			elif "/raw" in inp != -1:
				binp = inp.split("/raw")
				irc.send(binp[1]+'\r\n')
			else:
				for channel in channels:
					irc.send('privmsg '+channel+" :"+inp+"\r\n")
			
	def run(self):
		while 1:
			self.update()
			text=irc.recv(4096)
			if debug == "0":
				bub = text.split(':')
				ni = text.split('!')
				nick = ni[0].strip(':')
				print bub[1]+"	"+nick
			else:
				print text
			
			if text.find('End of /MOTD command') != -1:
				time.sleep(3)
				irc.send("PRIVMSG nickserv :identify "+password+"\r\n")

			if text.find('KICK') != -1:
				channel = GetChan(text)
				joinchan(channel)

			
			if text.find(':http') != -1:
				channel = GetChan(text)
				ar = text.partition('http')
				arg = str(ar[1]) + str(ar[2])
				arg = arg.replace('\r\n', '')
				if "youtube" in arg:
					pass
				else:
					try:	
						t = lxml.html.parse(str(arg))
						irc.send("PRIVMSG "+channel+" :Title: "+t.find(".//title").text+"\r\n")
					except UnicodeEncodeError:
						irc.send("PRIVMSG "+channel+" :Lol there is some Unicode error\r\n")
						continue
					except:
						pass
				
			if text.find('/watch?v=') != -1:
				channel = GetChan(text)
				ar = text.split('/watch?v=')
				arg = ar[1].split('&')
				
				print arg[0]
				
				id = arg[0]
				url = 'http://gdata.youtube.com/feeds/api/videos/%s?alt=json&v=2' % id

				json = simplejson.load(urllib.urlopen(url))

				title = json['entry']['title']['$t']
				author = json['entry']['author'][0]['name']
				
				author1 = str(author).split("'")
				author2 = author1[-2]
				
				irc.send("PRIVMSG "+channel+" :00,01You01,05Tube: "+title+" 01,00By "+str(author2)+"\r\n")
				
			
			if text.find('PING') != -1:
				split = text.split()
				thing = split[1].strip(':')
				irc.send('PONG :' + thing + '\r\n')
			
			if text.find(':!help') != -1:
				nick = GetNick(text)
				irc.send("NOTICE "+nick+" :my commands are: "+comms+"\r\n")
			
			if text.find(':!listen') != -1:
				nick = GetNick(text)
				notice(nick, "http://listen.globalwaves.tk/trance/mp3.m3u Trance channel ("+str(self.CountAll("trance"))+" listeners)")
				notice(nick, "http://listen.globalwaves.tk/main/mp3.m3u Main channel ("+str(self.CountAll("main"))+" listeners)")
				notice(nick, "http://listen.globalwaves.tk/dnb/mp3.m3u Drum & Bass channel ("+str(self.CountAll("dnb"))+" listeners)")
				# http://listen.globalwaves.tk/%s/mp3.m3u
				# ["trance","main","dnb"]
				
			if text.find(':!onair') != -1:
				nick = GetNick(text)
				
				try:
					notice(nick,"Trance: "+ self.icejson["/gw-trance/mp3"]["nowplaying"]+" ("+str(self.CountAll("trance"))+" listeners)")
				except:
					notice(nick,"Trance: 05 stream unavailable")
				try:
					notice(nick,"Main: "+ self.icejson["/gw-main/mp3"]["nowplaying"]+" ("+str(self.CountAll("main"))+" listeners)")
				except:
					notice(nick,"Main: 05 stream unavailable")
				try:
					notice(nick,"Drum & Bass: "+ self.icejson["/gw-dnb/mp3"]["nowplaying"]+" ("+str(self.CountAll("dnb"))+" listeners)")
				except:
					notice(nick,"Drum & Bass: 05 stream unavailable")
				
				#TODO: count all listeners
				
			if text.find(':!cake') != -1:
				channel = GetChan(text)
				irc.send('PRIVMSG '+channel+ ' :The cake is being made!\r\n')
				time.sleep(10)
				ni = text.split('!')
				nick = ni[0].strip(':')
				irc.send('PRIVMSG '+channel+ ' :Bing! cake for '+nick+'\r\n')

MyThread().start()
MyThread().cons()