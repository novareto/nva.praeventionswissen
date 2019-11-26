# -*- coding: utf-8 -*-
from zope.interface import Interface
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
from plone.dexterity.content import Container
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from uvc.api import api
from nva.praeventionswissen.vocabularies import durchbruchzeit, material, ausfuehrung, profilierung
from nva.praeventionswissen.vocabularies import pruefung374alt, pruefung374neu, chemikalienpruefung, pruefung375_5_2016
from nva.praeventionswissen.vocabularies import pruefung_weitere_chemie, allergene_vocab
from nva.praeventionswissen.vocabularies import pruefung_normen_mechanik, cecatvalues
from nva.praeventionswissen.vocabularies import collectGefahrstoffe, durchbruchzeit
from nva.praeventionswissen.vocabularies import symboldict
from plone import api as ploneapi

api.templatedir('templates')

class SchutzhandschuhView(api.View):
    api.context(Interface)

    def checkHHPlan(self):
        handschuh = self.context.UID()
        sessiondata = getSessionData(self.request)
        schutzhandschuhe = sessiondata.get('schutzhandschuhe')
        if schutzhandschuhe:
            if handschuh in schutzhandschuhe:
                return True
        return False

    def isChemiekalienschutz(self, obj):
        if obj.norm374_2003:
	    if 'chemikalien_einfach' in obj.norm374_2003:
	        return True
	    if 'chemikalien_spez' in obj.norm374_2003:
	        return True
        if obj.norm374_2016:
	    if obj.norm374_2016.startswith('Typ'):
	        return True
        return False

    def isMechanik(self, obj):
        if u'din_en_388_alt' in obj.mechanik:
            return True
        if u'din_en_388_2016' in obj.mechanik:
            return True
        return False

    def getTestTable388(self):
        testtable = '<table class="table table-striped"><thead><th>Testgegenstand</th><th>Wertebereich</th><th>Testergebnis</th></thead>'
        testtable += '<tbody>'
        self.typ388 = 'EN 388'
        if self.context.mechanik:
            stosstest = ''
            if self.context.stoss:
                stosstest = self.context.stoss
            testlist = self.context.mechanik
            if 'din_en_388_alt' in testlist and not 'din_en_388_2016' in testlist:
                testtable += '<tr><td>Abriebfestigkeit</td><td>1 (gering) bis 4 (hoch)</td><td>%s</td></tr>' % self.context.abrieb.upper()
                testtable += '<tr><td>Schnittfestigkeit (Coup-Test)</td><td>1 (gering) bis 5 (hoch)</td><td>%s</td></tr>' % self.context.schnittcoup.upper()
                testtable += '<tr><td>Weiterreissfestigkeit</td><td>1 (gering) bis 4 (hoch)</td><td>%s</td></tr>' % self.context.riss.upper()
                testtable += '<tr><td>Durchstichfestigkeit</td><td>1 (gering) bis 4 (hoch)</td><td>%s</td></tr>' % self.context.stick.upper()
            if 'din_en_388_2016' in testlist:
                testtable += '<tr><td>Abriebfestigkeit</td><td>1 (gering) bis 4 (hoch)</td><td>%s</td></tr>' % self.context.abrieb.upper()
                testtable += '<tr><td>Schnittfestigkeit (Coup-Test)</td><td>1 (gering) bis 5 (hoch)</td><td>%s</td></tr>' % self.context.schnittcoup.upper()
                testtable += '<tr><td>Weiterreissfestigkeit</td><td>1 (gering) bis 4 (hoch)</td><td>%s</td></tr>' % self.context.riss.upper()
                testtable += '<tr><td>Durchstichfestigkeit</td><td>1 (gering) bis 4 (hoch)</td><td>%s</td></tr>' % self.context.stick.upper()
                testtable += '<tr><td>Schnittfestigkeit (ISO-Test)</td><td>A (gering) bis F (hoch)</td><td>%s</td></tr>' % self.context.schnittiso
                testtable += '<tr><td>Stossfestigkeit</td><td>P (vorhanden)</td><td>%s</td></tr>' % stosstest
        
        testtable += '</tbody></table>'
        testtable += '<p style="font-size:80%">Buchstabe <b>X</b> steht für "nicht geprüft" oder "Test nicht anwendbar".</p>'
        return testtable

    def getFolderImages(self):
        folderimages = []
        fc = self.context.getFolderContents()
        for i in fc:
            if i.portal_type == 'Image':
                obj = i.getObject()
                folderimages.append('%s/@@images/image' %obj.absolute_url())
        return folderimages

    def update(self):
        self.hhplan = self.checkHHPlan()
        self.titleimg = ''
        self.images = []
        if self.context.bild:
            self.titleimg = '%s/@@images/bild' % self.context.absolute_url()
        if self.titleimg:
            self.images = [self.titleimg]
        if self.context.__class__ == Container:
            self.images += self.getFolderImages()
        self.beschreibung = ''
        if self.context.text:
            self.beschreibung = self.context.text.output
        self.hersteller = ''
        self.hersteller_url = ''
        if self.context.hersteller:
            self.hersteller = self.context.hersteller.to_object.title
            self.hersteller_url = self.context.hersteller.to_object.absolute_url()
        self.aussenmaterial = ''
        if self.context.material_aussen:
            self.aussenmaterial = ', '.join([material.getTerm(i).title for i in self.context.material_aussen])
        self.innenmaterial = ''
        if self.context.material_innen:
            self.innenmaterial = ', '.join([material.getTerm(i).title for i in self.context.material_innen])
        self.innenausfuehrung = ''
        if self.context.innen:
            self.innenausfuehrung = ', '.join([ausfuehrung.getTerm(i).token for i in self.context.innen])
        self.profilierung = ''
        if self.context.profilierung:
            self.profilierung = ', '.join([profilierung.getTerm(i).title for i in self.context.profilierung])

        self.symbolurl = ploneapi.portal.get().absolute_url()+'/++resource++nva.praeventionswissen/'
        self.symbolliste = []
        if self.context.norm374_2003:
            for i in self.context.norm374_2003:
                symbol = symboldict.get(i)
                if symbol and symbol not in self.symbolliste:
                    self.symbolliste.append(symbol)
        if self.context.norm374_2016:
            symbol = symboldict.get(self.context.norm374_2016)
            if symbol and symbol not in self.symbolliste:
                self.symbolliste.append(symbol)
        if self.context.norm374_5:
            symbol = symboldict.get(self.context.norm374_5)
            if symbol and symbol not in self.symbolliste:
                self.symbolliste.append(symbol)
        if self.context.mechanik:
            for i in self.context.mechanik:
                symbol = symboldict.get(i)
                if symbol and symbol not in self.symbolliste:
                    self.symbolliste.append(symbol)

        self.schichtstaerke = ''
        if self.context.schichtstaerke_min:
            self.schichtstaerke = str("%.2f" % self.context.schichtstaerke_min).replace('.', ',') + ' mm'
        if self.context.schichtstaerke_max:
            self.schichtstaerke = self.schichtstaerke + ' bis ' + str("%.2f" % self.context.schichtstaerke_max).replace('.', ',') + ' mm'

        self.gesamtlaenge = ''
        if self.context.gesamtlange_von:
            self.gesamtlaenge = str(self.context.gesamtlange_von) + ' mm'
        if self.context.gesamtlange_bis:
            self.gesamtlaenge = self.gesamtlaenge + ' bis ' + str(self.context.gesamtlange_bis) + ' mm'


        self.symbol374_2003_C = ''
        self.symbol374_2003_B = ''
        chemikalienliste = [chemikalienpruefung.getTerm(i).token for i in self.context.chemikalienliste if i != 'auswahl']
        self.chemikalienliste = ''.join(chemikalienliste)
        if self.context.norm374_2003:
            testlist = self.context.norm374_2003
            if u'chemikalien_einfach' in testlist and u'chemikalien_spez' in testlist:
                self.symbol374_2003_C = symboldict.get(u'chemikalien_spez')
            elif u'chemikalien_einfach' in testlist:
                self.symbol374_2003_C = symboldict.get(u'chemikalien_einfach')
            elif u'chemikalien_spez' in testlist:
                self.symbol374_2003_C = symboldict.get(u'chemikalien_spez')
            if u'bakt_pilze' in testlist:
                self.symbol374_2003_B = symboldict.get(u'bakt_pilze')

        self.symbol374_2016_C = ''
        self.typ374 = ''
        self.symbol374_2016_B = ''
        self.virus = ''
        if self.context.norm374_2016:
            if self.context.norm374_2016 != u'keine':
                self.typ374 = pruefung374neu.getTerm(self.context.norm374_2016).title
                self.symbol374_2016_C = symboldict.get(self.context.norm374_2016)
        if self.context.norm374_5:
            if self.context.norm374_5 != u'keine':
                self.virus = ''
                if self.context.norm374_5 == 'bakterienpilzeviren':
                    self.virus = 'VIRUS'
                self.symbol374_2016_B = symboldict.get(self.context.norm374_5)

        self.symbol388 = ''
        self.typ388 = 'EN 388'
        self.results388 = ''
        self.testtable = ''
        if self.context.mechanik:
            testlist = self.context.mechanik
            if 'din_en_388_alt' in testlist or 'din_en_388_2016' in testlist:
                self.testtable = self.getTestTable388()
	    if 'din_en_388_alt' in testlist and 'din_en_388_2016' in testlist:
	        self.symbol388 = symboldict.get('din_en_388_2016')
	    if 'din_en_388_alt' in testlist:
                self.symbol388 = symboldict.get('din_en_388_alt')
	        self.results388+=self.context.abrieb.upper()
	        self.results388+=self.context.schnittcoup.upper()
	        self.results388+=self.context.riss.upper()
	        self.results388+=self.context.stick.upper()
	    if 'din_en_388_2016' in testlist:
                self.symbol388 = symboldict.get('din_en_388_2016')
	        self.typ388 = 'EN 388:2016'
	        self.results388 = ''
	        self.results388+=self.context.abrieb.upper()
	        self.results388+=self.context.schnittcoup.upper()
	        self.results388+=self.context.riss.upper()
	        self.results388+=self.context.stick.upper()
                if self.context.schnittiso:
	            self.results388+=self.context.schnittiso
                if self.context.stoss:
	            self.results388+=self.context.stoss

        self.editable = False
        if not ploneapi.user.is_anonymous():
            myuser = ploneapi.user.get_current()
            if ploneapi.user.has_permission('Modify portal content', user=myuser):
                self.editable = True


        self.gefahrstoffschutz = []
        if self.context.gefahrstoffschutz:
            for i in self.context.gefahrstoffschutz:
                entry = {}
                try:
                    entry['gsid'] = i.get('gefahrstoff')
                    entry['gefahrstoff'] = collectGefahrstoffe(self.context).getTerm(i.get('gefahrstoff')).title
                    entry['zeit'] = durchbruchzeit.getTerm(i.get('zeit')).title
                    self.gefahrstoffschutz.append(entry)
                except:
                    pass
        self.gefahrstoffschutz = sorted(self.gefahrstoffschutz, key=itemgetter('gefahrstoff'))

        self.addurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/schutzhandschuhplan?produkt=%s' % self.context.UID()

        self.tabchemie = 'tab-pane active'
        self.tabmechanik = 'tab-pane'
        print self.isChemiekalienschutz(self.context)
        print self.isMechanik(self.context)

        if self.isChemiekalienschutz(self.context):
            self.tabchemie = 'tab-pane active'
            self.tabmechanik = ''
            if self.isMechanik(self.context):
                self.tabmechanik = 'tab-pane'
        if not self.isChemiekalienschutz(self.context) and self.isMechanik(self.context):
            self.tabchemie = ''
            self.tabmechanik = 'tab-pane active'

class SchutzhandschuhPlan(api.View):
    api.context(Interface)

    def render(self):
        handschuh = self.request.get('produkt')
        sessiondata = getSessionData(self.request)
        schutzhandschuhe = sessiondata.get('schutzhandschuhe')
        if schutzhandschuhe:
            if handschuh not in schutzhandschuhe:
                schutzhandschuhe.append(handschuh)
        else:
            schutzhandschuhe = [handschuh]
        sessiondata['schutzhandschuhe'] = schutzhandschuhe
        sessiondata['hhplan'] = True
        dataid = setSessionData(self.request, sessiondata)
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/@@schutzhandschuhe'
        return self.response.redirect(url)
            
class Schutzhandschuhe(api.Page):
    api.context(Interface)

    def update(self):
        pcat = getToolByName(self.context, 'portal_catalog')
        sessiondata = getSessionData(self.request)
        schutzhandschuhe = pcat(UID = sessiondata.get('schutzhandschuhe'))
        self.schutzhandschuhe = []
        for i in schutzhandschuhe:
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
            self.schutzhandschuhe.append(entry)
