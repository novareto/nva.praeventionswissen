# -*- coding:utf-8 -*-
import urllib
import transaction
from operator import itemgetter
from App.config import getConfiguration
from Products.statusmessages.interfaces import IStatusMessage
from plone import api as ploneapi
from uvc.api import api
from zeam.form.base import DictDataManager, Error
from zope.interface import Interface
from Products.CMFPlone.utils import getToolByName
from ukbg.theme.interfaces import IThemeSpecific
from zeam.form.base.widgets import ActionWidget
from zeam.form.base import interfaces
from grokcore import component as grok
from nva.praeventionswissen.interfaces import ITaetigkeitform, IChemieform
from edi.restreader.restaccess import possibleGefahrstoffe
from nva.praeventionswissen.persistance import getSessionData, setSessionData
from nva.praeventionswissen.schutzhandschuh import durchbruchzeit, material, profilierung, ausfuehrung
from nva.praeventionswissen.vocabularies import collectGefahrstoffe
from nva.praeventionswissen.schutzhandschuh import IGefahrstoffe
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

api.templatedir('templates')

class AddGs(api.Form):
    api.context(Interface)
    fields = api.Fields(IGefahrstoffe)

    ignoreRequest = False
    ignoreContent = False

    def update(self):
        self.formurl = self.context.absolute_url() + '/addgs'

    @api.action('speichern')
    def handle_search(self):
        data, errors = self.extractData()
        if errors:
            ploneapi.portal.show_message(message='Bitte korrigieren Sie die angezeigten Fehler.', 
                                         request=self.request, type="error")
            return
        url = self.context.absolute_url()+'/gsadder?gefahrstoff=%s&zeit=%s' %(data.get('gefahrstoff'), data.get('zeit'))
        return self.redirect(url)

        url = self.context.absolute_url()
        return self.redirect(url)

    @api.action('abbrechen')
    def handel_cancel(self):
        url = self.context.absolute_url()
        return self.redirect(url)


class GsAdder(api.View):
    api.context(Interface)

    def render(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        mydict = {'gefahrstoff':self.request.get('gefahrstoff'), 'zeit':self.request.get('zeit')}
        myobj = self.context
        schutz = myobj.gefahrstoffschutz
        if not schutz:
            schutz = []
        schutz.append(mydict)
        myobj.gefahrstoffschutz = schutz
        myobj.reindexObject()

        ploneapi.portal.show_message(message='Der Gefahrstoff wurde gespeichert.',
                                         request=self.request, type="info")

        url = self.context.absolute_url()
        return self.redirect(url)


class DelGs(api.View):
    api.context(Interface)

    def render(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        gsid = self.request.get('gs')
        gefahrstoffe = self.context.gefahrstoffschutz
        new_gefahrstoffe = [x for x in gefahrstoffe if not (gsid == x.get('gefahrstoff'))]

        myobj = self.context
        myobj.gefahrstoffschutz = new_gefahrstoffe 
        myobj.reindexObject()

        ploneapi.portal.show_message(message='Der Gefahrstoff wurde entfernt.',
                                         request=self.request, type="info")

        url = self.context.absolute_url()
        return self.redirect(url)
