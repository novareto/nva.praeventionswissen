from zope.interface import Interface
import random
from time import strftime, localtime
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from uvc.api import api
from plone import api as ploneapi
from nva.praeventionswissen.vocabularies import dpGefahrstoffe, dentalGefahrstoffe, textilGefahrstoffe, reinGefahrstoffe

api.templatedir('templates')

def webcodehandler(obj):
    """ Dieser Event wird immer dann aufgerufen wenn ein Dokument modifiziert wird.
        Mit dem Event soll eine 8-stellige, moeglichst eindeutige Zahl gebildet werden. Das
        soll durch folgende Methode erreicht werden:
        * Verkettung 2-stellige Jahreszahl(Konstante) + 6-stellige Zufallszahl
        * Catalogabfrage, ob im betr. Jahr ein Objekt mit dieser Kombination vorhanden ist, wenn ja:
          * wiederholter Aufruf des Zusfallszahlengenerators
    try:
        test = obj.webcode
    except:
        return
    """
    if not obj.webcode: #Webcode soll nur automatisch gesetzt werden wenn das Attribut leer ist
        #Bildung des Webcodes
        aktuell=str(DateTime()).split(' ')[0]
        neujahr='%s/01/01' %str(DateTime()).split(' ')[0][:4]
        konstante=str(aktuell[2:4])
        zufallszahl=str(random.randint(100000, 999999))
        code=konstante+zufallszahl
        #Sicherheitsabfrage
        pcat=getToolByName(obj,'portal_catalog')
        results = pcat(Webcode=code, created={"query":[neujahr,aktuell],"range":"minmax"})
        while results:
            zufallszahl=str(random.randint(100000, 999999))
            code=konstante+zufallszahl
            results = pcat(Webcode=code, created={"query":[neujahr,aktuell],"range":"minmax"})
        #Setzen des Webcodes
        obj.webcode = code
        obj.reindexObject()
        return code

class setWebCode(api.View):
    api.context(Interface)

    def render(self):
        brains = ploneapi.content.find(portal_type=['Schutzhandschuh', 'Hautschutzmittel', 'Hautreinigungsmittel', 
                                                    'Hautpflegemittel', 'Desinfektionsmittel'])
        for i in brains:
            obj = i.getObject()
            code = webcodehandler(obj)
            print code
        return 'Fertig'

class Testdp(api.Page):
    api.context(Interface)

    def render(self):
        gefahrstoffe = dpGefahrstoffe(self.context)
        self.mylist = []
        for i in gefahrstoffe:
            gefahrstoff = i.title
            brains = ploneapi.content.find(portal_type="Schutzhandschuh", Gefahrstoffe=i.value)
            handschuhe = ', '.join([i.Title for i in brains])
            self.mylist.append((gefahrstoff, handschuhe))
        mypage = u"<h1>Gefahrstoffe DP</h1>"
        mypage += u'<table class="table table-bordered"><thead><th>Gefahrstoff</th><th>Handschuhe</th></thead><tbody>'
        for i in self.mylist:
            mypage += u'<tr><td>%s</td><td>%s</td></tr>' %(i[0], i[1])
        mypage += u'</tbody></table>'
        return mypage

class Testdental(api.Page):
    api.context(Interface)

    def render(self):
        gefahrstoffe = dentalGefahrstoffe(self.context)
        self.mylist = []
        for i in gefahrstoffe:
            gefahrstoff = i.title
            brains = ploneapi.content.find(portal_type="Schutzhandschuh", Gefahrstoffe=i.value)
            handschuhe = ', '.join([i.Title for i in brains])
            self.mylist.append((gefahrstoff, handschuhe))
        mypage = u"<h1>Gefahrstoffe Dentaltechnik</h1>"
        mypage += u'<table class="table table-bordered"><thead><th>Gefahrstoff</th><th>Handschuhe</th></thead><tbody>'
        for i in self.mylist:
            try:
                mypage += u'<tr><td>%s</td><td>%s</td></tr>' %(i[0].decode('utf-8'), i[1].decode('utf-8'))
            except:
                print 'egal'
        mypage += u'</tbody></table>'
        return mypage

class Testtextil(api.Page):
    api.context(Interface)

    def render(self):
        gefahrstoffe = textilGefahrstoffe(self.context)
        self.mylist = []
        for i in gefahrstoffe:
            gefahrstoff = i.title
            brains = ploneapi.content.find(portal_type="Schutzhandschuh", Gefahrstoffe=i.value)
            handschuhe = ', '.join([i.Title for i in brains])
            self.mylist.append((gefahrstoff, handschuhe))
        mypage = u"<h1>Gefahrstoffe Textil / Mode</h1>"
        mypage += u'<table class="table table-bordered"><thead><th>Gefahrstoff</th><th>Handschuhe</th></thead><tbody>'
        for i in self.mylist:
            try:
                mypage += u'<tr><td>%s</td><td>%s</td></tr>' %(i[0].decode('utf-8'), i[1].decode('utf-8'))
            except:
                print 'egal'
        mypage += u'</tbody></table>'
        return mypage

class Testdrein(api.Page):
    api.context(Interface)

    def render(self):
        gefahrstoffe = reinGefahrstoffe(self.context)
        self.mylist = []
        for i in gefahrstoffe:
            gefahrstoff = i.title
            brains = ploneapi.content.find(portal_type="Schutzhandschuh", Gefahrstoffe=i.value)
            handschuhe = ', '.join([i.Title for i in brains])
            self.mylist.append((gefahrstoff, handschuhe))
        mypage = u"<h1>Gefahrstoffe Reinstoffe</h1>"
        mypage += '<table class="table table-bordered"><thead><th>Gefahrstoff</th><th>Handschuhe</th></thead><tbody>'
        for i in self.mylist:
            mypage += '<tr><td>%s</td><td>%s</td></tr>' %(i[0], i[1])
        mypage += '</tbody></table>'
        return mypage
