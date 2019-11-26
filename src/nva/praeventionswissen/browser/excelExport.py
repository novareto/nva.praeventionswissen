# -*- coding: utf-8 -*-
from zope.interface import Interface
import xlwt
import tempfile
from plone import api as ploneapi
from uvc.api import api
from edi.restreader.restaccess import getExternalGefahrstoffe, getExternalGefahrstoff
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

class createExcel(api.View):
    api.context(Interface)

    def createWorksheet(self, ws):
        ws.write(0,0, u'Hersteller:')
        ws.write(0,2, u'Gültige Werte:')
        ws.write(0,3, 10)
        ws.write(0,4, 30)
        ws.write(0,5, 60)
        ws.write(0,6, 120)
        ws.write(0,7, 240)
        ws.write(0,8, 480)
        ws.write(2,2, u'Produkt-UID (wird von BG ausgefüllt)')
        ws.write(1,0, u'Bearbeiter:')
        ws.write(3,0, u'UID')
        ws.write(3,1, u'Gefahrstoffe')
        ws.write(3,2, u'Zusammensetzung')
        ws.write(3,3, u'Ihr Produkt')
        ws.write(3,4, u'Ihr Produkt')
        ws.write(3,5, u'Ihr Produkt')
        ws.write(3,6, u'Ihr Produkt')
        ws.write(3,7, u'Ihr Produkt')
        ws.write(3,8, u'Ihr Produkt')

    def writeExcel(self, ws, row, data):
        algn1 = xlwt.Alignment()
        algn1.wrap = 1
        algn1.vert = 0
        algn1.horz = 1
        style1 = xlwt.XFStyle()
        style1.alignment = algn1
        chemikalien = data.get('chemikalienliste')
        ws.write(row,0, data.get('UID'), style1)
        try:
            produkt = u"%s\r(%s)\r" %(data.get('title'),
                                  data.get('hersteller').get('title'))
        except:
            if data.get('hersteller'):
                produkt = "%s\r(%s)\r" %(data.get('title'), data.get('hersteller'))
            else:
                produkt = "%s\r(keine Herstellerangabe)\r" %(data.get('title'))
        ws.write(row,1, produkt, style1)
        eintrag = ""
        for k in chemikalien:
            if k.get('cas'):
                eintrag += u"%s (%s) Anteil: %s\r" %(k.get('gefahrstoff'),
                                                     k.get('cas'),
                                                     k.get('anteil'))
            else:
                eintrag += u"%s Anteil: %s\r" %(k.get('gefahrstoff'),
                                                k.get('anteil'))
        ws.write(row,2, eintrag, style1) 

    def render(self):
        entries = getExternalGefahrstoffe()
        localgs = ploneapi.content.find(portal_type="Gefahrstoff", review_state="published")
        for i in localgs:
            gs = {}
            obj = i.getObject()
            gs['title'] = obj.title
            gs['description'] = obj.description
            gs['UID'] = obj.UID()
            gs['hersteller'] = obj.hersteller
            entries.append(gs)
        print len(entries)
        wb = xlwt.Workbook()
        ws = wb.add_sheet(u'Chemische Beständigkeit')
        row = 4
        self.createWorksheet(ws)
        for i in entries:
            url = i.get('@id')
            if url:
                data = getExternalGefahrstoff(url)
                if data.get('chemikalienliste'):
                    self.writeExcel(ws, row, data)
                    row += 1
            else:
                data = i
                data['chemikalienliste'] = []
                self.writeExcel(ws, row, data)
                row += 1
        myfile = tempfile.TemporaryFile()
        wb.save(myfile)
        myfile.seek(0)
        filename = 'produktdaten.xls'
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'application/vnd.ms-excel')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' %filename)
        return myfile.read()
