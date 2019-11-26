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
from z3c.form.interfaces import HIDDEN_MODE
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory
from edi.restreader.restaccess import possibleGefahrstoffe

from plone.dexterity.browser import edit

from nva.praeventionswissen.vocabularies import durchbruchzeit, material, ausfuehrung, profilierung
from nva.praeventionswissen.vocabularies import pruefung374alt, pruefung374neu, chemikalienpruefung, pruefung375_5_2016
from nva.praeventionswissen.vocabularies import pruefung_weitere_chemie, allergene_vocab
from nva.praeventionswissen.vocabularies import pruefung_normen_mechanik, cecatvalues
from nva.praeventionswissen.vocabularies import collectGefahrstoffe

catvalue1 = SimpleVocabulary.fromItems((
    ("x", "x"),
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4")))

catvalue2 = SimpleVocabulary.fromItems((
    ("x", "x"),
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5")))

catvalue3 = SimpleVocabulary.fromItems((
    ("x", "x"),
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
    ("E", "E"),
    ("F", "F")))

catvalue4 = SimpleVocabulary.fromItems((
    ("x", "x"),
    ("P", "P")))

catvalue5 = SimpleVocabulary.fromItems((
    ("x", "x"),
    ("0", "0"),
    ("1", "1")))


class IGefahrstoffe(form.Schema):

    gefahrstoff = schema.Choice(title = u"Gefahrstoff / Chemikalie", source=collectGefahrstoffe)
    zeit = schema.Choice(title = u"Durchbruchzeit bei 23 Grad Celsius", vocabulary=durchbruchzeit)

class ISchutzhandschuh(form.Schema, IImageScaleTraversable):
    """
    Schema eines Schutzhandschuhs
    """

    title = schema.TextLine(title=u"Produktname")

    text = RichText(title=u"Weitere Beschreibungungen des Produkts", required=False)

    bild = NamedBlobImage(title=u"Produktbild", required=False)

    hersteller = RelationChoice(
        title=u"Hersteller oder Lieferant",
        source=ObjPathSourceBinder(),
        required=False,
        )

    form.widget(material_aussen=CheckBoxFieldWidget)
    material_aussen = schema.List(title=u"Material außen", value_type=schema.Choice(vocabulary=material), required=False,)

    form.widget(material_innen=CheckBoxFieldWidget)
    material_innen = schema.List(title=u"Material innen", value_type=schema.Choice(vocabulary=material), required=False)

    form.widget(innen=CheckBoxFieldWidget)
    innen = schema.List(title=u"Innenausführung", value_type=schema.Choice(vocabulary=ausfuehrung), required=False)

    form.widget(profilierung=CheckBoxFieldWidget)
    profilierung = schema.List(title=u"Profilierung", value_type=schema.Choice(vocabulary=profilierung), required=False)

    schichtstaerke_min = schema.Float(title=u"Schichtstärke (min) in mm", required=False)
    schichtstaerke_max = schema.Float(title=u"Schichtstärke (max) in mm", required=False)

    gesamtlange_von = schema.Int(title=u"Gesamtlänge (von) in mm", required=False)
    gesamtlange_bis = schema.Int(title=u"Gesamtlänge (bis) in mm", required=False)

    cecategory = schema.Choice(title=u"CE-Kategorie", vocabulary=cecatvalues)

    allergene = schema.List(title=u"Allergene", value_type=schema.Choice(vocabulary=allergene_vocab), required=False)

    m1.fieldset(
        'chemie',
        label=u"Chemische/Biologische Risiken",
        fields=['norm374_2003', 'norm374_2016', 'chemikalienliste', 'norm374_5', 'gefahrstoffschutz']
    )

    form.widget(norm374_2003=CheckBoxFieldWidget)
    norm374_2003 = schema.List(title=u"Norm EN 374-1:2003 (3 Prüfchemikalien)",
                               value_type=schema.Choice(vocabulary=pruefung374alt),
                               required=False)

    form.widget(norm374_2016=RadioFieldWidget)
    norm374_2016 = schema.Choice(title=u"Norm EN ISO 374-1:2016", 
                                 vocabulary=pruefung374neu,
                                 default='keine',
                                 required=False)

    form.widget(chemikalienliste=CheckBoxFieldWidget)
    chemikalienliste = schema.List(title=u"Liste der Prüfchemikalien",
                                    description=u"Bitte wählen Sie aus, welche Chemikalien bei der Permeationsprüfung\
                                                  verwendet wurden.",
                                    value_type=schema.Choice(vocabulary=chemikalienpruefung),
                                    required=False)

    form.widget(norm374_5=RadioFieldWidget)
    norm374_5 = schema.Choice(title=u"Norm EN ISO 374-5:2016",
                              description=u"Schutz gegen Mikroorganismen",
                              vocabulary=pruefung375_5_2016,
                              default='keine',
                              required=False)

    #form.widget(chemie_weitere=CheckBoxFieldWidget)
    #chemie_weitere = schema.List(title=u"Prüfung gegen weitere Normen",
    #                             description=u"Bitte wählen Sie aus, gegen welche Normen das Produkt außerdem\
    #                                          geprüft wurde.",
    #                             value_type=schema.Choice(vocabulary=pruefung_weitere_chemie),
    #                             required=False,)

    form.widget(gefahrstoffschutz=DataGridFieldFactory)
    form.omitted(IEditForm, 'gefahrstoffschutz')
    gefahrstoffschutz = schema.List(title = u'Gefahrstoffschutz für dieses Produkt.',
                        value_type=DictRow(title=u"Gefahrstoff", schema=IGefahrstoffe),
                        required = False,)

    m1.fieldset(
        'mechanik',
        label=u"Mechanische Risiken",
        fields=['mechanik', 'abrieb', 'schnittcoup', 'riss', 'stick', 'schnittiso', 'stoss']
    )

    form.widget(mechanik=CheckBoxFieldWidget)
    mechanik = schema.List(title=u"Prüfung gegen Normen der mechanischen Beständigkeit",
                           description=u"Bitte wählen Sie aus, gegen welche Normen der Handschuh geprüft wurde.",
                           value_type=schema.Choice(vocabulary=pruefung_normen_mechanik),
                           required=False)

    abrieb = schema.Choice(title=u"Abriebfestigkeit", vocabulary=catvalue1, required=False)
    schnittcoup = schema.Choice(title=u"Schnittfestigkeit (Coup-Test)", vocabulary=catvalue2, required=False)
    riss = schema.Choice(title=u"Weiterreißfestigkeit", vocabulary=catvalue1, required=False)
    stick = schema.Choice(title=u"Durchstichfestigkeit", vocabulary=catvalue1, required=False)
    schnittiso = schema.Choice(title=u"Schnittfestigkeit (ISO)", vocabulary=catvalue3, required=False)
    stoss = schema.Choice(title=u"Schutz gegen Stosseinwirkung", vocabulary=catvalue4, required=False)

    m1.fieldset(
        'waerme_kaelte',
        label=u"Wärme / Kälte",
        fields = ['en407', 'brennverhalten', 'kontaktwaerme', 'konvektive_hitze', 'strahlungswaerme',
                  'metallspritzer','fluessigesmetall', 'en511', 'konvektive_kaelte', 'kontaktkaelte',
                  'wasserdichtigkeit'],
    )

    en407 = schema.Bool(title=u"Norm 407",
                      description=u"Erfüllt der Schutzhandschuh die Norm 407 bzw. wurde er dagegen getestet?",)

    brennverhalten = schema.Choice(title=u"Brennverhalten", vocabulary=catvalue1, required=False)
    kontaktwaerme = schema.Choice(title=u"Kontaktwärme", vocabulary=catvalue1, required=False)
    konvektive_hitze = schema.Choice(title=u"Konvektive Hitze", vocabulary=catvalue1, required=False)
    strahlungswaerme = schema.Choice(title=u"Strahlungswärme", vocabulary=catvalue1, required=False)
    metallspritzer = schema.Choice(title=u"Belastung durch kleine Spritzer geschmolzenen Metalls", 
                               vocabulary=catvalue1, required=False)
    fluessigesmetall = schema.Choice(title=u"Belastung durch große Mengen flüssigen Metalls", 
                          vocabulary=catvalue1, required=False)

    en511 = schema.Bool(title=u"Norm 511",
                        description=u"Erfüllt der Schutzhandschuh die Norm 511 bzw. wurde er dagegen getestet?",)

    konvektive_kaelte = schema.Choice(title=u"Konvektive Kälte", vocabulary=catvalue1, required=False)
    kontaktkaelte = schema.Choice(title=u"Kontaktkälte", vocabulary=catvalue1, required=False)
    wasserdichtigkeit = schema.Choice(title=u"Wasserdichtigkeit", vocabulary=catvalue5, required=False)

    m1.fieldset(
        'elektro',
        label=u"Elektro und Elektrostatik",
        fields=['esd'],
    )

    esd = schema.Bool(title=u"ESD Produktschutz")


class EditForm(edit.DefaultEditForm):
    pass


@indexer(ISchutzhandschuh)
def myGefahrstoffe(obj):
    gefahrstoffliste = []
    for i in obj.gefahrstoffschutz:
        if i.get('gefahrstoff') != u'auswahl':
            gefahrstoffliste.append(i.get('gefahrstoff'))
            print i.get('gefahrstoff')
    return gefahrstoffliste
grok.global_adapter(myGefahrstoffe, name="getGefahrstoffe")

@indexer(ISchutzhandschuh)
def isMechanik(obj):
    if u'din_en_388_alt' in obj.mechanik:
        return True
    if u'din_en_388_2016' in obj.mechanik:
        return True
    return False
grok.global_adapter(isMechanik, name="getMechanik")

@indexer(ISchutzhandschuh)
def isThermisch(obj):
    if obj.en407 and obj.en511:
        return True
    return False
grok.global_adapter(isThermisch, name="getThermisch")

@indexer(ISchutzhandschuh)
def isBiologisch(obj):
    if obj.norm374_2003:
        if u'bakt_pilze' in obj.norm374_2003:
            return True
    if obj.norm374_5:
        if u'bakterienpilze' in obj.norm374_5:
            return True
        if u'bakterienpilzeviren' in obj.norm374_5:
            return True
    return False
grok.global_adapter(isBiologisch, name="getBiologisch")

@indexer(ISchutzhandschuh)
def isViren(obj):
    if obj.norm374_5:
        if u'bakterienpilzeviren' in obj.norm374_5:
            return True
    return False
grok.global_adapter(isViren, name="getViren")

@indexer(ISchutzhandschuh)
def bioGefahr(obj):
    schutz = []
    if obj.norm374_2003:
        if u'bakt_pilze' in obj.norm374_2003:
            if not u"bakterienpilze" in schutz:
                schutz.append(u"bakterienpilze")
    if obj.norm374_5:
        if u'bakterienpilze' in obj.norm374_5:
            if not u"bakterienpilze" in schutz:
                schutz.append(u"bakterienpilze")
        if u'bakterienpilzeviren' in obj.norm374_5:
            schutz.append(u"bakterienpilzeviren")
    return schutz
grok.global_adapter(bioGefahr, name="getBiogefahr")

@indexer(ISchutzhandschuh)
def isChemiekalienschutz(obj):
    if obj.norm374_2003:
        if 'chemikalien_einfach' in obj.norm374_2003:
            return True
        if 'chemikalien_spez' in obj.norm374_2003:
            return True
    if obj.norm374_2016:
        if obj.norm374_2016.startswith('Typ'):
            return True
    return False
grok.global_adapter(isChemiekalienschutz, name="getChemiekalienschutz")

@indexer(ISchutzhandschuh)
def Abriebvalue(obj):
    values = []
    if obj.abrieb:
        if obj.abrieb != 'x':
            for i in range(int(obj.abrieb)+1):
                values.append(str(i))
    return values
grok.global_adapter(Abriebvalue, name="getAbrieb")

@indexer(ISchutzhandschuh)
def Schnittcoupvalue(obj):
    values = []
    if obj.schnittcoup:
        if obj.schnittcoup != 'x':
            for i in range(int(obj.schnittcoup)+1):
                values.append(str(i))
    return values
grok.global_adapter(Schnittcoupvalue, name="getSchnittcoup")

@indexer(ISchutzhandschuh)
def Rissvalue(obj):
    values = []
    if obj.riss:
        if obj.riss != 'x':
            for i in range(int(obj.riss)+1):
                values.append(str(i))
    return values
grok.global_adapter(Rissvalue, name="getRiss")

@indexer(ISchutzhandschuh)
def Stichvalue(obj):
    values = []
    if obj.stick:
        if obj.stick != 'x':
            for i in range(int(obj.stick)+1):
                values.append(str(i))
    return values
grok.global_adapter(Stichvalue, name="getStich")

@indexer(ISchutzhandschuh)
def Schnittisovalue(obj):
    values = []
    if obj.schnittiso == 'A':
        values = ['A']
    elif obj.schnittiso == 'B':
        values = ['A', 'B']
    elif obj.schnittiso == 'C':
        values = ['A', 'B', 'C']
    elif obj.schnittiso == 'D':
        values = ['A', 'B', 'C', 'D']
    elif obj.schnittiso == 'E':
        values = ['A', 'B', 'C', 'D', 'E']
    elif obj.schnittiso == 'F':
        values = ['A', 'B', 'C', 'D', 'E', 'F']
    return values    
grok.global_adapter(Schnittisovalue, name="getSchnittiso")

@indexer(ISchutzhandschuh)
def Stossvalue(obj):
    if obj.stoss == 'P':
        return True
    return False
grok.global_adapter(Stossvalue, name="getStoss")

@indexer(ISchutzhandschuh)
def Tastsinn(obj):
    value = 0.0
    if not obj.schichtstaerke_max:
        value = obj.schichtstaerke_min
    else:
        value = obj.schichtstaerke_max
    if value <= 0.15:
        return u'thin'
    if 0.15 < value <= 0.5:
        return u'medium'
    if value > 0.5:
        return u'thick'
grok.global_adapter(Tastsinn, name='getTastsinn')

@indexer(ISchutzhandschuh)
def Stulpenlaenge(obj):
    laenge = 0
    if not obj.gesamtlange_bis:
        laenge = obj.gesamtlange_von
    else:
        laenge = obj.gesamtlange_bis
    if laenge <= 230:
        return u'kurz'
    if 230 < laenge <= 260:
        return u'mittel'
    if laenge > 260:
        return u'lang'
grok.global_adapter(Stulpenlaenge, name='getStulpenlaenge')  

@indexer(ISchutzhandschuh)
def Hersteller(obj):
    if obj.hersteller:
        return obj.hersteller.to_object.UID()
grok.global_adapter(Hersteller, name='getHersteller')

class Schutzhandschuh(Container):
    grok.implements(ISchutzhandschuh)
