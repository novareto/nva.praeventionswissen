from zope.interface import Interface
from uvc.api import api
from plone import api as ploneapi
from nva.praeventionswissen.persistance import delSessionData

class DelData(api.View):
    api.context(Interface)

    def update(self):
        delSessionData(self.request)

    def render(self):
        url = ploneapi.portal.get().absolute_url() + '/hand-und-hautschutz'
        return self.response.redirect(url)
