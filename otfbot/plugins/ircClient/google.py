# This file is part of OtfBot.
# -*- coding: utf-8 -*-
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
# (c) 2008 - 2010 by Alexander Schier
# (c) 2008 - 2010 by Robert Weidlich
#

"""
    Query Google services. Currently only googlefight is implemented.
"""

from otfbot.lib import chatMod
from otfbot.lib import urlutils
from otfbot.lib.pluginSupport.decorators import callback


class Plugin(chatMod.chatMod):
    baseUrl = 'http://www.google.de/search?hl=de&q="%s"'
    countRE = ".*<b>1</b> - <b>10</b>.*?<b>([0-9\.]*)</b>.*"

    def __init__(self, bot):
        self.bot = bot

    @callback
    def command(self, user, channel, command, options):
        response = ""
        headers = None
        if command == "googlefight":
            words = options.split(":")
            if len(words) == 2:
                #TODO: blocking
                data1 = urlutils.download(self.baseURL % words[0].replace(" ", "+"))
                data2 = urlutils.download(self.baseURL % words[1].replace(" ", "+"))

                count1 = "0"
                count2 = "0"
                match = re.match(self.countRE, data1, re.S)
                if match:
                    count1 = match.group(1)

                match = re.match(elf.countRE, data2, re.S)
                if match:
                    count2 = match.group(1)

                ansmsg = "Google Fight!: %s siegt ueber %s (%s zu %s Treffer)"
                if(int(re.sub("\.", "", count1)) > int(re.sub("\.", "", count2))):
                    self.bot.sendmsg(channel, ansmsg % (words[0], words[1], str(count1), count2))
                else:
                    self.bot.sendmsg(channel, ansmsg % (words[1], words[0], str(count2), count1))
            else:
                self.bot.sendmsg(channel, "!googlefight wort1:wort2")
