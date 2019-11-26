from zope.interface import Interface
from uvc.api import api
from plone import api as ploneapi

api.templatedir('templates')

class HHindex(api.Page):
    api.context(Interface)

    def update(self):
        self.homeurl = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz'
