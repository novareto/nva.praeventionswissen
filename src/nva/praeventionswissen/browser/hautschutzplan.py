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
from nva.praeventionswissen.interfaces import IHautschutzplan 
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

api.templatedir('templates')

class Hautschutzplan(api.Form):
    api.context(Interface)
    fields = api.Fields(IHautschutzplan)

    ignoreRequest = False
    ignoreContent = False

    def formatMittel(self, products):
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(UID=products)
        mittel = []
        for i in brains:
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            hersteller = ''
            herstellerurl = ''
            if obj.hersteller:
                if obj.hersteller.to_object:
                    hersteller = obj.hersteller.to_object.title
                    herstellerurl = obj.hersteller.to_object.absolute_url()
            entry['hersteller'] = hersteller
            entry['herstellerurl'] = herstellerurl
            mittel.append(entry)
        return mittel

    def update(self):
        self.formtitle = u"Hand- und Hautschutzplan"
        self.formdescription = u""
        sessiondata = getSessionData(self.request)
        if sessiondata:
            if sessiondata.get('hautschutzplan'):
                self.setContentData(DictDataManager(sessiondata.get('hautschutzplan')))
        self.taetigkeit = ''
        self.beschreibung = ''
        if sessiondata.get('taetigkeit'):
            taetigkeit = sessiondata.get('taetigkeit')
            self.taetigkeit = taetigkeit.get('title')
            self.beschreibung = taetigkeit.get('description')
        self.hautschutz = self.formatMittel(sessiondata.get('hautschutz'))
        self.schutzhandschuhe = self.formatMittel(sessiondata.get('schutzhandschuhe'))
        self.desinfektion = self.formatMittel(sessiondata.get('desinfektion'))
        self.hautreinigung = self.formatMittel(sessiondata.get('hautreinigung'))
        self.hautpflege = self.formatMittel(sessiondata.get('hautpflege'))
        self.formurl = self.context.absolute_url() + '/hautschutzplan'

    @api.action('Daten Speichern')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        sessiondata['hautschutzplan'] = data
        sessionid = setSessionData(self.request, sessiondata)
        url = self.context.absolute_url() + '/hautschutzplan'     
        return self.response.redirect(url)
 
    @api.action('PDF-Dokument ansehen')
    def handel_cancel(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.',
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        sessiondata['hautschutzplan'] = data
        sessionid = setSessionData(self.request, sessiondata)
        url = self.context.absolute_url() + '/@@pdfview'
        return self.redirect(url)
