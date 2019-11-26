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

from plone.directives import form as directivesform
from plone.formwidget.multifile import MultiFileFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory
from nva.praeventionswissen.vocabularies import bgetembranchen
from nva.praeventionswissen.vocabularies import hskategorieVocabulary


class IGefahrstoff(form.Schema, IImageScaleTraversable):
    """
    Schema eines Hautpflegemittels
    """

    title = schema.TextLine(title=u"Name des Gefahrstoffes")

    description = schema.Text(title=u"Nähere Angaben zum Gefahrstoff", required=False)

    casnr = schema.TextLine(title=u"CAS-Nummer", required=False)

    hskategorie = schema.Choice(title=u"Hautschutzmittelgruppe", vocabulary=hskategorieVocabulary, required=False)

    hersteller = schema.TextLine(title=u"Name des Herstellers", required=False)

    branche = schema.List(title=u"Branchen, in denen der Gefahrstoff eingesetzt wird",
                          value_type=schema.Choice(vocabulary=bgetembranchen),
                          required = False)
