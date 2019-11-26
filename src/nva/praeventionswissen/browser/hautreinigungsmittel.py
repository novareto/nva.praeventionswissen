# -*- coding: utf-8 -*-
from zope.interface import Interface
from uvc.api import api
from plone import api as ploneapi
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.vocabularies import schmutzVocabulary
from nva.praeventionswissen.vocabularies import schmutzVocabulary

api.templatedir('templates')

class HautreinigungsmittelView(api.View):
    api.context(Interface)

    def checkHHPlan(self):
        reinigungsmittel = self.context.UID()
        sessiondata = getSessionData(self.request)
        storedhrmittel = sessiondata.get('hautreinigung')
        if storedhrmittel:
            if reinigungsmittel in storedhrmittel:
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
        self.anwendungsbereich = ''
        if self.context.anwendungsbereich:
            self.anwendungsbereich = ', '.join([schmutzVocabulary.getTerm(i).title for i in self.context.anwendungsbereich])
        self.inhaltsstoffe = ''
        if self.context.inhaltsstoffe:
            self.inhaltsstoffe = ', '.join(self.context.inhaltsstoffe)
        self.reibemittel = ''
        if self.context.reibemittel:
            self.reibemittel = ', '.join(self.context.reibemittel)
        self.loesemittel = ''
        if self.context.loesemittel:
            self.loesemittel = ', '.join(self.context.loesemittel)
        self.konservierungsmittel = ''
        if self.context.konservierungsmittel:
            self.konservierungsmittel = ', '.join(self.context.konservierungsmittel)
        self.duftstoffe = ''
        if self.context.duftstoffe:
            self.duftstoffe = ', '.join(self.context.duftstoffe)
        self.addurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/hautreinigungsmittelplan?produkt=%s' % self.context.UID()


class HautreinigungsmittelPlan(api.View):
    api.context(Interface)

    def render(self):
        reinigungsmittel = self.request.get('produkt')
        sessiondata = getSessionData(self.request)
        storedhrmittel = sessiondata.get('hautreinigung')
        if storedhrmittel:
            if reinigungsmittel not in storedhrmittel:
                storedhrmittel.append(reinigungsmittel)
        else:
            storedhrmittel = [reinigungsmittel]
        sessiondata['hautreinigung'] = storedhrmittel
        sessiondata['hhplan'] = True
        dataid = setSessionData(self.request, sessiondata)
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/@@resulthautreinigung'
        return self.response.redirect(url)


class ListHautreinigungsmittel(api.Page):
    api.context(Interface)

    def update(self):
        brains = ploneapi.content.find(portal_type="Hautreinigungsmittel", sort_on="sortable_title")

        self.hautreinigungsmittel = []        
        for i in brains:
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = ''
            if obj.bild:
                entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['anwendungsbereich'] = ','.join([schmutzVocabulary.getTerm(i).title for i in obj.anwendungsbereich])
            hersteller = ''
            herstellerurl = ''
            if obj.hersteller:
                if obj.hersteller.to_object:
                    hersteller = obj.hersteller.to_object.title
                    herstellerurl = obj.hersteller.to_object.absolute_url()
            entry['hersteller'] = hersteller
            entry['herstellerurl'] = herstellerurl
            self.hautreinigungsmittel.append(entry)


class ResultHautreinigung(api.Page):
    api.context(Interface)


    def update(self):
        self.hautreinigungsmittel = []
        sessiondata = getSessionData(self.request)
        brains = ploneapi.content.find(UID = sessiondata['hautreinigung'])
        for i in brains:
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = ''
            if obj.bild:
                entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['anwendungsbereich'] = ','.join([schmutzVocabulary.getTerm(i).title for i in obj.anwendungsbereich])
            hersteller = ''
            herstellerurl = ''
            if obj.hersteller:
                if obj.hersteller.to_object:
                    hersteller = obj.hersteller.to_object.title
                    herstellerurl = obj.hersteller.to_object.absolute_url()
            entry['hersteller'] = hersteller
            entry['herstellerurl'] = herstellerurl
            self.hautreinigungsmittel.append(entry)


class CompareHautreinigung(api.Page):
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
            sessiondata['hautreinigung'] = self.request.get('produkt')
            dataid = setSessionData(self.request, sessiondata)
            url = self.context.absolute_url() + '/@@resulthautreinigung'
            return self.response.redirect(url)
        vergleich = []
        title = [u'Produktname',]
        bild = [u'Produktbild']
        hersteller = [u'Hersteller']
        anwendungsbereich = [u'Anwendungsbereich']
        inhaltsstoffe = [u'Inhaltsstoffe']
        reibemittel = [u'Reibemittel']
        loesemittel = [u'Lösemittel']
        konservierungsmittel = [u'Konservierungsmittel']
        duftstoffe = [u'Duftstoffe']
        text = [u'<b>Produkt auswählen</b>',]
        uids = self.request.get('produkt')
        #pcat = getToolByName(self.context, 'portal_catalog')
        #brains = pcat(UID = uids)
        brains = ploneapi.content.find(UID = uids)
        for i in brains:
            obj = i.getObject()
            title.append(obj.title)
            imgtag = '<img class="img-responsive" src="%s/@@images/bild/thumb">' %obj.absolute_url()
            bild.append(imgtag)
            hersteller.append(obj.hersteller.to_object.title)
            anwendungsbereich.append(self.formatList([schmutzVocabulary.getTerm(i).title for i in obj.anwendungsbereich]))
            inhaltsstoffe.append(self.formatList(obj.inhaltsstoffe))
            reibemittel.append(self.formatList(obj.reibemittel))
            loesemittel.append(self.formatList(obj.loesemittel))
            konservierungsmittel.append(self.formatList(obj.konservierungsmittel))
            duftstoffe.append(self.formatList(obj.duftstoffe))
            text.append('<input class="form-control" type="checkbox" name="produkt" value="%s">' %obj.UID())
        vergleich.append(title)
        vergleich.append(bild)
        vergleich.append(hersteller)
        vergleich.append(anwendungsbereich)
        vergleich.append(inhaltsstoffe)
        vergleich.append(reibemittel)
        vergleich.append(loesemittel)
        vergleich.append(konservierungsmittel)
        vergleich.append(duftstoffe)
        vergleich.append(text)
        self.vergleich = vergleich
        self.formurl = self.context.absolute_url() + '/comparehautreinigung'
