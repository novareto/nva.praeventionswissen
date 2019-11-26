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
from plone.indexer import indexer

from plone.dexterity.content import Item, Container
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.directives import form as directivesform
from plone.formwidget.multifile import MultiFileFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory

from zope.schema.vocabulary import SimpleVocabulary
from nva.praeventionswissen.vocabularies import anwendungVocabulary


class IHautpflegemittel(form.Schema, IImageScaleTraversable):
    """
    Schema eines Hautpflegemittels
    """

    title = schema.TextLine(title=u"Produktname")

    anwendungsbereich = schema.List(title=u"Anwendungsbereich", value_type=schema.Choice(vocabulary=anwendungVocabulary), 
                                    required=False,)

    inhaltsstoffe = schema.List(title=u"Inhaltsstoffe", value_type=schema.TextLine(), required=False)

    konservierungsmittel = schema.List(title=u"Konservierungsmittel", value_type=schema.TextLine(), required=False)

    duftstoffe = schema.List(title=u"Duftstoffe", value_type=schema.TextLine(), required=False)

    bemerkungen = schema.Text(title=u"Bemerkungen", required=False)

    bild = NamedBlobImage(title=u"Produktbild", required=False)

    hersteller = RelationChoice(
        title=u"Hersteller oder Lieferant",
        source=ObjPathSourceBinder(),
        required=False,
        )

@indexer(IHautpflegemittel)
def Hersteller(obj):
    if obj.hersteller:
        return obj.hersteller.to_object.UID()
grok.global_adapter(Hersteller, name='getHersteller')

class Hautpflegemittel(Container):
    grok.implements(IHautpflegemittel)
