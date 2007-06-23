# This file is part of OtfBot.
#
# OtfBot is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# OtfBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OtfBot; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
# (c) 2006 by Alexander Schier
#

import time
import chatMod


def default_settings():
	settings={};
	return settings
		
class chatMod(chatMod.chatMod):
	def __init__(self, bot):
		self.bot=bot
		self.messages={}

	def remind(self):
		when=int( (time.time())/60 )
		messages=[]
		if self.messages.has_key(when):
			messages=self.messages[when]
			del self.messages[when]

		for message in messages:
			self.bot.sendmsg(message[0], message[1]+": Reminder: "+message[2])

	def msg(self, user, channel, msg):
		#if channel == self.bot.nickname:
		#if msg[0]=="!" or msg[:len(self.bot.nickname)]==self.bot.nickname:
		if msg[0:10]=="!remindme ":
			user=user.split("!")[0]

			tmp=msg.split(" ", 2)
			try:
				wait=float(tmp[1])
			except ValueError:
				self.bot.sendmsg(channel, user.split("!")[0]+": invalid number format \""+tmp[1]+"\".")
				return
			text=str(tmp[2])
			
			when=int( (time.time()+wait*60)/60 ) #when will this be executed? (minutes since 1.1.1970 ;-))
			if self.messages.has_key(when):
				self.messages[when].append([channel, user, text])
			else:
				self.messages[when]=[[channel, user, text]]
			self.bot.getReactor().callLater(wait*60, self.remind)
