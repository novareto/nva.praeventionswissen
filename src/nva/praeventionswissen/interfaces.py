# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from zope.schema import ValidationError
from plone.directives import dexterity, form
from edi.restreader.restaccess import possibleGefahrstoffe
from edi.restreader.restaccess import getExternalGefahrstoff
from nva.praeventionswissen.vocabularies import collectGefahrstoffe
from nva.praeventionswissen.vocabularies import rankvalue, rankvalue2, rankvalue3
from nva.praeventionswissen.vocabularies import biologische_gefaehrdung, biologische_gefaehrdung_short
from nva.praeventionswissen.vocabularies import schichtstaerke, stulpenlaenge, gefaehrdungen
from zope.schema import ValidationError
from collective.z3cform.datagridfield import DictRow, DataGridFieldFactory
from plone import api as ploneapi
from nva.praeventionswissen.persistance import getSessionData

class ISchutzhandschuhOrdner(Interface):
    """Marker Interface"""

class INvaPraeventionswissenLayer(Interface):
    """Marker Interface"""

class ITaetigkeitform(Interface):

    title = schema.TextLine(title=u"Name der Tätigkeit", required=True)

    description = schema.TextLine(title=u"Kurzbeschreibung", required=False)
    
    beschreibung = schema.Text(title=u"Beschreibung der Tätigkeit", 
                       description=u"Bitte beschreiben Sie hier die Tätigkeit etwas ausführlicher.",
                       required=False)

    gefaehrdung = schema.Choice(title=u"Primäre Gefährdung",
                       description=u"Bitte wählen Sie hier die primäre Gefährdung bei dieser Tätigkeit aus.",
                       source=gefaehrdungen,
                       required=True)

class IMechanikform(Interface):

    abrieb = schema.Choice(title=u"Abriebfestigkeit", source=rankvalue)

    schnittcoup = schema.Choice(title=u"Schnittfestigkeit (Coup-Test)", 
                      description=u"Arbeiten mit scharfen, aber leichten Gegenständen.",
                      source=rankvalue2)

    riss = schema.Choice(title=u"Reißfestigkeit", source=rankvalue)

    stick = schema.Choice(title=u"Durchstichfestigkeit", source=rankvalue)

    schnittiso = schema.Choice(title=u"Schnittfestigkeit (ISO-Test)",
                      description=u"Arbeiten mit scharfen Gegenständen unter unterschiedlich großer Krafteinwirkung oder stoßartigen einmaligen Gefahren.",
                      source=rankvalue3)

    stoss = schema.Bool(title=u"Schutz vor Stößen")


class GefahrstoffConflict(ValidationError):
    """ Sie haben die Gefahrstoffangaben in Ihrem Hand- und Hautschutzplan verändert. Die jetzt ausgewählten Gefahrstoffe passen
        leider nicht zu dem von Ihnen ausgewählten Hautschutzprodukt. Bitte korrigieren Sie Ihre Gefahrstoffauswahl oder löschen
        Sie Ihre Daten und treffen danach erneut eine Auswahl für Ihren Hand- und Hautschutzplan. """

def validateGefahrstoffe(value):
    context = ploneapi.portal.get()
    sessiondata = getSessionData(context.REQUEST)
    if sessiondata.get('hautschutz'):
        brain = ploneapi.content.find(UID=sessiondata.get('hautschutz'))[0]
        obj = brain.getObject()
        kategorie = obj.kategorie[0]
        if kategorie == 'id_wechselnd':
            return True
        for i in value:
            if i.startswith('http://emissionsarme'):
                jsonobj = getExternalGefahrstoff(i)
                if jsonobj.get('hskategorie') != kategorie:
                    raise GefahrstoffConflict
            else:
                objid = collectGefahrstoffe(context).getTerm(i).token
                brain = ploneapi.content.find(portal_type="Gefahrstoff", id=objid)[0]
                obj = brain.getObject()
                if obj.hskategorie != kategorie:
                    raise GefahrstoffConflict
    return True

class IChemieform(Interface):

    gefahrstoffe = schema.List(title=u"Folgende Gefahrstoffe kommen bei dieser Tätigkeit zur Anwendung:",
                      value_type=schema.Choice(source=collectGefahrstoffe),
                      constraint = validateGefahrstoffe,
                      required=True)

    biologie = schema.Choice(title=u"Mit folgenden biologischen Gefährdungen ist diese Tätigkeit verbunden:",
                      source=biologische_gefaehrdung, required=False)
    
    mechanik = schema.Bool(title=u"Mechanische Gefährdungen",
                           description=u"(Beispiel: Arbeit mit spitzen oder scharfkantigen Gegenstände, Stosseinwirkung)",
                           required=False)

    #thermisch = schema.Bool(title=u"Thermische Gefährdungen",
    #                  description=u"(Hitze oder Kälteeinwirkung)",
    #                  required=False)

    materialdicke = schema.Choice(title=u"Schichtstärke des Handschuhs",
                      description=u"Je nach Tätigkeit spielt die Schichtstärke des Handschuhs eine Rolle bei der Frage wie\
                                    feinfühlig gearbeitet werden muss. Bitte wählen Sie hier die gewünschte Schichtstärke\
                                    des Handschuhs.",
                      source=schichtstaerke,
                      required=False)

    handschuhlaenge = schema.Choice(title=u"Länge der Stulpe",
                      description=u"Wenn bei der von Ihnen beschriebenen Tätigkeit die Länge der Stulpen ein Rolle spielt,\
                                  können Sie diese hier für Ihre Produktauswahl angeben.",
                      source=stulpenlaenge,
                      required = False)


class IBiologieform(Interface):

    biologie = schema.Choice(title=u"Mit folgenden biologischen Gefährdungen ist diese Tätigkeit verbunden:",
                      source=biologische_gefaehrdung_short, default=u'bakterienpilze', required=True)


    gefahrstoffe = schema.List(title=u"Chemische Gefährdungen",
                      description=u"Folgende Gefahrstoffe kommen bei dieser Tätigkeit zur Anwendung:",
                      value_type=schema.Choice(source=collectGefahrstoffe),
                      constraint = validateGefahrstoffe,
                      required=False)

    mechanik = schema.Bool(title=u"Mechanische Gefährdungen",
                           description=u"(Beispiel: Arbeit mit spitzen oder scharfkantigen Gegenstände, Stosseinwirkung)",
                           required=False)

    #thermisch = schema.Bool(title=u"Thermische Gefährdungen",
    #                  description=u"(Hitze oder Kälteeinwirkung)",
    #                  required=False)

    materialdicke = schema.Choice(title=u"Schichtstärke des Handschuhs",
                      description=u"Je nach Tätigkeit spielt die Schichtstärke des Handschuhs eine Rolle bei der Frage wie\
                                    feinfühlig gearbeitet werden muss. Bitte wählen Sie hier die gewünschte Schichtstärke\
                                    des Handschuhs.",
                      source=schichtstaerke,
                      required=False)

    handschuhlaenge = schema.Choice(title=u"Länge der Stulpe",
                      description=u"Wenn bei der von Ihnen beschriebenen Tätigkeit die Länge der Stulpen ein Rolle spielt,\
                                  können Sie diese hier für Ihre Produktauswahl angeben.",
                      source=stulpenlaenge,
                      required = False)



class IHSfinden(Interface):

    gefahrstoffe = schema.List(title=u"Folgende Gefahrstoffe kommen bei der Tätigkeit zur Anwendung:",
                      value_type=schema.Choice(source=collectGefahrstoffe),
                      required=True)

class IGefaehrdung(Interface):

    gefaehrdung = schema.Choice(title=u"Primäre Gefährdung",
                       description=u"Bitte wählen Sie hier die primäre Gefährdung bei Ihrer Tätigkeit aus.",
                       source=gefaehrdungen,
                       required=True)

class IHautschutzplan(Interface):

    arbeitsbereich = schema.TextLine(title=u"Arbeitsbereich / Arbeitsplatz:",
                       required=False)

    verantwortung = schema.TextLine(title=u"Verantwortlich für den Hand- und Hautschutzplan:",
                       required=True)

    stand = schema.TextLine(title=u"Stand:",
                       required=False)

    information = schema.TextLine(title=u"Information/Einweisung/praktische Übung durch:",
                       required=False)

    telefon = schema.TextLine(title=u"Telefon:",
                       required=False)

    lieferant = schema.TextLine(title=u"Neue Schutzhandschuhe sind erhältlich bei:",
                       required=False)

    tel_lieferant = schema.TextLine(title=u"Telefon Ansprechpartner Hautmittel",
                                    description=u"Bitte diese Telefonnummer anrufen wenn die Bestände zur Neige gehen.",
                       required=False)

