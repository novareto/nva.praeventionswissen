import os
from zope.interface import Interface
from uvc.api import api
import tempfile
from pyPdf import PdfFileWriter, PdfFileReader
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from nva.praeventionswissen.lib.pdfgen import createpdf
from nva.praeventionswissen.persistance import getSessionData
from App.config import getConfiguration


config = getConfiguration()
configuration = config.product_config.get('praeventionswissen', dict())
vorlage = configuration.get('vorlage')

class PDFView(api.View):
    """
    pdf browser view
    """
    api.context(Interface)

    def render(self):
        """
        schreibt das PDF
        """

        sessiondata = getSessionData(self.request)

        filehandle = tempfile.TemporaryFile()
    
        pdf = createpdf(filehandle, sessiondata)
        pdf.seek(0)
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'application/pdf')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=hand-und-hautschutzplan.pdf')
        return pdf.read()
