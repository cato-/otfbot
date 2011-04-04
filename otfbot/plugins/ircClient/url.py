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
# (c) 2008 by Alexander Schier
# (c) 2008 - 2011 by Robert Weidlich
#

import urllib2, re, string
from HTMLParser import HTMLParser, HTMLParseError
from lxml.html.soupparser import fromstring

from otfbot.lib import chatMod, urlutils
from otfbot.lib.pluginSupport.decorators import callback

class Plugin(chatMod.chatMod):

    def __init__(self, bot):
        self.bot = bot
        self.autoTiny=self.bot.config.get("autotiny", False, "url", self.bot.network)
        self.autoTinyLength=int(self.bot.config.get("autoLength", "50", "url", self.bot.network))
        self.autoPreview=self.bot.config.get("autopreview", False, "url", self.bot.network)
        self.lasturl=""

    @callback
    def command(self, user, channel, command, options):
        response = ""
        headers=None
        if "preview" in command:
            if options == "":
                if self.lasturl:
                    options=self.lasturl
                else:
                    return
            d=urlutils.download(options, headers={'Accept':'text/html'})
            d.addCallback(self.processPreview, channel)
            d.addErrback(self.error, channel)
        if "tinyurl" in command:
            if options == "":
                options = self.lasturl
            d=urlutils.download("http://tinyurl.com/api-create.php?url="+options)
            d.addCallback(self.processTiny, channel)
            d.addErrback(self.error, channel)

    def error(self, failure, channel):
        self.bot.sendmsg(channel, "Error while retrieving informations: "+failure.getErrorMessage())

    def processTiny(self, data, channel):
        self.bot.sendmsg(channel, "[Link Info] "+data )

    def processPreview(self, data, channel):
        root = fromstring(data)
        result = root.find('.//title').text
        if result:
            result = re.sub(r'\s+', ' ', result).strip()
            self.bot.sendmsg(channel, "[Link Info] " + result)
    
    @callback
    def msg(self, user, channel, msg):
        mask=0        
        # http://www.truerwords.net/2539
        regex=re.match(".*((ftp|http|https):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-])).*", msg)
        if regex:
            url=regex.group(1)
            if string.lower(user.getNick()) != string.lower(self.bot.nickname):
                cmd=""
                if not "tinyurl.com" in url:
                    if len(url) > self.autoTinyLength and self.autoTiny:
                        cmd+="+tinyurl"
                    else:
                        self.lasturl=url
                if self.autoPreview:
                    cmd+="+preview"
                self.command(user, channel, cmd, url)

