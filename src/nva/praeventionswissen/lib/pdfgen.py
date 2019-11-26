# -*- coding: utf-8 -*-
#Import der benoetigten Bibliotheken
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from time import gmtime, strftime
from reportlab.graphics.barcode.code39 import Standard39
from reportlab.lib.colors import gray
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from App.config import getConfiguration
from plone import api as ploneapi

config = getConfiguration()
configuration = config.product_config.get('praeventionswissen', dict())
image = configuration.get('image')


def formatMittel(products):
    brains = ploneapi.content.find(UID=products)
    mittel = []
    for i in brains:
        entry = {}
        obj = i.getObject()
        entry['title'] = obj.title
        hersteller = ''
        herstellerurl = ''
        if obj.hersteller:
            if obj.hersteller.to_object:
                hersteller = obj.hersteller.to_object.title
                herstellerurl = obj.hersteller.to_object.absolute_url()
        entry['hersteller'] = hersteller
        mittel.append(entry)
    return mittel

#Definition einer Funktion
def createpdf(filehandle, sessiondata):
    """
    Schreibt eine PDF-Datei
    """

    #Pfad und Dateiname
    timestamp=strftime("%d%m%Y%H%M%S",gmtime()) #Ermitteln der aktuellen Uhrzeit und Formatierung eines Strings mit Zeitstempel

    #c ist ein Objekt der Klasse Canvas
    c = canvas.Canvas(filehandle,pagesize=A4)

    #Metainformationen fuer das PDF-Dokument
    c.setAuthor(u"Berufsgenossenschaft Energie Textil Medienerzeugnisse")
    c.setTitle(u"Hand- und Hautschutzplan")
    c.drawImage(image, 0*cm, 0*cm, width=20.993*cm, height=29.693*cm)

    #Variablen 
    schriftart = "Helvetica"
    schriftartfett = "Helvetica-Bold"

    c.setFont(schriftart,12)
    if sessiondata.get('taetigkeit'):
        taetigkeit = sessiondata.get('taetigkeit').get('title')
    c.drawString(5.5*cm, 18.6*cm, taetigkeit)
    if sessiondata.get('hautschutzplan'):
        arbeitsbereich = sessiondata.get('hautschutzplan').get('arbeitsbereich')
        verantwortung = sessiondata.get('hautschutzplan').get('verantwortung')
        stand = sessiondata.get('hautschutzplan').get('stand')
        information = sessiondata.get('hautschutzplan').get('information')
        telefon = sessiondata.get('hautschutzplan').get('telefon')
        lieferant = sessiondata.get('hautschutzplan').get('lieferant')
        tel_lieferant = sessiondata.get('hautschutzplan').get('tel_lieferant')
    c.drawString(5.5*cm, 19.15*cm, arbeitsbereich)
    c.drawString(8.2*cm, 19.7*cm, verantwortung)
    c.drawString(15.5*cm, 19.7*cm, stand)
    c.drawString(8.4*cm, 3.55*cm, information)
    c.drawString(15.4*cm, 3.55*cm, telefon)
    c.drawString(3.3*cm, 2.55*cm, tel_lieferant)
    c.drawString(7.2*cm, 2*cm, lieferant)


    c.setFont(schriftart,9)
    fixx = 8
    if sessiondata.get('hautschutz'):
        mittel = formatMittel(sessiondata.get('hautschutz'))
        fixy = 15.6
        diff = 0.5
        for i in mittel:
            eintrag = '%s (%s)' % (i.get('title'), i.get('hersteller'))
            c.drawString(fixx*cm, fixy*cm, eintrag)
            fixy = fixy - diff

    if sessiondata.get('schutzhandschuhe'):
        mittel = formatMittel(sessiondata.get('schutzhandschuhe'))
        fixy = 13.1
        diff = 0.5
        for i in mittel:
            eintrag = '%s (%s)' % (i.get('title'), i.get('hersteller'))
            c.drawString(fixx*cm, fixy*cm, eintrag)
            fixy = fixy - diff

    if sessiondata.get('desinfektion'):
        mittel = formatMittel(sessiondata.get('desinfektion'))
        fixy = 10.55
        diff = 0.5
        for i in mittel:
            eintrag = '%s (%s)' % (i.get('title'), i.get('hersteller'))
            c.drawString(fixx*cm, fixy*cm, eintrag)
            fixy = fixy - diff

    if sessiondata.get('hautreinigung'):
        mittel = formatMittel(sessiondata.get('hautreinigung'))
        fixy = 8.05
        diff = 0.5
        for i in mittel:
            eintrag = '%s (%s)' % (i.get('title'), i.get('hersteller'))
            c.drawString(fixx*cm, fixy*cm, eintrag)
            fixy = fixy - diff

    if sessiondata.get('hautpflege'):
        mittel = formatMittel(sessiondata.get('hautpflege'))
        fixy = 5.5
        diff = 0.5
        for i in mittel:
            eintrag = '%s (%s)' % (i.get('title'), i.get('hersteller'))
            c.drawString(fixx*cm, fixy*cm, eintrag)
            fixy = fixy - diff

    #Seitenumbruch
    c.showPage()
    #Schliessen der Datei
    c.save()

    return filehandle
