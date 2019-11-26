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

class myHRImport(api.Page):
    api.context(Interface)

    def update(self):
        book = xlrd.open_workbook("/tmp/Listen_Branche_DP.xls")
        sh = book.sheet_by_index(7)
        objlist = []
        for rx in range(1,sh.nrows):
            print sh.row(rx)[0].value
            entry = {}
            entry['name'] = sh.row(rx)[0].value
            entry['hersteller'] = sh.row(rx)[1].value
            objlist.append(entry)

            obj = ploneapi.content.create(
                type='Hautreinigungsmittel',
                title=sh.row(rx)[0].value,
                container=self.context)
            anwendungsbereich = []
            if u'leicht' in sh.row(rx)[2].value:
                anwendungsbereich.append('id_leicht')
            if u'normal' in sh.row(rx)[2].value:
                anwendungsbereich.append('id_normal')
            if u'grob' in sh.row(rx)[2].value:
                anwendungsbereich.append('id_grob')
            obj.anwendungsbereich = anwendungsbereich
            obj.reibemittel = [x.strip() for x in sh.row(rx)[3].value.split(',')]
            obj.loesemittel = [x.strip() for x in sh.row(rx)[4].value.split(',')]
            obj.konservierungsmittel = [x.strip() for x in sh.row(rx)[5].value.split(',')]
            obj.inhaltsstoffe = [x.strip() for x in sh.row(rx)[6].value.split(',')]
            obj.bemerkungen = sh.row(rx)[7].value

            transaction.commit()

        print objlist
        self.objlist = objlist

    def render(self):
        return "Fertig"
