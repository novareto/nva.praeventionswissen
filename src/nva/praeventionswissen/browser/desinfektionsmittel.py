# -*- coding: utf-8 -*-
from zope.interface import Interface
from uvc.api import api
from plone import api as ploneapi
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.vocabularies import desinf_anwendung, desinf_produktgruppe, desinf_wirksamkeit, desinf_pruefung, einwirkzeit

api.templatedir('templates')

class DesinfektionsmittelView(api.View):
    api.context(Interface)

    def checkHHPlan(self):
        desinfektionsmittel = self.context.UID()
        sessiondata = getSessionData(self.request)
        storeddimittel = sessiondata.get('desinfektion')
        if storeddimittel:
            if desinfektionsmittel in storeddimittel:
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
            self.anwendungsbereich = desinf_anwendung.getTerm(self.context.anwendungsbereich).title
        self.produktgruppe = ''
        if self.context.produktgruppe:
            self.produktgruppe = desinf_produktgruppe.getTerm(self.context.produktgruppe).title
        self.wirksamkeit = ''
        if self.context.wirksamkeit:
            self.wirksamkeit = ', '.join([desinf_wirksamkeit.getTerm(i).title for i in self.context.wirksamkeit])
        self.einwirkzeit = ''
        if self.context.einwirkung:
            self.einwirkzeit = einwirkzeit.getTerm(self.context.einwirkung).title + ' Sekunden'
        self.pruefung = ''
        if self.context.pruefung:
            self.pruefung = desinf_pruefung.getTerm(self.context.pruefung).title
        self.addurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/desinfektionsmittelplan?produkt=%s' % self.context.UID()


class DesinfektionsmittelPlan(api.View):
    api.context(Interface)

    def render(self):
        desinfektionsmittel = self.request.get('produkt')
        sessiondata = getSessionData(self.request)
        storeddimittel = sessiondata.get('desinfektion')
        if storeddimittel:
            if desinfektionsmittel not in storeddimittel:
                storeddimittel.append(desinfektionsmittel)
        else:
            storeddimittel = [desinfektionsmittel]
        sessiondata['desinfektion'] = storeddimittel
        sessiondata['hhplan'] = True
        dataid = setSessionData(self.request, sessiondata)
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/@@resultdesinfektion'
        return self.response.redirect(url)


class ListDesinfektionsmittel(api.Page):
    api.context(Interface)

    def update(self):
        brains = ploneapi.content.find(portal_type="Desinfektionsmittel", sort_on="sortable_title")

        self.desinfektionsmittel = []        
        for i in brains:
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = ''
            if obj.bild:
                entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['anwendungsbereich'] = desinf_anwendung.getTerm(obj.anwendungsbereich).title
            hersteller = ''
            herstellerurl = ''
            if obj.hersteller:
                if obj.hersteller.to_object:
                    hersteller = obj.hersteller.to_object.title
                    herstellerurl = obj.hersteller.to_object.absolute_url()
            entry['hersteller'] = hersteller
            entry['herstellerurl'] = herstellerurl
            self.desinfektionsmittel.append(entry)


class ResultDesinfektion(api.Page):
    api.context(Interface)

    def update(self):
        self.desinfektionsmittel = []
        sessiondata = getSessionData(self.request)
        brains = ploneapi.content.find(UID = sessiondata['desinfektion'])
        for i in brains:
            entry = {}
            obj = i.getObject()
            entry['title'] = obj.title
            entry['url'] = obj.absolute_url()
            entry['uid'] = obj.UID()
            entry['image'] = ''
            if obj.bild:
                entry['image'] = '<img src="%s/@@images/bild/thumb">' % obj.absolute_url()
            entry['anwendungsbereich'] = desinf_anwendung.getTerm(obj.anwendungsbereich).title
            hersteller = ''
            herstellerurl = ''
            if obj.hersteller:
                if obj.hersteller.to_object:
                    hersteller = obj.hersteller.to_object.title
                    herstellerurl = obj.hersteller.to_object.absolute_url()
            entry['hersteller'] = hersteller
            entry['herstellerurl'] = herstellerurl
            self.desinfektionsmittel.append(entry)


class CompareDesinfektion(api.Page):
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
            sessiondata['desinfektion'] = self.request.get('produkt')
            dataid = setSessionData(self.request, sessiondata)
            url = self.context.absolute_url() + '/@@resultdesinfektion'
            return self.response.redirect(url)
        vergleich = []
        title = [u'Produktname',]
        bild = [u'Produktbild']
        hersteller = [u'Hersteller']
        anwendungsbereich = [u'Anwendungsbereich']
        produktgruppe = [u'Produktgruppe']
        wirksamkeit = [u'Wirksamkeit']
        einwirkung = [u'Einwirkzeit']
        pruefung = [u'Prüfung']
        text = [u'<b>Produkt auswählen</b>',]
        uids = self.request.get('produkt')
        brains = ploneapi.content.find(UID = uids)
        for i in brains:
            obj = i.getObject()
            title.append(obj.title)
            imgtag = '<img class="img-responsive" src="%s/@@images/bild/thumb">' %obj.absolute_url()
            bild.append(imgtag)
            hersteller.append(obj.hersteller.to_object.title)
            anwendungsbereich.append(desinf_anwendung.getTerm(obj.anwendungsbereich).title)
            produktgruppe.append(desinf_produktgruppe.getTerm(obj.produktgruppe).title)
            wirksamkeit.append(self.formatList([desinf_wirksamkeit.getTerm(k).title for k in obj.wirksamkeit]))
            einwirkung.append(einwirkzeit.getTerm(obj.einwirkung).title + u' Sekunden')
            pruefung.append(desinf_pruefung.getTerm(obj.pruefung).title)
            text.append('<input class="form-control" type="checkbox" name="produkt" value="%s">' %obj.UID())
        vergleich.append(title)
        vergleich.append(bild)
        vergleich.append(hersteller)
        vergleich.append(anwendungsbereich)
        vergleich.append(produktgruppe)
        vergleich.append(wirksamkeit)
        vergleich.append(einwirkung)
        vergleich.append(pruefung)
        vergleich.append(text)
        self.vergleich = vergleich
        self.formurl = self.context.absolute_url() + '/comparedesinfektion'
