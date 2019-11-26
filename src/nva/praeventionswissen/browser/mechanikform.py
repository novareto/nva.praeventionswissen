# -*- coding:utf-8 -*-
import urllib
import ast
from operator import itemgetter
from App.config import getConfiguration
from Products.statusmessages.interfaces import IStatusMessage
from plone import api as ploneapi
#from pymongo import MongoClient
from uvc.api import api
from zeam.form.base import DictDataManager
from zope.interface import Interface
from Products.CMFPlone.utils import getToolByName
from ukbg.theme.interfaces import IThemeSpecific
from zeam.form.base.widgets import ActionWidget
from zeam.form.base import interfaces
from grokcore import component as grok
from nva.praeventionswissen.interfaces import IMechanikform
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

api.templatedir('templates')

bgfaktor = {
    'abrieb':1,
    'schnittcoup':2,
    'riss':1,
    'stick':2,
    'schnittiso':2,
    'stoss':2}
schnittiso = {
    'A':1,
    'B':2,
    'C':3,
    'D':4,
    'E':5,
    'F':6}

def rankmapping(value):
    if value == u'gering':
        return u'1'
    if value == u'mittel':
        return u'2'
    if value == u'hoch':
        return u'3'
    return u'nicht_relevant'

def rankmapping2(value):
    if value == u'gering':
        return u'1'
    if value == u'mittel':
        return u'3'
    if value == u'hoch':
        return u'4'
    return u'nicht_relevant'

def rankmapping3(value):
    if value == u'gering':
        return u'A'
    if value == u'mittel':
        return u'C'
    if value == u'hoch':
        return u'F'
    return u'nicht_relevant'

class MechanikForm(api.Form):
    api.context(Interface)
    fields = api.Fields(IMechanikform)

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        self.formtitle = u"Tätigkeit mit mechanischen Gefährdungen"
        self.formdescription = u""
        sessiondata = getSessionData(self.request)
        if sessiondata:
            if sessiondata.get('taetigkeit'):
                taetigkeit = sessiondata.get('taetigkeit')
                self.formtitle = taetigkeit.get('title')
                self.formdescription = taetigkeit.get('description')
            if sessiondata.get('mechaniksuche'):
                mechdata = sessiondata.get('mechaniksuche')
                mydict = {}
                for i in mechdata:
                    if i in ['abrieb', 'riss', 'stick']:
                        mydict[i] = rankmapping(mechdata[i])
                    elif i == 'schnittcoup':
                        mydict[i] = rankmapping2(mechdata[i])
                    elif i == 'schnittiso':
                        mydict[i] = rankmapping3(mechdata[i])
                self.setContentData(DictDataManager(mydict))
        self.formurl = self.context.absolute_url() + '/mechanikform'

    @api.action('Suchen')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.',
                                         request=self.request, type="error")
            return
        params = urllib.urlencode(data)
        url = self.context.absolute_url() + '/mechanikergebnisse?' + params         
        return self.response.redirect(url)
 
    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)

class MechanikErgebnisse(api.Page):
    api.context(Interface)

    def calc_sortindex(self, obj):
        sortindex = 0
        if obj.abrieb:
            if obj.abrieb != 'x':
                sortindex += int(obj.abrieb) * bgfaktor['abrieb'] * self.abrieb
        if obj.schnittcoup:
            if obj.schnittcoup != 'x':
                sortindex += int(obj.schnittcoup) * bgfaktor['schnittcoup'] * self.schnittcoup
        if obj.riss:
            if obj.riss != 'x':
                sortindex += int(obj.riss) * bgfaktor['riss'] * self.riss
        if obj.stick:
            if obj.stick != 'x':
                sortindex += int(obj.stick) * bgfaktor['stick'] * self.stick
        if obj.schnittiso:
            if obj.schnittiso != 'x':
                sortindex += schnittiso[obj.schnittiso] * bgfaktor['schnittiso'] * self.schnittiso
        if obj.stoss:
            if obj.stoss == 'P':
                sortindex += 2 * bgfaktor['stoss'] * self.stoss
        return sortindex

    def update(self):
        self.abrieb = 1
        self.schnittcoup = 1
        self.riss = 1
        self.stick = 1
        self.schnittiso = 1
        self.stoss = 1
        pcat = getToolByName(self.context, 'portal_catalog')
        query = {}
        sortorder = False
        self.sf = "checked"
        self.st = ""
        if self.request.get('sortierung'):
            if self.request.get('sortierung') == "True":
                sortorder = True
                self.sf = ""
                self.st = "checked"

        self.resultform = []
        query['portal_type'] = u"Schutzhandschuh"
        query['Mechanik'] = True
        query['Chemiekalienschutz'] = False

        if self.request.get('abrieb'):
            self.resultform.append({'name':'abrieb', 'value':self.request.get('abrieb')}) 
            if self.request.get('abrieb') != u'nicht_relevant':
                query['Abrieb'] = self.request.get('abrieb')
                self.abrieb = int(self.request.get('abrieb'))

        if self.request.get('schnittcoup'):
            self.resultform.append({'name':'schnittcoup', 'value':self.request.get('schnittcoup')}) 
            if self.request.get('schnittcoup') != u'nicht_relevant':
                query['Schnittcoup'] = self.request.get('schnittcoup')
                self.schnittiso = int(self.request.get('schnittcoup'))

        if self.request.get('riss'):
            self.resultform.append({'name':'riss', 'value':self.request.get('riss')}) 
            if self.request.get('riss') != u'nicht_relevant':
                query['Rissfestigkeit'] = self.request.get('riss')
                self.riss = int(self.request.get('riss'))

        if self.request.get('stick'):
            self.resultform.append({'name':'stick', 'value':self.request.get('stick')}) 
            if self.request.get('stick') != u'nicht_relevant':
                query['Durchstich'] = self.request.get('stick')
                self.stick = int(self.request.get('stick'))

        if self.request.get('schnittiso'):
            self.resultform.append({'name':'schnittiso', 'value':self.request.get('schnittiso')}) 
            if self.request.get('schnittiso') != u'nicht_relevant':
                query['Schnittiso'] = self.request.get('schnittiso')
                self.schnittiso = schnittiso[self.request.get('schnittiso')]
        if self.request.get('stoss'):
            if ast.literal_eval(self.request.get('stoss')):
                self.resultform.append({'name':'stoss', 'value':self.request.get('stoss')}) 
                query['Stossfestigkeit'] = ast.literal_eval(self.request.get('stoss'))
                self.stoss = 2

        print query
        brains = pcat.searchResults(query)
        print len(brains)
        self.produktlist = []
        for i in brains:
            sortvalue = 0
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['sortindex'] = self.calc_sortindex(obj)
            entry['ergebnisse'] = []
            entry['ergebnisse'].append((u'Abriebfestigkeit', obj.abrieb))
            entry['ergebnisse'].append((u'Schnittfestigkeit (Coup)', obj.schnittcoup))
            entry['ergebnisse'].append((u'Weiterreißfestigkeit', obj.riss))
            entry['ergebnisse'].append((u'Durchstichfestigkeit', obj.stick))
            entry['ergebnisse'].append((u'Schnittfestigkeit (ISO)', obj.schnittiso))
            entry['ergebnisse'].append((u'Stossfestigkeit', obj.stoss))
            self.produktlist.append(entry)
        self.produktlist = sorted(self.produktlist, key=itemgetter('sortindex'), reverse=sortorder)
        if not self.produktlist:
            ploneapi.portal.show_message(message=u'Für die von Ihnen angegebenen Suchkriterien konnte kein Produkt\
                                                  gefunden werden. Bitte überprüfen Sie Ihre Suchkriterien.',
                                         request=self.request, type="warn")
            url = self.context.absolute_url() + '/mechanikform'
            return self.response.redirect(url)
        self.formurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/@@compareproducts'
