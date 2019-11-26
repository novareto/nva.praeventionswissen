from zope.interface import Interface
from uvc.api import api
from plone import api as ploneapi
from Products.CMFCore.utils import getToolByName

class Handschuhliste(api.Page):
    api.context(Interface)

    def update(self):
        """ """

    def render(self):
        return 'Hallo Welt'

