# -*- coding: utf-8 -*-
##
## $id$
##
## This file is part of Indico.
## Copyright (C) 2002 - 2013 European Organization for Nuclear Research (CERN).
##
## Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.

from MaKaC.plugins import PluginsHolder
from MaKaC.conference import ConferenceHolder
from MaKaC.plugins.helpers import DBHelpers
from MaKaC.plugins.InstantMessaging.pages import WPConfModifChat, WPConferenceInstantMessaging
from MaKaC.plugins.InstantMessaging.urlHandlers import UHConfModifChat, UHConfModifChatSeeLogs, UHConferenceInstantMessaging
from MaKaC.plugins.InstantMessaging.XMPP.helpers import LogLinkGenerator
from MaKaC.plugins import InstantMessaging
from MaKaC.webinterface.rh.conferenceDisplay import RHConferenceBaseDisplay
from MaKaC.webinterface.rh.conferenceModif import RHConferenceModifBase
from MaKaC.errors import MaKaCError
from MaKaC.i18n import _
import urllib2
import pkg_resources

from indico.web.legacy import wrapUH
from indico.web.rh import RHHtdocs


class RHInstantMessagingHtdocs(RHHtdocs):
    """
    Static file handler for InstantMessaging plugin
    """

    _url = r"^/InstantMessaging/(?P<filepath>.*)$"
    _local_path = pkg_resources.resource_filename(InstantMessaging.__name__, "htdocs")
    _min_dir = 'InstantMessaging'


class RHChatModifBase(RHConferenceModifBase):


    def _checkProtection( self ):
        instantMessagingAdmins = []
        for imPlugin in PluginsHolder().getPluginType('InstantMessaging').getPluginList():
            instantMessagingAdmins.extend(imPlugin.getOption("admins").getValue())
        if not self._getUser() in instantMessagingAdmins:
            RHConferenceModifBase._checkProtection(self)

    def _checkParams(self, params):
        RHConferenceModifBase._checkParams(self, params)

        self._activeTabName = params.get("tab", None)

        self._tabs = []
        #fill the tabs with the active plugins in the Instant Messaging module
        for plugin in PluginsHolder().getPluginType('InstantMessaging').getPluginList():
            if plugin.isActive():
                self._tabs.append(plugin.getName())


class RHChatFormModif(RHChatModifBase):
    """ For the conference modification"""
    _url = wrapUH(UHConfModifChat)

    def _checkParams(self, params):
        RHChatModifBase._checkParams(self, params)
        if self._activeTabName and not self._activeTabName in self._tabs:
            self._cannotViewTab = True
        else:
            self._cannotViewTab = False
            if not self._activeTabName and self._tabs:
                self._activeTabName = self._tabs[0]

    def _process( self ):
        p = WPConfModifChat( self, self._conf )
        return p.display()


class RHChatSeeLogs(RHChatModifBase):
    """ For the conference modification"""
    _url = wrapUH(UHConfModifChatSeeLogs)

    def _checkParams(self, params):
        RHChatModifBase._checkParams(self, params)
        self._conf = ConferenceHolder().getById(params['confId'])
        self._chatroom = DBHelpers.getChatroom(params['chatroom'])
        self._sdate = params['sdate'] if params.has_key('sdate') else None
        self._edate = params['edate'] if params.has_key('edate') else None
        self._forEvent = bool(params['forEvent']) if params.has_key('forEvent') else None
        self._getAll = not self._sdate and not self._edate and not self._forEvent

    def _process( self ):
        if self._getAll:
            url = LogLinkGenerator(self._chatroom).generate()
        elif self._forEvent:
            url = LogLinkGenerator(self._chatroom).generate(str(self._conf.getStartDate().date()), str(self._conf.getEndDate().date()))
        else:
            url = LogLinkGenerator(self._chatroom).generate(self._sdate, self._edate)

        req = urllib2.Request(url, None, {'Accept-Charset' : 'utf-8'})
        document = urllib2.urlopen(req).read()
        if document is '':
            raise MaKaCError('No logs were found for these dates')
        return document


class RHInstantMessagingDisplay(RHConferenceBaseDisplay):
    """ For the conference display"""
    _url = wrapUH(UHConferenceInstantMessaging)

    def _checkParams(self, params):
        RHConferenceBaseDisplay._checkParams(self, params)

    def _process( self ):
        p = WPConferenceInstantMessaging( self, self._conf )
        return p.display()

