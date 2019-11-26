# -*- coding:utf-8 -*-
import urllib
import ast
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
from nva.praeventionswissen.interfaces import ITaetigkeitform, IChemieform, IHSfinden
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

api.templatedir('templates')

class HSFinden(api.Form):
    api.context(Interface)
    fields = api.Fields(IHSfinden)
    fields['gefahrstoffe'].allowOrdering = False

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        self.formtitle = u"Tätigkeit mit chemischen Gefährdungen"
        self.formdescription = u""
        sessiondata = getSessionData(self.request)
        if sessiondata:
            if sessiondata.get('taetigkeit'):
                taetigkeit = sessiondata.get('taetigkeit')
                self.formtitle = taetigkeit.get('title')
                self.formdescription = taetigkeit.get('description')
            if sessiondata.get('cbsuche'):
                if sessiondata.get('hhplan') == True:
                    url = self.context.absolute_url() + '/hautschutzmittel'
                    return self.response.redirect(url)
                self.setContentData(DictDataManager(sessiondata.get('cbsuche')))
        self.formurl = self.context.absolute_url() + '/hsfinden'

    @api.action('Weiter')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        sessiondata['chemiesuche'] = data
        sessionid = setSessionData(self.request, sessiondata)
        url = self.context.absolute_url() + '/hautschutzmittel'     
        return self.response.redirect(url)
 
    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)
