from zope.interface import Interface
from uvc.api import api
from plone import api as ploneapi
from plone.app.layout.viewlets.interfaces import IAboveContent, IAboveContentTitle, IBelowContentTitle
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.interfaces import ISchutzhandschuhOrdner
from nva.praeventionswissen.vocabularies import schichtstaerke, stulpenlaenge

api.templatedir('templates')

class SchutzhandschuhFilter(api.Viewlet):
    api.context(Interface)
    api.viewletmanager(IBelowContentTitle)

    def available(self):
        if ISchutzhandschuhOrdner.providedBy(self.context):
            return True
        return False

    def getHersteller(self):
        fc = self.context.getFolderContents()
        produkthersteller = []
        for i in fc:
            if i.portal_type in ['Schutzhandschuh', 'Hautreinigungsmittel', 'Hautpflegemittel', 'Hautschutzmittel', 'Desinfektionsmittel']:
                obj = i.getObject()
                if obj.hersteller:
                    if (obj.hersteller.to_object.UID(), obj.hersteller.to_object.title) not in produkthersteller:
                        produkthersteller.append((obj.hersteller.to_object.UID(), obj.hersteller.to_object.title))
        sorted_produkthersteller = sorted(produkthersteller, key=lambda tup: tup[1])
        return sorted_produkthersteller

    def update(self):
        self.hersteller = self.getHersteller()
        

class UserStatus(api.Viewlet):
    api.context(Interface)
    api.viewletmanager(IAboveContentTitle)

    def hsReady(self, sessiondata):
        taetigkeit = False
        hautschutz = False
        if sessiondata.get('taetigkeit'):
            taetigkeit = sessiondata.get('taetigkeit')
            if taetigkeit.get('title') and taetigkeit.get('gefaehrdung'):
                taetigkeit = True
        if sessiondata.get('hautschutz') or sessiondata.get('schutzhandschuhe'):
            hautschutz = True
        if taetigkeit == True and hautschutz == True:
            return True
        return False

    def getTaetigkeit(self, sessiondata):
        btnclass = "btn btn-warning"
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/taetigkeitform'
        if sessiondata.get('taetigkeit'):
            taetigkeit = sessiondata.get('taetigkeit')
            if taetigkeit.get('title') and taetigkeit.get('gefaehrdung'):
                btnclass = "btn btn-success"
        return {'btn': btnclass, 'url': url}


    def getSchutzhandschuhe(self, sessiondata):
        btnclass = "btn btn-warning"
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/gefaehrdung'
        if sessiondata.get('hautschutz'):
            btnclass = "btn btn-default"
        if sessiondata.get('schutzhandschuhe'):
            form = '/hand-und-hautschutz/schutzhandschuhe'
            btnclass = "btn btn-success"
            url = self.context.aq_inner.absolute_url() + form
        return {'btn': btnclass, 'url': url}


    def getHautschutz(self, sessiondata):
        btnclass = "btn btn-warning"
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/hsfinden'
        if sessiondata.get('schutzhandschuhe'):
            btnclass = "btn btn-default"
        if sessiondata.get('hautschutz'):
            btnclass = "btn btn-success"
            url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/resulthautschutz'
        return {'btn': btnclass, 'url': url}

    def getHautreinigung(self, sessiondata):
        btnclass = "btn btn-default"
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/listhautreinigungsmittel'
        if sessiondata.get('hautreinigung'):
                form = '/hand-und-hautschutz/resulthautreinigung'
                btnclass = "btn btn-success"
                url = self.context.aq_inner.absolute_url() + form
        return {'btn': btnclass, 'url': url}

    def getHautpflege(self, sessiondata):
        btnclass = "btn btn-default"
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/listhautpflegemittel'
        if sessiondata.get('hautpflege'):
                form = '/hand-und-hautschutz/resulthautpflege'
                btnclass = "btn btn-success"
                url = self.context.aq_inner.absolute_url() + form
        return {'btn': btnclass, 'url': url}

    def getDesinfektion(self, sessiondata):
        btnclass = "btn btn-default"
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz/listdesinfektionsmittel'
        if sessiondata.get('desinfektion'):
                form = '/hand-und-hautschutz/resultdesinfektion'
                btnclass = "btn btn-success"
                url = self.context.aq_inner.absolute_url() + form
        return {'btn': btnclass, 'url': url}

    def update(self):
        sessiondata = getSessionData(self.request)
        self.available = sessiondata.get('hhplan', False)
        self.taetigkeit = self.getTaetigkeit(sessiondata)
        self.schutzhandschuhe = self.getSchutzhandschuhe(sessiondata)
        self.hautschutz = self.getHautschutz(sessiondata)
        self.desinfektion = self.getDesinfektion(sessiondata)
        self.hautreinigung = self.getHautreinigung(sessiondata)
        self.hautpflege = self.getHautpflege(sessiondata)
        self.ready = self.hsReady(sessiondata)
        self.homeurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz'
