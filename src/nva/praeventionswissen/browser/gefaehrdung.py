# -*- coding:utf-8 -*-
import urllib
from operator import itemgetter
from App.config import getConfiguration
from Products.statusmessages.interfaces import IStatusMessage
from plone import api as ploneapi
from uvc.api import api
from zeam.form.base import DictDataManager, Error
from zope.interface import Interface
from Products.CMFPlone.utils import getToolByName
from ukbg.theme.interfaces import IThemeSpecific
from zeam.form.base.widgets import ActionWidget
from zeam.form.base import interfaces
from grokcore import component as grok
from nva.praeventionswissen.interfaces import ITaetigkeitform, IChemieform, IGefaehrdung
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

api.templatedir('templates')

class Gefaehrdung(api.Form):
    api.context(Interface)
    fields = api.Fields(IGefaehrdung)

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        sessiondata = getSessionData(self.request)
        taetigkeit = sessiondata.get('taetigkeit')
        self.setContentData(DictDataManager(taetigkeit))
        self.formurl = self.context.absolute_url() + '/gefaehrdung'

    @api.action('Weiter')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        taetigkeit = sessiondata.get('taetigkeit')
        taetigkeit['gefaehrdung'] = data.get('gefaehrdung') 
        sessiondata['taetigkeit'] = taetigkeit
        sessionid = setSessionData(self.request, sessiondata)
        gefaehrdung = data.get('gefaehrdung')
        if gefaehrdung == u'b':
            form = '/biologieform'
        elif gefaehrdung == u'c':
            form = '/chemieform'
        elif gefaehrdung == u'm':
            form = '/mechanikform'
        url = self.context.absolute_url() + form
        return self.response.redirect(url)
 
    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)

