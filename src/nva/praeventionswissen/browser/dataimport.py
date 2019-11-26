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

class DataImport(api.Page):
    api.context(Interface)

    def update(self):
        book = xlrd.open_workbook("/tmp/Gefahrstoffe_TM.xls")
        sh = book.sheet_by_index(0)
        objlist = []
        for rx in range(1,sh.nrows):
            entry = {}
            entry['gefahrstoff'] = sh.row(rx)[0].value
            entry['hersteller'] = sh.row(rx)[1].value
            objlist.append(entry)

            obj = ploneapi.content.create(
                type='Gefahrstoff',
                title=sh.row(rx)[0].value,
                container=self.context)
            obj.hersteller = sh.row(rx)[1].value

            transaction.commit()
        self.objlist = objlist
