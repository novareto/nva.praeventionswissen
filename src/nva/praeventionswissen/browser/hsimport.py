import xlrd
import transaction
from zope.interface import Interface
from plone import api as ploneapi
from uvc.api import api
from plone.i18n.normalizer import idnormalizer
import string
import transaction
from random import choice

api.templatedir('templates')

class HSImport(api.Page):
    api.context(Interface)

    def update(self):
        book = xlrd.open_workbook("/tmp/Listen_Branche_DP.xls")
        sh = book.sheet_by_index(2)
        for rx in range(1,sh.nrows):
            print sh.row(rx)[0].value
            entry = {}
            obj = ploneapi.content.create(
                type='Hautschutzmittel',
                title=sh.row(rx)[0].value,
                container=self.context)
            obj.gefaehrdung = ['id_chemisch',]
            kategorie= []
            if u'wechsel' in sh.row(rx)[2].value:
                kategorie.append('id_wechselnd')
            if u'wasserunl' in sh.row(rx)[2].value:
                kategorie.append('id_nichtwasserloeslich')
            if u'wasserl' in sh.row(rx)[2].value:
                kategorie.append('id_wasserloeslich')
            obj.kategorie = kategorie
            obj.inhaltsstoffe = [x.strip() for x in sh.row(rx)[3].value.split(',')]
            obj.konservierungsmittel = [x.strip() for x in sh.row(rx)[4].value.split(',')]
            obj.bemerkungen = sh.row(rx)[5].value
            transaction.commit()

    def render(self):
        return "Fertig"

class setHSKategorie(api.Page):
    api.context(Interface)

    def update(self):
        gefahrstoffe = ploneapi.content.find(portal_type='Gefahrstoff')
        for i in gefahrstoffe:
            obj = i.getObject()
            obj.hskategorie = 'id_nichtwasserloeslich'

            
    def render(self):
        return "fertig"
