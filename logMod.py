import time, string, locale, threading, os

#Copyright (C) 2005 Alexander Schier
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

def default_settings():
	settings={};
	settings['logMod_logdir']='log'
	return settings
		
class chatMod:
	def __init__(self, bot):
		self.bot=bot
		self.channels={}
		self.files={}
		self.logdir=bot.getConfig("logMod_logdir", "log")
		if not os.path.isdir(self.logdir):
			os.mkdir(self.logdir)
		locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
		#self.hour=self.ts("%H") #saves the hour, to detect daychanges
		self.timer=threading.Timer(self.secsUntilDayChange(), self.dayChange)
		self.timer.start()
	
	def ts(self, format="%H:%M"):
		"""timestamp"""
		return time.strftime(format, time.localtime(time.time()))
		
	def secsUntilDayChange(self):
		"""calculate the Seconds to midnight"""
		tmp=time.localtime(time.time())
		wait=(24-tmp[3] -1)*60*60
		wait+=(60-tmp[4] -1)*60
		wait+=60-tmp[5]
		return wait

	def dayChange(self):
		for channel in self.channels:
			self.log(channel, "--- Day changed "+self.ts("%a %b %d %Y"))
		#restart the timer
		self.timer=threading.Timer(self.secsUntilDayChange(), self.dayChange)
		self.timer.start()
		
		
	def log(self, channel, string):
		if channel in self.channels:
			self.files[channel].write(string+"\n")
			self.files[channel].flush()

	def logPrivate(self, user, mystring):
		file=open(self.logdir+"/"+string.lower(user)+".log", "a")
		file.write(mystring+"\n")
		file.close()

	def joined(self, channel):
		self.channels[string.lower(channel)]=1
		#self.files[string.lower(channel)]=open(string.lower(channel)+".log", "a")
		self.files[string.lower(channel)]=open(self.logdir+"/"+string.lower(channel[1:])+".log", "a")

		self.log(channel, "--- Log opened "+self.ts("%a %b %d %H:%M:%S %Y"))
		self.log(channel, self.ts()+"-!- "+self.bot.nickname+" ["+self.bot.nickname+"@hostmask] has joined "+channel) #TODO: real Hostmask

	def msg(self, user, channel, msg):
		modesign=" "
		user=user.split("!")[0]
		if string.lower(channel)==string.lower(self.bot.nickname):
			self.logPrivate(user, self.ts()+"< "+user+"> "+msg)
		elif len(channel)>0 and channel[0]=="#":
			self.log(channel, self.ts()+"<"+modesign+user+"> "+msg)
		else:
			self.logPrivate(channel, self.ts()+"< "+self.bot.nickname+"> "+msg)

	def action(self, user, channel, msg):
		user=user.split("!")[0]
		self.log(channel, self.ts()+" * "+user+" "+msg)
		
	def modeChanged(self, user, channel, set, modes, args):
		user=user.split("!")[0]
		sign="+"
		if not set:
			sign="-"
		self.log(channel, self.ts()+"-!- mode/"+channel+" ["+sign+modes+" "+string.join(args, " ")+"] by "+user)
		
	def userKicked(self, kickee, channel, kicker, message):
		self.log(channel, self.ts()+"-!- "+kickee+" was kicked from "+channel+" by "+kicker+" ["+message+"]")

	def userJoined(self, user, channel):
		self.log(channel, self.ts()+"-!- "+user+" [user@hostmask] has joined "+channel)#TODO: real Hostmask

	def userLeft(self, user, channel):
		self.log(channel, self.ts()+"-!- "+user+" [user@hostmask] has left "+channel)#TODO: real Hostmask
		
	def topicUpdated(self, user, channel, newTopic):
		#TODO: first invoced on join. This should not be logged
		self.log(channel, self.ts()+"-!- "+user+" changed the topic of "+channel+" to: "+newTopic)

	def userRenamed(self, oldname, newname):
		#TODO: This can not handle different channels right
		for channel in self.channels:
			self.log(channel, self.ts()+"-!- "+oldname+" is now known as "+newname)
		
	def stop(self):
		for channel in self.channels:
			self.log(channel, "--- Log closed "+self.ts("%a %b %d %H:%M:%S %Y"))
			self.files[channel].close()
		self.timer.cancel()
		
	def connectionLost(self, reason):
		self.stop()
