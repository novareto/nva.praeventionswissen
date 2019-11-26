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
from nva.praeventionswissen.interfaces import ITaetigkeitform, IChemieform
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe
from Products.statusmessages.interfaces import IStatusMessage


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


class ChemieForm(api.Form):
    api.context(Interface)
    fields = api.Fields(IChemieform)
    fields['gefahrstoffe'].allowOrdering = False
    dataValidators = [ChemieBiologieValidator]

    #Weitere Gefährdungen bei dieser Tätigkeit

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        self.panelclassone = 'panel-collapse collapse'
        self.panelclasstwo = 'panel-collapse collapse'
        self.formtitle = u"Tätigkeit mit chemischen Gefährdungen"
        self.formdescription = u""
        sessiondata = getSessionData(self.request)
        if sessiondata:
            if sessiondata.get('taetigkeit'):
                taetigkeit = sessiondata.get('taetigkeit')
                self.formtitle = taetigkeit.get('title')
                self.formdescription = taetigkeit.get('description')
            if sessiondata.get('cbsuche'):
                formdata = sessiondata.get('cbsuche')
                if formdata.get('biologie') != u'keine':
                    self.panelclassone = 'panel-collapse collapse in'
                if formdata.get('handschuhlaenge') != u'alle' or formdata.get('materialdicke') != 'alle':
                    self.panelclasstwo = 'panel-collapse collapse in'
                self.setContentData(DictDataManager(sessiondata.get('cbsuche')))
        self.formurl = self.context.absolute_url() + '/chemieform'

    @api.action('Weiter')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        sessiondata = getSessionData(self.request)
        sessiondata['cbsuche'] = data
        sessiondata['searchform'] = 'chemieform'
        sessionid = setSessionData(self.request, sessiondata)
        url = self.context.absolute_url() + '/chemieergebnisse'     
        return self.response.redirect(url)
 
    @api.action('Abbrechen')
    def handel_cancel(self):
        url = ploneapi.portal.get().absolute_url()
        return self.redirect(url)

class ActionWidget(ActionWidget):

    grok.adapts(
        interfaces.IAction,
        interfaces.IFieldExtractionValueSetting,
        IThemeSpecific)

    def htmlClass(self):
        return 'btn btn-primary'

class ChemieErgebnisse(api.Page):
    api.context(Interface)

    def update(self):
        sessiondata = getSessionData(self.request)
        data = sessiondata.get('cbsuche')
        pcat = getToolByName(self.context, 'portal_catalog')
        self.resultform = []
        query = {}
        query['portal_type'] = u"Schutzhandschuh"
        gefahrstoffe = data.get('gefahrstoffe')
        if gefahrstoffe:
            query['Gefahrstoffe'] = gefahrstoffe
        biogefahr = data.get('biologie')
        if biogefahr and biogefahr != 'keine':
            self.resultform.append({'name':'biologie', 'value':biogefahr})
            query['Biogefahr'] = biogefahr
        if data.get('mechanik'):
            self.resultform.append({'name':'mechanik', 'value':data.get('mechanik')})
            query['Mechanik'] = True
        #if data.get('thermisch'):
        #    self.resultform.append({'name':'thermisch', 'value':data.get('thermisch')})
        #    query['Thermisch'] = True
        if data.get('materialdicke') != u'alle':
            self.resultform.append({'name':'materialdicke', 'value':data.get('materialdicke')})
            query['Tastsinn'] = data.get('materialdicke')
        if data.get('handschuhlaenge') != u'alle':
            self.resultform.append({'name':'handschuhlaenge', 'value':data.get('handschuhlaenge')})
            query['Stulpenlaenge'] = data.get('handschuhlaenge')
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
        self.gefahrstoffe = gefahrstoffe
        if not self.produktlist:
            ploneapi.portal.show_message(message=u'Für Ihre Suchkriterien konnte leider kein Produkt gefunden werden.',
                                         request=self.request, type="info")
            url = self.context.absolute_url() + '/' + sessiondata.get('searchform')
            return self.response.redirect(url)
        

class CompareProducts(api.Page):
    api.context(Interface)


    def formatMM(self, value):
        if value:
            value = str(value).replace('.', ',')
            value = value + ' mm'
            return value
        return 'k.A.'

    def formatInnen(self, value):
        if value:
            value = value[0]
            value = ausfuehrung.getTerm(value).token
            return value 
        return ''       

    def formatMaterial(self, value):
        if value:
            value = value[0]
            value = material.getTerm(value).title
            return value
        return ''

    def formatProfilierung(self, value):
        if value:
            value = value[0]
            value = profilierung.getTerm(value).title
            return value
        return ''

    def formatList(self, value):
        if value:
            format = u'<ul>'
            for i in value:
                format += '<li>%s</li>' %i
            format += '</ul>'
            return format
        return ''

    def formatText(self,value):
        if value:
            if value.output:
                heading = u"""<h1>Herstellerangaben</h1>
                              <p class="documentDescription">Bitte beachten Sie, dass 
                              die folgenden Informationen auf Herstellerangaben basieren.</p>"""
                output = heading + value.output
                return output
        return ''

    def update(self):
        if self.request.get('choose'):
             sessiondata = getSessionData(self.request)
             handschuhe = self.request.get('produkt')
             if not isinstance(handschuhe, list):
                 handschuhe = [handschuhe]
             sessiondata['schutzhandschuhe'] = handschuhe
             sessiondata['hhplan'] = True
             dataid = setSessionData(self.request, sessiondata)
             url = self.context.absolute_url() + '/@@schutzhandschuhe'
             return self.response.redirect(url)
        vergleich = []
        title = [u'Produktname',]
        bild = [u'Produktbild']
        material_aussen = [u'Material außen',]
        material_innen = [u'Material innen',]
        innen = [u'Innenausführung',]
        profilierung = [u'Profilierung']
        schichtstaerke= [u'Schichtstärke min/max',]
        gesamtlaenge = [u'Gesamtlänge von-bis',]
        allergene = [u'Allergene',]
        abrieb = [u'Abriebfestigkeit',]
        schnitt = [u'Schnittfestigkeit (Coup-Test)',]
        riss = [u'Weiterreißfestigkeit',]
        stick = [u'Durchstichfestigkeit',]
        schnittiso = [u'Schnittfestigkeit (ISO-Test)']
        stoss = [u'Schutz gegen Stoßeinwirkung',]
        text = [u'<b>Produkt auswählen</b>',] 
        uids = self.request.get('produkt')
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(UID = uids)
        for i in brains:
            obj = i.getObject()
            title.append(obj.title)
            imgtag = '<img class="img-responsive" src="%s/@@images/bild/thumb">' %obj.absolute_url()
            bild.append(imgtag)
            material_aussen.append(self.formatMaterial(obj.material_aussen))
            material_innen.append(self.formatMaterial(obj.material_innen))
            innen.append(self.formatInnen(obj.innen))
            profilierung.append(self.formatProfilierung(obj.profilierung))
            myschichtstaerke = "%s / %s" %(self.formatMM(obj.schichtstaerke_min),
                                         self.formatMM(obj.schichtstaerke_max))    
            schichtstaerke.append(myschichtstaerke)
            mygesamtlaenge = "%s - %s" %(self.formatMM(obj.gesamtlange_von),
                                       self.formatMM(obj.gesamtlange_bis))
            gesamtlaenge.append(mygesamtlaenge)
            allergene.append(self.formatList(obj.allergene))
            abrieb.append(obj.abrieb)
            schnitt.append(obj.schnittcoup)
            riss.append(obj.riss)
            stick.append(obj.stick)
            schnittiso.append(obj.schnittiso)
            stoss.append(obj.stoss)
            text.append('<input class="form-control" type="checkbox" name="produkt" value="%s">' %obj.UID())
        vergleich.append(title)
        vergleich.append(bild)
        vergleich.append(material_aussen)
        vergleich.append(material_innen)
        vergleich.append(innen)
        vergleich.append(profilierung)
        vergleich.append(schichtstaerke)
        vergleich.append(gesamtlaenge)
        vergleich.append(allergene)
        vergleich.append(abrieb)
        vergleich.append(schnitt)
        vergleich.append(riss)
        vergleich.append(stick)
        vergleich.append(schnittiso)
        vergleich.append(stoss)
        vergleich.append(text)
        self.vergleich = vergleich
        self.formurl = self.context.absolute_url() + '/compareproducts'
