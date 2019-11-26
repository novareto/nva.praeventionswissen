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
from nva.praeventionswissen.interfaces import ITaetigkeitform, IChemieform
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

api.templatedir('templates')

class TaetigkeitForm(api.Form):
    api.context(Interface)
    fields = api.Fields(ITaetigkeitform)

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        sessiondata = getSessionData(self.request)
        taetigkeit = sessiondata.get('taetigkeit')
        self.setContentData(DictDataManager(taetigkeit))
        self.formurl = self.context.absolute_url() + '/taetigkeitform'

    @api.action('Weiter')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        taetigkeit = sessiondata.get('taetigkeit')
        taetigkeit['title'] = data.get('title')
        taetigkeit['beschreibung'] = data.get('beschreibung')
        taetigkeit['gefaehrdung'] = data.get('gefaehrdung') 
        sessiondata['taetigkeit'] = taetigkeit
        sessiondata['hhplan'] = True
        sessionid = setSessionData(self.request, sessiondata)
        gefaehrdung = data.get('gefaehrdung')
        if gefaehrdung == u'c':
            form = '/chemieform'
        elif gefaehrdung == u'b':
            form = '/biologieform'
        elif gefaehrdung == u'm':
            form = '/mechanikform'
        url = self.context.absolute_url() + form
        return self.response.redirect(url)
 
    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)

class TaetigkeitShortForm(api.Form):
    api.context(Interface)
    fields = api.Fields(ITaetigkeitform)

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        formdict = {}
        formdict['description'] = self.context.description
        formdict['title'] = self.context.title
        formdict['beschreibung'] = self.context.text
        formdict['gefaehrdung'] = self.context.gefaehrdung
        self.setContentData(DictDataManager(formdict))
        self.formurl = self.context.absolute_url() + '/taetigkeitshortform'

    @api.action('Weiter')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.',
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        taetigkeit = sessiondata.get('taetigkeit')
        taetigkeit['title'] = data.get('title')
        taetigkeit['description'] = data.get('description')
        taetigkeit['beschreibung'] = data.get('beschreibung')
        taetigkeit['gefaehrdung'] = data.get('gefaehrdung')
        sessiondata['taetigkeit'] = taetigkeit
       
        if self.context.gefaehrdung == u'c':
            chemiesuche = {} 
            gefahrstoffe = []
            gefahrstoffschutz = self.context.gefahrstoffschutz
            for i in gefahrstoffschutz:
                gefahrstoffe.append(i.get('gefahrstoff'))
            chemiesuche['gefahrstoffe'] = gefahrstoffe
            chemiesuche['biologie'] = self.context.biologie
            chemiesuche['mechanik'] = self.context.mechanik
            chemiesuche['thermisch'] = self.context.thermisch
            sessiondata['chemiesuche'] = chemiesuche

        if self.context.gefaehrdung == u'm':
            mechaniksuche = {}
            mechaniksuche['abrieb'] = self.context.abrieb
            mechaniksuche['schnittcoup'] = self.context.schnitt
            mechaniksuche['riss'] = self.context.riss
            mechaniksuche['stick'] = self.context.stick
            if hasattr(self.context, 'schnittiso'):
                mechaniksuche['schnittiso'] = self.context.schnittiso
            else:
                if self.context.schnitt != u'nicht_relevant':
                    mechaniksuche['schnittiso'] = u'nicht_relevant'
                else:
                    mechaniksuche['schnittiso'] = u'nicht_relevant'
            mechaniksuche['stoss'] = self.context.stoss
            sessiondata['mechaniksuche'] = mechaniksuche

        sessiondata['hhplan'] = True
        sessionid = setSessionData(self.request, sessiondata)
        gefaehrdung = self.context.gefaehrdung
        if gefaehrdung == u'c':
            form = '/chemieform'
        elif gefaehrdung == u'm':
            form = '/mechanikform'
        url = self.context.absolute_url() + form
        return self.response.redirect(url)

    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)

