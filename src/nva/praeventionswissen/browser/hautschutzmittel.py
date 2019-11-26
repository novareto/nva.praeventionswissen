# -*- coding: utf-8 -*-
from zope.interface import Interface
from uvc.api import api
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.vocabularies import collectGefahrstoffe, hskategorieVocabulary
from nva.praeventionswissen.hautschutzmittel import anwendungVocabulary, zusatzVocabulary
from edi.restreader.restaccess import getExternalGefahrstoff
from Products.CMFCore.utils import getToolByName
from plone import api as ploneapi

api.templatedir('templates')

class HautschutzmittelView(api.View):
    api.context(Interface)

    def checkHHPlan(self):
        hautschutzmittel = self.context.UID()
        sessiondata = getSessionData(self.request)
        storedhsmittel = sessiondata.get('hautschutz')
        if storedhsmittel:
            if hautschutzmittel in storedhsmittel:
                return True
        return False

    def update(self):
        self.hhplan = self.checkHHPlan()
        self.titleimg = ''
        self.images = []
        if self.context.bild:
            self.titleimg = '%s/@@images/bild' % self.context.absolute_url()
        if self.titleimg:
            self.images = [self.titleimg]
        self.beschreibung = ''
        if self.context.bemerkungen:
            self.beschreibung = self.context.bemerkungen
        self.hersteller = ''
        self.hersteller_url = ''
        if self.context.hersteller:
            self.hersteller = self.context.hersteller.to_object.title
            self.hersteller_url = self.context.hersteller.to_object.absolute_url()

        self.gefaehrdung = ''
        if self.context.gefaehrdung:
            self.gefaehrdung = ', '.join([anwendungVocabulary.getTerm(i).token for i in self.context.gefaehrdung])

        self.schutzfunktion = ''
        if self.context.kategorie:
            self.schutzfunktion = ', '.join([hskategorieVocabulary.getTerm(i).title for i in self.context.kategorie])
        
        self.inhaltsstoffe = ''
        if self.context.inhaltsstoffe:
            self.inhaltsstoffe = ', '.join(self.context.inhaltsstoffe)

        self.konservierungsmittel = ''
        if self.context.konservierungsmittel:
            self.konservierungsmittel = ', '.join(self.context.konservierungsmittel)

        self.duftstoffe = ''
        if self.context.duftstoffe:
            self.duftstoffe = ', '.join(self.context.duftstoffe)

        self.addurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/hautschutzmittelplan?produkt=%s' % self.context.UID()


class HautschutzmittelPlan(api.View):
    api.context(Interface)

    def render(self):
        hautschutzmittel = self.request.get('produkt')
        sessiondata = getSessionData(self.request)
        storedhsmittel = sessiondata.get('hautschutz')
        if storedhsmittel:
            if hautschutzmittel not in storedhsmittel:
                storedhsmittel.append(hautschutzmittel)
        else:
            storedhsmittel = [hautschutzmittel]
        sessiondata['hautschutz'] = storedhsmittel
        sessiondata['hhplan'] = True
        dataid = setSessionData(self.request, sessiondata)
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/@@resulthautschutz'
        return self.response.redirect(url)


class Hautschutzmittel(api.Page):
    api.context(Interface)

    def update(self):
        sessiondata = getSessionData(self.request)
        self.hautschutzmittel = []
        pcat = getToolByName(self.context, 'portal_catalog')
        if sessiondata:
            chemie = sessiondata.get('cbsuche')
            gefahrstoffe = chemie.get('gefahrstoffe')
            if gefahrstoffe == [u'auswahl']:
                gefahrstoffe = []
            kategorien = []
            if gefahrstoffe:
                for i in gefahrstoffe:
                    if i.startswith('http://emissionsarme'):
                        jsonobj = getExternalGefahrstoff(i)
                        if jsonobj.get('hskategorie') not in kategorien:
                            kategorien.append(jsonobj.get('hskategorie'))
                    else:
                        pcat = getToolByName(self.context, 'portal_catalog')
                        objid = collectGefahrstoffe(self.context).getTerm(i).token
                        brains = pcat(portal_type = "Gefahrstoff", id = objid)
                        if brains:
                            gefahrstoff = brains[0].getObject()
                            if gefahrstoff.hskategorie not in kategorien:
                                kategorien.append(gefahrstoff.hskategorie)
            kat = 'id_wechselnd'
            if kategorien:
                if len(kategorien) > 1:
                    kat = 'id_wechselnd'
                else:
                    kat = kategorien[0]
            brains = pcat(portal_type="Hautschutzmittel", Hautschutzmittel=kat)

            for i in brains:
                entry = {}
                obj = i.getObject()
                entry['title'] = obj.title
                entry['url'] = obj.absolute_url()
                entry['uid'] = obj.UID()
                entry['image'] = ''
                if obj.bild:
                    entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
                entry['cat'] = hskategorieVocabulary.getTerm(obj.kategorie[0]).title
                hersteller = ''
                herstellerurl = ''
                if obj.hersteller:
                    if obj.hersteller.to_object:
                        hersteller = obj.hersteller.to_object.title
                        herstellerurl = obj.hersteller.to_object.absolute_url()
                entry['hersteller'] = hersteller
                entry['herstellerurl'] = herstellerurl
                self.hautschutzmittel.append(entry)


class ResultHautschutz(api.Page):
    api.context(Interface)

    def update(self):
        self.hautschutzmittel = []
        sessiondata = getSessionData(self.request)
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(UID = sessiondata['hautschutz'])
        for i in brains:
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = ''
            if obj.bild:
                entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['cat'] = hskategorieVocabulary.getTerm(obj.kategorie[0]).title
            hersteller = ''
            herstellerurl = ''
            if obj.hersteller:
                if obj.hersteller.to_object:
                    hersteller = obj.hersteller.to_object.title
                    herstellerurl = obj.hersteller.to_object.absolute_url()
            entry['hersteller'] = hersteller
            entry['herstellerurl'] = herstellerurl
            self.hautschutzmittel.append(entry)


class CompareHautschutz(api.Page):
    api.context(Interface)

    def formatList(self, value):
        if value:
            format = u'<ul>'
            for i in value:
                format += '<li>%s</li>' %i
            format += '</ul>'
            return format
        return ''

    def update(self):
        sessiondata = getSessionData(self.request)
        if self.request.get('choose'):
            sessiondata['hhplan'] = True
            sessiondata['hautschutz'] = self.request.get('produkt')
            dataid = setSessionData(self.request, sessiondata)
            url = self.context.absolute_url() + '/@@resulthautschutz'
            return self.response.redirect(url)
        vergleich = []
        title = [u'Produktname',]
        bild = [u'Produktbild']
        hersteller = [u'Hersteller']
        gefaehrdung = [u'Gefährdung']
        kategorie = [u'Kategorie']
        uvschutzfaktor = [u'Sonnenschutzfaktor']
        zusatzfunktion = [u'Zusatzfunktion']
        inhaltsstoffe = [u'Inhaltsstoffe']
        konservierungsmittel = [u'Konservierungsmittel']
        duftstoffe = [u'Duftstoffe']
        text = [u'<b>Produkt auswählen</b>',]
        uids = self.request.get('produkt')
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(UID = uids)
        for i in brains:
            obj = i.getObject()
            title.append(obj.title)
            imgtag = '<img class="img-responsive" src="%s/@@images/bild/thumb">' %obj.absolute_url()
            bild.append(imgtag)
            hersteller.append(obj.hersteller.to_object.title)
            gefaehrdung.append(self.formatList([anwendungVocabulary.getTerm(i).title for i in obj.gefaehrdung]))
            kategorie.append(self.formatList([hskategorieVocabulary.getTerm(i).title for i in obj.kategorie]))
            uvschutzfaktor.append(obj.uvschutzfaktor)
            zusatzfunktion.append(zusatzVocabulary.getTerm(obj.zusatzfunktion).title)
            inhaltsstoffe.append(self.formatList(obj.inhaltsstoffe))
            konservierungsmittel.append(self.formatList(obj.konservierungsmittel))
            duftstoffe.append(self.formatList(obj.duftstoffe))
            text.append('<input class="form-control" type="checkbox" name="produkt" value="%s">' %obj.UID())
        vergleich.append(title)
        vergleich.append(bild)
        vergleich.append(hersteller)
        vergleich.append(gefaehrdung)
        vergleich.append(kategorie)
        vergleich.append(uvschutzfaktor)
        vergleich.append(zusatzfunktion)
        vergleich.append(inhaltsstoffe)
        vergleich.append(konservierungsmittel)
        vergleich.append(duftstoffe)
        vergleich.append(text)
        self.vergleich = vergleich
        self.formurl = self.context.absolute_url() + '/comparehautschutz'
