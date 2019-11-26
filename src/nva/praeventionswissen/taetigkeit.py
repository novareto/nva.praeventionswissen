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
from z3c.form.browser.checkbox import CheckBoxFieldWidget

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
from z3c.form.browser.radio import RadioFieldWidget
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from plone.formwidget.autocomplete import AutocompleteFieldWidget

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory
from edi.restreader.restaccess import possibleGefahrstoffe

from nva.praeventionswissen.vocabularies import durchbruchzeit, material, ausfuehrung, profilierung
from nva.praeventionswissen.vocabularies import pruefung374alt, pruefung374neu, chemikalienpruefung, pruefung375_5_2016
from nva.praeventionswissen.vocabularies import pruefung_weitere_chemie, rankvalue, biologische_gefaehrdung
from nva.praeventionswissen.vocabularies import pruefung_normen_mechanik, gefaehrdungen
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

ranks = [
    SimpleTerm(u'nicht_relevant', u'nicht_relevant', u'nicht relevant'),
    SimpleTerm(u'gering', u'gering', u'gering'),
    SimpleTerm(u'mittel', u'mittel', u'mittel'),
    SimpleTerm(u'hoch', u'hoch', u'hoch'),
]
rankvalue = SimpleVocabulary(ranks)

class IGefahrstoffe(form.Schema):

    gefahrstoff = schema.Choice(title = u"Gefahrstoff / Chemikalie", source=collectGefahrstoffe)
    zeit = schema.Choice(title = u"Kontaktzeit", vocabulary=durchbruchzeit)

class ITaetigkeit(form.Schema, IImageScaleTraversable):
    """
    Schema eines Schutzhandschuhs
    """

    title = schema.TextLine(title=u"Tätigkeit")

    description=schema.TextLine(title=u"Kurzbeschreibung", required=False)

    text = schema.Text(title=u"Weitere Beschreibungungen der Tätigkeit", required=False)

    gefaehrdung = schema.Choice(title=u"Primäre Gefährdung bei dieser Tätigkeit",
        description=u"Bitte wählen Sie hier die primäre Gefährdung bei dieser Tätigkeit aus.",
        source = gefaehrdungen,
        required = True,
    )  

    m1.fieldset(
        'chemie',
        label=u"Chemische/Biologische Risiken",
        fields=['gefahrstoffschutz', 'biologie']
    )

    form.widget(gefahrstoffschutz=DataGridFieldFactory)
    gefahrstoffschutz = schema.List(title = u'Gefahrstoffkontakt bei dieser Tätigkeit',
                        value_type=DictRow(title=u"Gefahrstoff", schema=IGefahrstoffe),
                        required = False,)

    biologie = schema.Choice(title=u"Mit folgenden biologischen Gefährdungen ist diese Tätigkeit verbunden:",
                      source=biologische_gefaehrdung, required=True)


    m1.fieldset(
        'mechanik',
        label=u"Mechanische Risiken",
        fields=['mechanik', 'kettensaege', 'abrieb', 'schnitt', 'riss', 'stick', 'stoss']
    )

    mechanik = schema.Bool(title=u"Mechanische Gefährdungen",
                           description=u"(Beispiel: Arbeit mit spitzen oder scharfkantigen Gegenstände, Stosseinwirkung)",
                           required=False)

    kettensaege = schema.Bool(title=u"Arbeit mit handgeführten Kettensägen", required=False)
    abrieb = schema.Choice(title=u"Anforderung an Abriebfestigkeit", vocabulary=rankvalue, default='nicht_relevant', required=False)
    schnitt = schema.Choice(title=u"Anforderung an Schnittfestigkeit", vocabulary=rankvalue, default='nicht_relevant', required=False)
    riss = schema.Choice(title=u"Anforderung an Weiterreißfestigkeit", vocabulary=rankvalue, default='nicht_relevant', required=False)
    stick = schema.Choice(title=u"Anforderung an Durchstichfestigkeit", vocabulary=rankvalue, default='nicht_relevant', required=False)
    stoss = schema.Choice(title=u"Anforderung an Schutz gegen Stosseinwirkung", vocabulary=rankvalue, default='nicht_relevant', required=False)

    m1.fieldset(
        'waerme_kaelte',
        label=u"Wärme / Kälte",
        fields = ['thermisch', 'brennverhalten', 'kontaktwaerme', 'konvektive_hitze', 'strahlungswaerme',
                  'metallspritzer','fluessigesmetall', 'konvektive_kaelte', 'kontaktkaelte',
                  'wasserdichtigkeit'],
    )

    thermisch = schema.Bool(title=u"Thermische Gefährdungen",
                      description=u"(Hitze oder Kälteeinwirkung)",
                      required=False)

    brennverhalten = schema.Choice(title=u"Anforderung an das Brennverhalten", vocabulary=rankvalue, default='nicht_relevant', required=False)
    kontaktwaerme = schema.Choice(title=u"Anforderung an die Kontaktwärme", vocabulary=rankvalue, default='nicht_relevant', required=False)
    konvektive_hitze = schema.Choice(title=u"Anforderung an die Konvektive Hitze", vocabulary=rankvalue, default='nicht_relevant', required=False)
    strahlungswaerme = schema.Choice(title=u"Anforderung an die Strahlungswärme", vocabulary=rankvalue, default='nicht_relevant', required=False)
    metallspritzer = schema.Choice(title=u"Anforderung an die Belastung durch kleine Spritzer geschmolzenen Metalls", 
                               vocabulary=rankvalue, default='nicht_relevant', required=False)
    fluessigesmetall = schema.Choice(title=u"Anforderung an die Belastung durch große Mengen flüssigen Metalls", 
                          vocabulary=rankvalue, default='nicht_relevant', required=False)

    konvektive_kaelte = schema.Choice(title=u"Anforderung an die Konvektive Kälte", vocabulary=rankvalue, default='nicht_relevant', required=False)
    kontaktkaelte = schema.Choice(title=u"Anforderung an die Kontaktkälte", vocabulary=rankvalue, default='nicht_relevant', required=False)
    wasserdichtigkeit = schema.Choice(title=u"Anforderung an die Wasserdichtigkeit", vocabulary=rankvalue, default='nicht_relevant', required=False)

@indexer(ITaetigkeit)
def myGefahrstoffe(obj):
    gefahrstoffliste = []
    for i in obj.gefahrstoffschutz:
        if i.get('gefahrstoff') != u'auswahl':
            gefahrstoffliste.append(i.get('gefahrstoff'))
    return gefahrstoffliste
grok.global_adapter(myGefahrstoffe, name="getGefahrstoffe")
