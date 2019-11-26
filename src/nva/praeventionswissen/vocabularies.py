# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from edi.restreader.restaccess import externalGefahrstoffList
from plone import api as ploneapi
from zope.schema.interfaces import IContextSourceBinder
from Products.CMFCore.utils import getToolByName
from zope.interface import directlyProvides
from plone.memoize import ram
from time import time

hskategorien = [
    SimpleTerm(u"id_wasserloeslich", u"wasserloeslich", u"gegen wasserlösliche Arbeitsstoffe"),
    SimpleTerm(u"id_nichtwasserloeslich", u"nichtwasserloeslich", u"gegen wasserunlösliche Arbeitsstoffe"),
    SimpleTerm(u"id_wechselnd", u"wechselnd", u"gegen wechselnde Arbeitsstoffe")]
hskategorieVocabulary = SimpleVocabulary(hskategorien)


cekategorien = [
    SimpleTerm(u"auswahl", u"auswahl", u"bitte auswählen"),
    SimpleTerm(1, 1, u'I'),
    SimpleTerm(2, 2, u'II'),
    SimpleTerm(3, 3, u'III')]
cecatvalues = SimpleVocabulary(cekategorien)

zeiten = [
    SimpleTerm(u"auswahl", u"auswahl", u"bitte auswählen"),
    SimpleTerm(u"spritzschutz", u"spritzschutz", u"Spritzschutz / <=10min"),
    SimpleTerm(u"10", u"10", u">10min"),
    SimpleTerm(u"30", u"30", u">30min"),
    SimpleTerm(u"60", u"60", u">60min"),
    SimpleTerm(u"120", u"120", u">120min"),
    SimpleTerm(u"240", u"240", u">240min"),
    SimpleTerm(u"480", u"480", u">480min")]
durchbruchzeit = SimpleVocabulary(zeiten)

einwirkung = [
    SimpleTerm(u"auswahl", u"auswahl", u"bitte auswählen"),
    SimpleTerm(u"30", u"30", u"30"),
    SimpleTerm(u"60", u"60", u"60"),]
einwirkzeit = SimpleVocabulary(einwirkung)

materialien = [
    SimpleTerm(u"baumwolle", u"baumwolle", u"Baumwolle"),
    SimpleTerm(u"bambus-viskose", u"bambus-viskose", u"Bambus-Viskose"),
    SimpleTerm(u"butylkautschuk", u"butylkautschuk", u"Butylkautschuk (Butyl, IR)"),
    SimpleTerm(u"dyneema", u"dyneema", u"Dyneema"),
    SimpleTerm(u"fluorkautschuk", u"fluorkautschuk", u"Fluorkautschuk (Viton, FKM)"),
    SimpleTerm(u"glasfaser", u"glasfaser", u"Glasfaser"),
    SimpleTerm(u"kevlar", u"kevlar", u"Kevlar"),
    SimpleTerm(u"naturkautschuk", u"naturkautschuk", u"Naturkautschuk (Latex, NR)"),
    SimpleTerm(u"nitrilkautschuk", u"nitrilkautschuk", u"Nitrilkautschuk (Nitril, NBR)"),
    SimpleTerm(u"nylon", u"nylon", u"Nylon"),
    SimpleTerm(u"para-aramid", u"para-aramid", u"Para-Aramid"),
    SimpleTerm(u"polyamid", u"polyamid", u"Polyamid"),
    SimpleTerm(u"polychloropren", u"polychloropren", u"Polychloropren (Neopren, CR)"),
    SimpleTerm(u"polyester", u"polyester", u"Polyester"),
    SimpleTerm(u"polyurethan", u"polyurethan", u"Polyurethan (PU)"),
    SimpleTerm(u"polyvinylalkohol", u"polyvinylalkohol", u"Polyvinylalkohol (PVA)"),
    SimpleTerm(u"polyvinylchlorid", u"polyvinylchlorid", u"Polyvinylchlorid (Vinyl, PVC)"),
    SimpleTerm(u"spectra", u"spectra", u"Spectra"),
    SimpleTerm(u"stahl", u"stahl", u"Stahl"),
    SimpleTerm(u"synthetik-leder", u"synthetik-leder", u"Synthetik-Leder")]
material = SimpleVocabulary(materialien)

ausfuehrung = SimpleVocabulary.fromItems((
    (u"Baumwollbeflockung", u"Baumwollbeflockung"),
    (u"Bambus-Viskose", u"Bambus-Viskose"),
    (u"Baumwolltrikot", u"Baumwolltrikot"),
    (u"Baumwollvelourisierung", u"Baumwollvelourisierung"),
    (u"chloriniert", u"chloroniert"),
    (u"gepudert", u"gepudert"),
    (u"Innenbeschichtung aus Synthetik", u"Innenbeschichtung aus Synthetik"),
    (u"Stricktrikot", u"Stricktrikot"),
    (u"trikotiert", u"trikotiert"),
    (u"unbeschichtet", u"unbeschichtet"),
    (u"ungepudert", u"ungepudert"),
    (u"velourisiert", u"velourisiert")))

profilierungen = [
    SimpleTerm(u"Fingerspitzen Diamantprofil", u"Fingerspitzen Diamantprofil", u"Fingerspitzen Diamantprofil"),
    SimpleTerm(u"Fingerspitzen genoppt", u"Fingerspitzen genoppt", u"Fingerspitzen genoppt"),
    SimpleTerm(u"Fingerspitzen geraut", u"Fingerspitzen geraut", u"Fingerspitzen geraut"),
    SimpleTerm(u"Fingerspitzen glatt", u"Fingerspitzen glatt", u"Fingerspitzen glatt"),
    SimpleTerm(u"Fingerspitzen mit Profil", u"Fingerspitzen mit Profil", u"Fingerspitzen mit Profil"),
    SimpleTerm(u"Fingerspitzen Rautenprofil", u"Fingerspitzen Rautenprofil", u"Fingerspitzen Rautenprofil"),
    SimpleTerm(u"Handfleache Diamantprofil", u"Handfleache Diamantprofil", u"Handfläche Diamantprofil"),
    SimpleTerm(u"Handflaeche genoppt", u"Handflaeche genoppt", u"Handfläche genoppt"),
    SimpleTerm(u"Handflaeche geraut", u"Handflaeche geraut", u"Handfläche geraut"),
    SimpleTerm(u"Handflaeche glatt", u"Handflaeche glatt", u"Handfläche glatt"),
    SimpleTerm(u"Handflaeche mit Profil", u"Handflaeche mit Profil", u"Handfläche mit Profil"),
    SimpleTerm(u"Handflaeche Rautenprofil", u"Handflaeche Rautenprofil", u"Handfläche Rautenprofil")
    ]
profilierung = SimpleVocabulary(profilierungen)

chemikalientabelle = [
    SimpleTerm(u'67-56-1', u'A', u'(A) Methanol'),
    SimpleTerm(u'67-64-1', u'B', u'(B) Aceton'),
    SimpleTerm(u'75-05-8', u'C', u'(C) Acetonitril'),
    SimpleTerm(u'75-09-2', u'D', u'(D) Dichlormethan'),
    SimpleTerm(u'75-15-0', u'E', u'(E) Schwefelkohlenstoff (Kohlenstoffdisulfid)'),
    SimpleTerm(u'108-88-3', u'F', u'(F) Tuluol'),
    SimpleTerm(u'109-89-7', u'G', u'(G) Diethylamin'),
    SimpleTerm(u'109-99-9', u'H', u'(H) Tetrahydrofuran'),
    SimpleTerm(u'141-78-6', u'I', u'(I) Essigsäureethylester (Ethylacetat)'),
    SimpleTerm(u'142-82-5', u'J', u'(J) n-Heptan'),
    SimpleTerm(u'1310-73-2', u'K', u'(K) Natriumhydroxid 40 %'),
    SimpleTerm(u'7664-93-9', u'L', u'(L) Schwefelsäure 96 %'),
    SimpleTerm(u'7697-37-2', u'M', u'(M) Salpetersäure 65 %'),
    SimpleTerm(u'64-19-7', u'N', u'(N) Essigsäure 99 %'),
    SimpleTerm(u'1336-21-6', u'O', u'(O) Ammoniak 25 %'),
    SimpleTerm(u'7722-84-1', u'P', u'(P) Wasserstoffperoxid 30%'),
    SimpleTerm(u'7664-39-3', u'S', u'(S) Flusssäure 40 %'),
    SimpleTerm(u'50-00-0', u'T', u'(T) Formaldehyd 37 %'),
]
chemikalienpruefung = SimpleVocabulary(chemikalientabelle)

symboldict = {
    u'chemikalien_einfach':'EN374_allg.jpg',
    u'chemikalien_spez':'EN374_spec.jpg',
    u'bakt_pilze':'EN374_bio.jpg',
    u'TypA':'EN374_spec.jpg',
    u'TypB':'EN374_spec.jpg',
    u'TypC':'EN374_spec.jpg',
    u'bakterienpilze':'EN374_bio.jpg',
    u'bakterienpilzeviren':'EN374_bio.jpg',
    u'din_en_388_alt':'EN388.jpg',
    u'din_en_388_2016':'EN388.jpg',
    }

symbole_374_alt = [
    SimpleTerm(u'chemikalien_einfach', u'chemikalien_einfach', u'Eingeschränkter Schutz gegen Chemikalien'),
    SimpleTerm(u'chemikalien_spez', u'chemikalien_spez', u'Spezifischer Schutz gegen Chemikalien'),
    SimpleTerm(u'bakt_pilze', u'bakt_pilze', u'Schutz gegen Mikroorganismen (Bakterien und Pilze)'),
]
pruefung374alt = SimpleVocabulary(symbole_374_alt)

symbole_374_neu = [
    SimpleTerm(u'keine', u'keine', u'keine Prüfung'),
    SimpleTerm(u'TypA', u'TypA', u'EN ISO 374-1 / Typ A (6 Prüfchemikalien)'),
    SimpleTerm(u'TypB', u'TypB', u'EN ISO 374-1 / Typ B (3 Prüfchemikalien)'),
    SimpleTerm(u'TypC', u'TypC', u'EN ISO 374-1 / Typ C (1 Prüfchemikalie)'),
]
pruefung374neu = SimpleVocabulary(symbole_374_neu)

symbole_374_5 = [
    SimpleTerm(u'keine', u'keine', u'keine Prüfung'),
    SimpleTerm(u'bakterienpilze', u'bakterienpilze', u'Schutz vor Bakterien und Pilzen'),
    SimpleTerm(u'bakterienpilzeviren', u'bakterienpilzeviren', u'Schutz vor Bakterien, Pilzen und Viren'),
]
pruefung375_5_2016 = SimpleVocabulary(symbole_374_5)

biogefahr = [
    SimpleTerm(u'keine', u'keine', u'keine'),
    SimpleTerm(u'bakterienpilze', u'bakterienpilze', u'Bakterien und Pilze'),
    SimpleTerm(u'bakterienpilzeviren', u'bakterienpilzeviren', u'Bakterien, Pilze und Viren'),
]
biologische_gefaehrdung = SimpleVocabulary(biogefahr)

biogefahr_short = [
    SimpleTerm(u'bakterienpilze', u'bakterienpilze', u'Bakterien und Pilze'),
    SimpleTerm(u'bakterienpilzeviren', u'bakterienpilzeviren', u'Bakterien, Pilze und Viren'),
]
biologische_gefaehrdung_short = SimpleVocabulary(biogefahr_short)

weitere_normen_chemie = [
    SimpleTerm(u'din_en_16523', u'din_en_16523', u'DIN EN 16523'),
]
pruefung_weitere_chemie = SimpleVocabulary(weitere_normen_chemie)

normen_mechanik = [
    SimpleTerm(u'din_en_381', u'din_en_381', u'DIN EN 381'),
    SimpleTerm(u'din_en_388_alt', u'din_en_388_alt', u'DIN EN 388 vor 2016'),
    SimpleTerm(u'din_en_388_2016', u'din_en_388_2016', u"EN 388:2016"),
]
pruefung_normen_mechanik = SimpleVocabulary(normen_mechanik)

terms = [
    SimpleTerm(u"Informationsbroschuere beachten", u"Informationsbroschuere beachten", u"Informationsbroschüre beachten"),
    SimpleTerm(u"Mechanische Risiken", u"Mechanische Risiken", u"Mechanische Risiken"),
    SimpleTerm(u"Chemische Risiken", u"Chemische Risiken", u"Chemische Risiken"),
    SimpleTerm(u"Bakteriologische Risiken", u"Bakteriologische Risiken", u"Bakteriologische Risiken"),
    SimpleTerm(u"Kaelterisiken", u"Kaelterisiken", u"Kälterisiken"),
    SimpleTerm(u"Risiken durch ionisierende Strahlung", u"Risiken durch ionisierende Strahlung", u"Risiken durch ionisierende Strahlung"),
    SimpleTerm(u"Thermische Risiken", u"Thermische Risiken", u"Thermische Risiken"),
    SimpleTerm(u"Arbeiten unter elektrischer Spannung", u"Arbeiten unter elektrischer Spannung", u"Arbeiten unter elektrischer Spannung"),
    SimpleTerm(u"Schutz vor statischer Elektrizitaet", u"Schutz vor statischer Elektrizitaet", u"Schutz vor statischer Elektriztät"),
    SimpleTerm(u"Umgang mit Handmessern", u"Umgang mit Handmessern", u"Umgang mit Handmessern"),
    SimpleTerm(u"fuer Schweisser", u"fuer Schweisser", u"für Schweißer"),
    SimpleTerm(u"gegen Vibration", u"gegen Vibration", u"gegen Vibration"),
    ]
piktogramme = SimpleVocabulary(terms)

allergene = [
    SimpleTerm(u'Thiurame', u'Thiurame', u'Thiurame'),
    SimpleTerm(u'TMTM', u'TMTM', u'Tetramethylthiurammonosulfid (TMTM)'),
    SimpleTerm(u'TMTD', u'TMTD', u'Tetramethylthiuramdisulfid (TMTD)'),
    SimpleTerm(u'TETD', u'TETD', u'Tetraethylthiuramdisulfid (TETD)'),
    SimpleTerm(u'DPTD', u'DPTD', u'Dipentamethylthiuramdisulfid (DPTD)'),
    SimpleTerm(u'Dithiocarbamate', u'Dithiocarbamate', u'Dithiocarbamate'),
    SimpleTerm(u'ZDMC', u'ZDMC', u'Zinkdimethyldithiocarbamat (Ziram, ZDMC)'),
    SimpleTerm(u'ZDEC', u'ZDEC', u'Zinkdiethyldithiocarbamat (ZDC, ZDEC)'),
    SimpleTerm(u'ZDBC', u'ZDBC', u'Zinkdibutyldithiocarbamat (ZBC, ZDBC)'),
    SimpleTerm(u'ZEPC', u'ZEPC', u'Zinkethylphenyldithiocarbamat (ZEPC)'),
    SimpleTerm(u'ZPD', u'ZPD', u'Zinkpentamethylendithiocarbamat (ZPD)'),
    SimpleTerm(u'NBC', u'NBC', u'Natriumdibutyldithiocarbamat (NBC)'),
    SimpleTerm(u'NHEC', u'NHEC', u'Natriumcyclohexylethyldithiocarbamat (NHEC)'),
    SimpleTerm(u'Zinkdibenzyldithiocarbama', u'Zinkdibenzyldithiocarbama', u'Zinkdibenzyldithiocarbama'),
    SimpleTerm(u'Thioharnstoffe', u'Thioharnstoffe', u'Thioharnstoffe'),
    SimpleTerm(u'DBTU', u'DBTU', u'Dibutylthioharnstoff (DBTU)'),
    SimpleTerm(u'DETU', u'DETU', u'Diethylthioharnstoff (DETU)'),
    SimpleTerm(u'DPTU', u'DPTU', u'Diphenylthioharnstoff (DPTU)'),
    SimpleTerm(u'ETU', u'ETU', u"N,N'-Ethylenthioharnstoff (ETU)"),
    SimpleTerm(u'Mercaptobenzothiazol', u'Mercaptobenzothiazol', u'Mercaptobenzothiazol'),
    SimpleTerm(u'MBT', u'MBT', u'Mercaptobenzothiazol (MBT)'),
    SimpleTerm(u'ZMBT', u'ZMBT', u'Zinkmercaptobenzothiazol (ZMBT)'),
    SimpleTerm(u'MBS', u'MBS', u'Morpholinylmercaptobenzothiazol (MOR, MBS)'),
    SimpleTerm(u'MBTS', u'MBTS', u'Dibenzothiazyldisulfid (MBTS)',),
    SimpleTerm(u'DEBS', u'DEBS', u'Diethylbenzothiazolsulfenamid (DEBS)'),
    SimpleTerm(u'CBS', u'CBS', u'N-Cyclohexyl-2-benzothiazylsulfenamid (CBS)'),
    SimpleTerm(u'DCBS', u'DCBS', u'Dicyclohexylbenzothiazolsufenamid (DCBS)'),
    SimpleTerm(u'p-Phenylendiamin-Derivate', u'p-Phenylendiamin-Derivate' u'p-Phenylendiamin-Derivate'),
    SimpleTerm(u'IPPD', u'IPPD', u"N-Isopropyl-N'-phenyl-p-phenylendiamin (IPPD)"),
    SimpleTerm(u'DPPD', u'DPPD', u"N,N'-Diphenyl-p-phenylendiamin (DPPD)"),
    SimpleTerm(u'Mercaptobenzimidazol', u'Mercaptobenzimidazol', u'Mercaptobenzimidazol'),
    SimpleTerm(u'1,3-Diphenylguanidin', u'1,3-Diphenylguanidin', u'1,3-Diphenylguanidin'),
    SimpleTerm(u'Hydrochinon', u'Hydrochinon', u'Hydrochinon'),
    SimpleTerm(u'Hexamethylentetramin', u'Hexamethylentetramin', u'Hexamethylentetramin'),
    SimpleTerm(u'HN-Cyclohexylthiophthalimid', u'HN-Cyclohexylthiophthalimid', u'HN-Cyclohexylthiophthalimid'),
    SimpleTerm(u'Naturlatex', u'Naturlatex', u'Naturlatex'),
    SimpleTerm(u'Maisstaerke', u'Maisstaerke', u'Maisstärke'),
    ]
allergene_vocab = SimpleVocabulary(allergene)

ranks = [
    SimpleTerm(u'nicht_relevant', u'nicht_relevant', u'nicht relevant'),
    SimpleTerm(u'1', u'gering', u'gering'),
    SimpleTerm(u'2', u'mittel', u'mittel'),
    SimpleTerm(u'3', u'hoch', u'hoch'),
]
rankvalue = SimpleVocabulary(ranks)

ranks2 = [
    SimpleTerm(u'nicht_relevant', u'nicht_relevant', u'nicht relevant'),
    SimpleTerm(u'1', u'gering', u'gering'),
    SimpleTerm(u'3', u'mittel', u'mittel'),
    SimpleTerm(u'4', u'hoch', u'hoch'),
]
rankvalue2 = SimpleVocabulary(ranks2)

ranks3 = [
    SimpleTerm(u'nicht_relevant', u'nicht_relevant', u'nicht relevant'),
    SimpleTerm(u'A', u'gering', u'gering'),
    SimpleTerm(u'C', u'mittel', u'mittel'),
    SimpleTerm(u'F', u'hoch', u'hoch'),
]
rankvalue3 = SimpleVocabulary(ranks3)

bgetembranchen = SimpleVocabulary((
    SimpleTerm(value=u'druckundpapier', token=u'druckundpapier', title=u'Druck und Papierverarbeitung'),
    SimpleTerm(value=u'elektrohandwerke', token=u'elektrohandwerke', title=u'Elektrohandwerke'),
    SimpleTerm(value=u'elektrotechnische industrie', token=u'elektrotechnische industrie', title=u'Elektrotechnische Industrie'),
    SimpleTerm(value=u'feinmechanik', token=u'feinmechanik', title=u'Feinmechanik'),
    SimpleTerm(value=u'textilundmode', token=u'textilundmode', title=u'Textil und Mode'),
    ))

desinf_anwendung = SimpleVocabulary((
    SimpleTerm(value=u'haende', token=u'haende', title=u'Hände'),
    ))

desinf_produktgruppe = SimpleVocabulary((
    SimpleTerm(value=u'haendewaschprodukt', token=u'haendewaschprodukt', title=u"Hygienisches Händewaschprodukt"),
    SimpleTerm(value=u'haendedesinketionsmittel', token=u'haendedesinfektionsmittel', title=u'Händedesinfektionsmittel'),
    ))

desinf_wirksamkeit = SimpleVocabulary((
    SimpleTerm(value=u'bakterizid', token=u'bakterizid', title=u'Bakterizid (d.h. wirksam gegen Bakterien, ohne bakterielle Sporen)'),
    SimpleTerm(value=u'begrenzt_viruzid', token=u'begrenzt_viruzid', title=u'Begrenzt viruzid PLUS'),
    SimpleTerm(value=u'levurozide', token=u'levurozide', title=u'Levurozide (d.h. wirksam gegen Hefen, Sporen)'),
    SimpleTerm(value=u'mykobakterizid', token=u'mykobakterizid', title=u'Mykobakterizid'),
    SimpleTerm(value=u'fungizid', token=u'fungizid', title=u'Fungizid (d.h. wirksam gegen Schimmelpilze und deren Sporen, z.B.: Aspergillus)'),
    SimpleTerm(value=u'viruzid', token=u'viruzid', title=u'Viruswirksamkeit (d.h. begrenzt viruzid oder viruzid gemäß den Anordnungen nach RKI/DVV (2))')
    ))

desinf_pruefung = SimpleVocabulary((
    SimpleTerm(value=u'vah', token=u'vah', title=u'VAH (Verband für Angewandte Hygiene e.V.)'),
    SimpleTerm(value=u'rki', token=u'rki', title=u'RKI (Robert Koch Institut)'),
    ))

schichtstaerke = SimpleVocabulary((
    SimpleTerm(value=u'alle', token=u'alle', title=u'alle anzeigen'),
    SimpleTerm(value=u'thin', token=u'thin', title=u'geringe Schichtstärke (max. 0,15mm)'),
    SimpleTerm(value=u'medium', token=u'medium', title=u'mittlere Schichtstärke (0,15mm - 0,5mm)'),
    SimpleTerm(value=u'thick', token=u'thick', title=u'hohe Schicktstärke (> 0,5mm)'),
    ))

stulpenlaenge = SimpleVocabulary((
    SimpleTerm(value=u'alle', token=u'alle', title=u'alle anzeigen'),
    SimpleTerm(value=u'kurz', token=u'kurz', title=u'kurze Länge (max. 230mm)'),
    SimpleTerm(value=u'mittel', token=u'mittel', title=u'mittlere Länge (230mm - 260mm)'),
    SimpleTerm(value=u'lang', token=u'lang', title=u'lange Stulpen (> 260mm)'),
    ))

gefaehrdungen = SimpleVocabulary((
    SimpleTerm(value=u"b", token=u"b", title=u"Biologische Gefährdungen"),
    SimpleTerm(value=u"c", token=u"c", title=u"Chemische Gefährdungen"),
    SimpleTerm(value=u"m", token=u"m", title=u"Mechanische Gefährdungen"),
    ))

anwendungVocabulary = SimpleVocabulary((
    SimpleTerm(u"id_normal", u"id_normal", u"normal belastete Haut"),
    SimpleTerm(u"id_stark", u"id_stark", u"stark belastete Haut"),
    ))

schmutzVocabulary = SimpleVocabulary((
    SimpleTerm(u"id_leicht", u"id_leicht", u"leichte Verschmutzung"),
    SimpleTerm(u"id_normal", u"id_normal", u"normale Verschmutzung"),
    SimpleTerm(u"id_grob", u"id_grob", u"grobe Verschmutzung")
    ))

@ram.cache(lambda *args: time() // (60 * 60 * 48))
def collectGefahrstoffe(context):
    print 'collectGefahrstoffe'
    terms = externalGefahrstoffList()
    terms.append(SimpleVocabulary.createTerm(u'auswahl', u'000auswahl', u'bitte auswählen'))
    portal = ploneapi.portal.get()
    pcat = portal.portal_catalog
    brains = pcat(portal_type="Gefahrstoff", review_state="published")
    for i in brains:
        gfid = i.getURL()
        gfid = gfid.replace('http://hautschutz.bgetem.de', 'http://praevention-bgetem.bg-kooperation.de')
        gfid = gfid.replace('https://hautschutz.bgetem.de', 'http://praevention-bgetem.bg-kooperation.de')
        gfid = gfid.replace('http://bgetemkontakt.bg-kooperation.de', 'http://praevention-bgetem.bg-kooperation.de')
        gfid = gfid.replace('https://bgetemkontakt.bg-kooperation.de', 'http://praevention-bgetem.bg-kooperation.de')
        terms.append(SimpleVocabulary.createTerm(gfid, i.id, i.Title.decode('utf-8')))
    newlist = sorted(terms, key=lambda x: x.token, reverse=False)
    print 'return Gefahrstoffliste'
    return SimpleVocabulary(newlist)
directlyProvides(collectGefahrstoffe, IContextSourceBinder)

@ram.cache(lambda *args: time() // (60 * 60))
def dpGefahrstoffe(context):
    terms = externalGefahrstoffList()
    newlist = sorted(terms, key=lambda x: x.token, reverse=False)
    return SimpleVocabulary(newlist)
directlyProvides(dpGefahrstoffe, IContextSourceBinder)

@ram.cache(lambda *args: time() // (60 * 60))
def dentalGefahrstoffe(context):
    terms = []
    path = '/praevention/datenbanken/gefahrstoffe/dentaltechnik'
    portal = ploneapi.portal.get()
    pcat = portal.portal_catalog
    brains = pcat(portal_type="Gefahrstoff", path=path, review_state="published")
    for i in brains:
        terms.append(SimpleVocabulary.createTerm(i.getURL(), i.id, i.Title.decode('utf-8')))
    newlist = sorted(terms, key=lambda x: x.token, reverse=False)
    return SimpleVocabulary(newlist)
directlyProvides(dentalGefahrstoffe, IContextSourceBinder)

@ram.cache(lambda *args: time() // (60 * 60))
def textilGefahrstoffe(context):
    terms = []
    path = '/praevention/datenbanken/gefahrstoffe/textil-und-mode'
    portal = ploneapi.portal.get()
    pcat = portal.portal_catalog
    brains = pcat(portal_type="Gefahrstoff", path=path, review_state="published")
    for i in brains:
        terms.append(SimpleVocabulary.createTerm(i.getURL(), i.id, i.Title.decode('utf-8')))
    newlist = sorted(terms, key=lambda x: x.token, reverse=False)
    return SimpleVocabulary(newlist)
directlyProvides(textilGefahrstoffe, IContextSourceBinder)

@ram.cache(lambda *args: time() // (60 * 60))
def reinGefahrstoffe(context):
    terms = []
    path = '/praevention/datenbanken/gefahrstoffe/reinstoffe'
    portal = ploneapi.portal.get()
    pcat = portal.portal_catalog
    brains = pcat(portal_type="Gefahrstoff", path=path, review_state="published")
    for i in brains:
        terms.append(SimpleVocabulary.createTerm(i.getURL(), i.id, i.Title.decode('utf-8')))
    newlist = sorted(terms, key=lambda x: x.token, reverse=False)
    return SimpleVocabulary(newlist)
directlyProvides(textilGefahrstoffe, IContextSourceBinder)


