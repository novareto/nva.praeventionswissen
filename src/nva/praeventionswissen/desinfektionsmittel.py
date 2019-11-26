# -*- coding: utf-8 -*-
from five import grok

from z3c.form import group, field
from z3c.form.form import extends
from z3c.form.field import Fields
from z3c.form.interfaces import IEditForm, IAddForm
from zope import schema
from zope.interface import invariant, Invalid, directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.supermodel import model as m1
from plone.dexterity.interfaces import IDexterityFTI

from plone.dexterity.content import Item, Container
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.indexer import indexer

from plone.directives import form as directivesform
from plone.formwidget.multifile import MultiFileFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory

from zope.schema.vocabulary import SimpleVocabulary
from nva.praeventionswissen.vocabularies import desinf_anwendung, desinf_produktgruppe, desinf_wirksamkeit, desinf_pruefung, einwirkzeit 

class IDesinfektionsmittel(form.Schema, IImageScaleTraversable):
    """
    Schema eines Desinfektionsmittels
    """

    title = schema.TextLine(title=u"Produktname")

    anwendungsbereich = schema.Choice(
            title=u"Anwendungsbereich", 
            source=desinf_anwendung, 
            required=True,
    )

    produktgruppe = schema.Choice(
            title=u"Produktgruppe",
            source=desinf_produktgruppe,
            default=u'haendedesinketionsmittel',
            required=True,
    )

    wirksamkeit = schema.List(
            title=u"Wirksamkeit",
            value_type=schema.Choice(
                source=desinf_wirksamkeit,),
            required=True,
    )

    einwirkung = schema.Choice(
            title = u"Einwirkzeit",
            source = einwirkzeit,
            required = True,
    )

    pruefung = schema.Choice(
            title=u"Wirksamkeit geprüft und gelistet von:",
            source=desinf_pruefung,
            default=u'vah',
            required=True,
    )

    bemerkungen = schema.Text(title=u"Bemerkungen", required=False)

    bild = NamedBlobImage(title=u"Produktbild", required=False)

    hersteller = RelationChoice(
        title=u"Hersteller oder Lieferant",
        source=ObjPathSourceBinder(),
        required=False,
        )

@indexer(IDesinfektionsmittel)
def Hersteller(obj):
    if obj.hersteller:
        return obj.hersteller.to_object.UID()
grok.global_adapter(Hersteller, name='getHersteller')


class Desinfektionsmittel(Container):
    grok.implements(IDesinfektionsmittel)
