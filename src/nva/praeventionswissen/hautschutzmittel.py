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

from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory
from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from nva.praeventionswissen.vocabularies import hskategorieVocabulary

anwendungen = [
    SimpleTerm(u"id_chemisch", u"id_chemisch", u"chemisch"),
    SimpleTerm(u"id_biologisch", u"id_biologisch", u"biologisch"),
    SimpleTerm(u"id_rauche", u"id_rauche", u"Schweissrauche"),
    SimpleTerm(u"id_uvstrahlen", u"id_uvstrahlen", u"UV-Strahlen"),
    ]
anwendungVocabulary = SimpleVocabulary(anwendungen)

#anwendungVocabulary = SimpleVocabulary.fromItems((
#    (u"chemisch", "id_chemisch"),
#    (u"biologisch", "id_biologisch"),
#    (u"Schweissrauche", "id_rauche"),
#    (u"UV-Strahlen", "id_uvstrahlen")))

zusatzVocabulary = SimpleVocabulary.fromItems((
    (u"gegen Hauterweichung", "id_hauterweichung"),
    (u"keine", "keine")))


class IHautschutzmittel(form.Schema, IImageScaleTraversable):
    """
    Schema eines Hautschutzmittels
    """

    title = schema.TextLine(title=u"Produktname")

    gefaehrdung = schema.List(title=u'Gefährdung', value_type=schema.Choice(vocabulary=anwendungVocabulary, required=False), required=False)

    kategorie = schema.List(title=u'Schutzfunktion bei chemischer Gefährdung', value_type=schema.Choice(vocabulary=hskategorieVocabulary), required=False)

    uvschutzfaktor = schema.TextLine(title=u'Sonnenschutzfaktor', required=False)

    schweissrauche = schema.TextLine(title=u'Zusatzangaben bei Schweissarbeiten', required=False)

    zusatzfunktion = schema.Choice(title=u'Zusatzfunktion', vocabulary=zusatzVocabulary, default="keine", required=False)  

    inhaltsstoffe = schema.List(title=u"Inhaltsstoffe", value_type=schema.TextLine(), required=False)

    konservierungsmittel = schema.List(title=u"Konservierungsmittel", value_type=schema.TextLine(), required=False)

    duftstoffe = schema.List(title=u"Duftstoffe", value_type=schema.TextLine(), required=False)

    bemerkungen = schema.Text(title=u"Bemerkungen", required=False)

    bild = NamedBlobImage(title=u'Produktbild', required=False)

    hersteller = RelationChoice(
        title=u"Hersteller oder Lieferant",
        source=ObjPathSourceBinder(),
        required=False,
        )

class Hautschutzmittel(Container):
    grok.implements(IHautschutzmittel)

@indexer(IHautschutzmittel)
def myHautschutzkategorien(obj):
    katliste = []
    for i in obj.kategorie:
        if i != u'auswahl':
            katliste.append(i)
    return katliste
grok.global_adapter(myHautschutzkategorien, name="getHautschutzmittel")

@indexer(IHautschutzmittel)
def Hersteller(obj):
    if obj.hersteller:
        return obj.hersteller.to_object.UID()
grok.global_adapter(Hersteller, name='getHersteller')
