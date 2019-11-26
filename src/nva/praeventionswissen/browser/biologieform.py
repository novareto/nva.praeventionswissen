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
from nva.praeventionswissen.interfaces import ITaetigkeitform, IBiologieform
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

api.templatedir('templates')

class ChemieBiologieValidator(object):

    def __init__(self, form, fields):
        self.form = form
        self.fields = fields
        self.errors = []

    def validate(self, data):
        if not data.get('gefahrstoffe') and data.get('biologie') == u'keine':
            self.errors.append(Error(
                u'Bitte wählen Sie Gefahrstoffe aus oder geben Sie an, mit welchen biologischen Gefährdungen\
                die Tätigkeit verbunden ist.',
                identifier="form.field.gefahrstoffe",
            ))
        return self.errors


class BiologieForm(api.Form):
    api.context(Interface)
    fields = api.Fields(IBiologieform)
    fields['gefahrstoffe'].allowOrdering = False
    #dataValidators = [ChemieBiologieValidator]

    #Weitere Gefährdungen bei dieser Tätigkeit

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        self.panelclassone = 'panel-collapse collapse'
        self.panelclasstwo = 'panel-collapse collapse'
        if self.request.get('form.field.gefahrstoffe.add') or self.request.get('form.field.gefahrstoffe.remove'):
            self.panelclassone = 'panel-collapse collapse in'
        self.formtitle = u"Tätigkeit mit biologischen Gefährdungen"
        self.formdescription = u""
        sessiondata = getSessionData(self.request)
        if sessiondata:
            if sessiondata.get('taetigkeit'):
                taetigkeit = sessiondata.get('taetigkeit')
                self.formtitle = taetigkeit.get('title')
                self.formdescription = taetigkeit.get('description')
            if sessiondata.get('cbsuche'):
                formdata = sessiondata.get('cbsuche')
                if formdata.get('gefahrstoffe') or formdata.get('thermisch') or formdata.get('mechanik'):
                    self.panelclassone = 'panel-collapse collapse in'
                if formdata.get('handschuhlaenge') != u'alle' or formdata.get('materialdicke') != 'alle':
                    self.panelclasstwo = 'panel-collapse collapse in'
                self.setContentData(DictDataManager(sessiondata.get('cbsuche')))
        self.formurl = self.context.absolute_url() + '/biologieform'

    @api.action('Weiter')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        sessiondata['cbsuche'] = data
        sessiondata['searchform'] = 'biologieform'
        sessionid = setSessionData(self.request, sessiondata)
        url = self.context.absolute_url() + '/chemieergebnisse'     
        return self.response.redirect(url)
 
    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)


class BiologieErgebnisse(api.Page):
    api.context(Interface)

    def update(self):
        sessiondata = getSessionData(self.request)
        chemiedata = sessiondata.get('chemiesuche')
        pcat = getToolByName(self.context, 'portal_catalog')
        gefahrstoffe = chemiedata.get('gefahrstoffe')
        self.resultform = []
        query = {}
        query['portal_type'] = u"Schutzhandschuh"
        query['Gefahrstoffe'] = gefahrstoffe
        biogefahr = chemiedata.get('biologie')
        if biogefahr:
            self.resultform.append({'name':'biologie', 'value':biogefahr})
            if biogefahr == 'bakterienpilze':
                query['Biologisch'] = True
            if biogefahr == 'bakterienpilzeviren':
                query['Viren'] = True
        if chemiedata.get('mechanik'):
            self.resultform.append({'name':'mechanik', 'value':chemiedata.get('mechanik')})
            query['Mechanik'] = True
        if chemiedata.get('thermisch'):
            self.resultform.append({'name':'thermisch', 'value':chemiedata.get('thermisch')})
            query['Thermisch'] = True
        if chemiedata.get('materialdicke') != u'alle':
            self.resultform.append({'name':'materialdicke', 'value':chemiedata.get('materialdicke')})
            query['Tastsinn'] = chemiedata.get('materialdicke')
        if chemiedata.get('handschuhlaenge') != u'alle':
            self.resultform.append({'name':'handschuhlaenge', 'value':chemiedata.get('handschuhlaenge')})
            query['Stulpenlaenge'] = chemiedata.get('handschuhlaenge')
        brains = pcat.searchResults(query)
        sortgefahrstoff = self.request.get('sortgefahrstoff')
        produktlist = []
        for i in brains:
            sortvalue = 0
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['gefahrstoffe'] = []
            obj_gefahrstoffe = []
            for k in obj.gefahrstoffschutz:
                obj_gefahrstoffe.append(k.get('gefahrstoff'))
                if k.get('gefahrstoff') in gefahrstoffe:
                    stoff = {}
                    stoff['gefahrstoff'] = collectGefahrstoffe(self.context).getTerm(k.get('gefahrstoff')).title
                    stoff['gefahrstoffurl'] = k.get('gefahrstoff')
                    stoff['durchbruch'] = durchbruchzeit.getTerm(k.get('zeit')).title
                    zeit = k.get('zeit')
                    if zeit == u'spritzschutz' or zeit == 'auswahl':
                        zeit = 5
                    else:
                        zeit = int(zeit)
                    if not sortgefahrstoff:
                        if sortvalue == 0:
                            sortvalue = zeit
                        if 0 < zeit <= sortvalue:
                            sortvalue =zeit
                    else:
                        if sortgefahrstoff == k.get('gefahrstoff'):
                            sortvalue = zeit
                    entry['gefahrstoffe'].append(stoff)
            if set(gefahrstoffe).issubset(obj_gefahrstoffe):
                entry['sortvalue'] = sortvalue
                produktlist.append(entry)
        self.produktlist = sorted(produktlist, key=itemgetter('sortvalue'), reverse=True)
        if not self.produktlist:
            ploneapi.portal.show_message(message=u'Für Ihre Gefahrstoffauswahl und die von Ihnen angegebenen Suchkriterien konnte kein Produkt\
                                                  gefunden werden. Bitte prüfen Sie die ausgewählten Gefahrstoffe oder reduzieren Sie die sonstigen\
                                                  Suchkriterien.',
                                         request=self.request, type="error")
            url = self.context.absolute_url() + '/chemieform'
            return self.response.redirect(url)        
        self.gefahrstoffe = gefahrstoffe
