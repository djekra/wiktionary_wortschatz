import pandas     as pd 
import bpyth      as bpy
import pandasklar as pak 
import bj_nlp               # für translate_tagZ




##########################################################################################################################
# ........................................................................................................................  
# Verschiedenes
# ........................................................................................................................  
##########################################################################################################################

# verbendungen
verbendungen = ('en','eln','ern','tun','sein','ln')

# Sonstiges                                      
nicht_erlaubte_sonderzeichen_gnädig  =     '[\{\}\[\]\\\|\^"§$#=<>;:→»]'     
nicht_erlaubte_sonderzeichen_lemma   =     '[\{\}\[\]\\\|\?\*\^!"§$#=<>_;:→»]'        # Klammern sind erlaubt
nicht_erlaubte_sonderzeichen         =     '[\{\}\[\]\\\|\?\*\^!"§$#=<>_;:→»]'

# Globals
# ALT nicht_erlaubte_sonderzeichen   = '[\{\}\[\]\\\|\?\*\^!"§$#=<>_;:]'

manuelle_quellen                     = ['lexeme_manuell','nachnamen','nachnamen vornamen','laender','vornamen', 'orte','laender orte','zahlwörter']
#pattern_nicht_erlaubte_sonderzeichen = re.compile(nicht_erlaubte_sonderzeichen)

# Diese Merkmale gibt es ohne data_id: 
merkmale_ohne_data_id = ['ipa','syllables','rhymes','Genus','up'] # gemeinsames up verbindet

# Diese Merkmale sind in wiktionary_merkmal_wertlos erlaubt:
merkmale_in_wiktionary_merkmal_wertlos = ['familie','down','syn','def','lateral','herkunft','gegen','kombi','down_part_1','familie_1',
                                  'down_part','nurWortart','up_part','Positiv','PTKVZ','Hilfsverb',]

##########################################################################################################################
# ........................................................................................................................  
# merkmal
# ........................................................................................................................  
##########################################################################################################################


# plan: Welche Wiktionary-Absätze sollen wie extrahiert werden und unter welchem Merkmal werden sie gespeichert?
# plan1 enthält die Merkmale, die in wiktionary_merkmal gespeichert werden.
# L extrahiert nur Links 
# T extrahiert komplette Text-Absätze
# Ü extrahiert Übersetzungen
# P extrahiert Template-Parameter (Substring reicht)
#
plan1 = [
    ('kSt.',                                 'E', 'noSteig',   ),      
    ('kSg.',                                 'E', 'noSing',   ),     
    ('Wortart fehlt',                        'P', 'nurWortart',   ),    # geändert, war E / noWortart   
    ('Navigationsleiste Anthroponyme',       'E', 'istName',   ),  
    ('Wikispecies',                          'E', 'Wikispecies',   ),  
    ('Wikivoyage',                           'E', 'Wikivoyage',   ),   
    ('Artikel Biologische Taxonomie',        'E', 'Taxonomie',   ),       
    ('Präfixe (Deutsch)',                    'E', 'Präfix',   ),  
    ('Suffixe (Deutsch)',                    'E', 'Suffix',   ),  
    ('Vorsätze für Maßeinheiten',            'E', 'VMaßeinheiten',   ),       
    ('Übersicht',                            'P', 'übersicht',   ),      
    ('Pronomina-Tabelle',                    'P', 'übersicht',   ),   
  # ('Grundformverweis',                     'P', 'lemma',       ),        
  # ('Lemmaverweis',                         'P', 'lemma',       ),   
  # ('Ähnlichkeiten',                        'P', 'ähnl',        ),  
    ('Bedeutungen',                          'L', 'def',           ),
    ('Herkunft',                             'Ü', 'herkunft',      ), 
    ('Synonyme',                             'L', 'syn',           ), 
    ('Sinnverwandte Wörter',                 'L', 'lateral',       ), 
    ('Gegenwörter',                          'L', 'gegen',         ), 
    ('Verkleinerungsformen',                 'L', 'klein',         ), 
    ('Oberbegriffe',                         'L', 'up',            ), 
    ('Holonyme',                             'L', 'up_part',       ),     
    ('Unterbegriffe',                        'L', 'down',          ),
    ('Teilbegriffe',                         'L', 'down_part',     ),
    ('Meronyme',                             'L', 'down_part_1',   ),    
    ('Charakteristische Wortkombinationen',  'L', 'kombi',         ),   
    ('Wortbildungen',                        'L', 'familie',       ), 
    ('Wortfamilie',                          'L', 'familie_1',     ),      
    ('Abkürzungen',                          'L', 'abk',           ),  
    ('Nicht mehr gültige Schreibweisen',     'L', 'alt',           ),      
    ('Nebenformen',                          'L', 'alt_1',         ),  
    ('Alternative Schreibweisen',            'L', 'alt_2',         ), 
    ('Namensvarianten',                      'L', 'alt_3',         ),      
    ('Kurzformen',                           'L', 'alt_abk',       ),  
    ('Koseformen',                           'L', 'alt_klein',     ),  
    ('Männliche Namensvarianten',            'L', 'alt_weib',      ),  
    ('Weibliche Namensvarianten',            'L', 'alt_männ',      ),      
    
    ('Weibliche Wortformen',                 'L', 'weib',          ), 
    ('Männliche Wortformen',                 'L', 'männ',          ),      
    ('Grammatische Merkmale',                'L', 'gm',            ),    
    
    ]



# plan2 enthält die Merkmale, die in wiktionary_merkmal_text gespeichert werden.
plan2 = [
    ('Bedeutungen',          'T', 'def',      ),
    ('Herkunft',             'T', 'herkunft', ), 
    ('Beispiele',            'T', 'bsp',      ), 
    ('Redewendungen',        'T', 'bsp_re',   ), 
    ('Geflügelte Worte',     'T', 'bsp_gw',   ), 
    ('Sprichwörter',         'T', 'bsp_sp',   ), 
   
]


# plan3: Reihenfolge und Liste aller Merkmale aus flexion / übersicht
# sowie die Merkmale aus named_entities_lemmas und lexeme_manuell
plan3 = [
 'Akk',
 'Akk Pl',
 'Akk Sg',
 'Akk Sg f',
 'Akk Sg m',
 'Akk Sg n',
 'Dat',
 'Dat Pl',
 'Dat Sg',
 'Dat Sg f',
 'Dat Sg m',
 'Dat Sg n',
 'Gen',
 'Gen Pl',
 'Gen Sg',
 'Gen Sg f',
 'Gen Sg m',
 'Gen Sg n',
 'Genus',
 'Hilfsverb',
 'Imp Pl',
 'Imp Sg',
 'Komparativ',
 'Konj1',
 'Konj2',    
 'Konj1 ich',
 'Konj2 ich',
 'Nom',
 'Nom Pl',
 'Nom Sg',
 'Nom Sg f',
 'Nom Sg m',
 'Nom Sg n',
 'Pl',
 'Positiv',
 'Präsens du',
 'Präsens ersiees',
 'Präsens ich',
 'Präteritum ich',
 'Ptz1',    
 'Ptz2',
 'Stamm',
 'Superlativ',
 'ipa',
 'noFlex',
 'noPl',
 'noSg',
 'syllables',
 'lex',
 'lemma',    
 'lexAlt',
 'PTKVZ',
 'Befehl du', 
 'Befehl ihr',  
 'Gerundivum',
 'Imp',
 'Konj',
 'rhymes',   # kommt direkt aus wiktionary
 'VVIZU',    # wird erkannt   
]




def sort_merkmale(df, col_merkmal='merkmal', col_sort2='merkmal_lang'):
    '''
    sortiert DataFrames mit dem Feld 'merkmal'
    '''
    df['sort'] = ''

    mask = df[col_merkmal].str.startswith('Genus')
    df.loc[mask,'sort'] += '0'
    
    mask = df[col_merkmal].str.startswith('Geschlecht')
    df.loc[mask,'sort'] += '1'    

    mask = df[col_merkmal].str.contains('Sg')
    df.loc[mask,'sort'] += '2'

    mask = df[col_merkmal].str.contains('Pl')
    df.loc[mask,'sort'] += '3'


    mask = df[col_merkmal].str.startswith('Nom')
    df.loc[mask,'sort'] += 'k1'
    mask = df[col_merkmal].str.startswith('Gen')   &   ~df[col_merkmal].str.startswith('Genus')
    df.loc[mask,'sort'] += 'k2'
    mask = df[col_merkmal].str.startswith('Dat')
    df.loc[mask,'sort'] += 'k3'
    mask = df[col_merkmal].str.startswith('Akk')
    df.loc[mask,'sort'] += 'k4'

    mask = df[col_merkmal].str.startswith('Präsens')
    df.loc[mask,'sort'] += 'v0'
    mask = df[col_merkmal].str.startswith('Präteritum')
    df.loc[mask,'sort'] += 'v1'
    mask = df[col_merkmal].str.startswith('Konj')
    df.loc[mask,'sort'] += 'v2'
    mask = df[col_merkmal].str.startswith('Imp')
    df.loc[mask,'sort'] += 'v3'
    mask = df[col_merkmal].str.startswith('Ptz')
    df.loc[mask,'sort'] += 'v4'
    mask = df[col_merkmal].str.startswith('Hilfsverb')
    df.loc[mask,'sort'] += 'v5'


    mask = df[col_merkmal].str.startswith('Positiv')
    df.loc[mask,'sort'] += 'x1'
    mask = df[col_merkmal].str.startswith('Komparativ')
    df.loc[mask,'sort'] += 'x2'
    mask = df[col_merkmal].str.startswith('Superlativ')
    df.loc[mask,'sort'] += 'x3'


    mask = df[col_merkmal].str.endswith( ('noPl','noSg','noFlex','Weitere','Stamm','ipa','syllables')) 
    df.loc[mask,'sort'] += 'z1'

    df.sort += ' ' + df[col_sort2]

    df = pak.reset_index(df.sort_values(['sort']))
    return df
   







def plan_merkmal_erstellen():
    '''
    * definiert in Steuertabellen/s01_Steuertabellen.py
    * `merkmal`: Name des Merkmals
    * `template`: Name des Mediawiki-Templates, das diese Information enthält
    * `collect`: Extractionsmethode
       * L extrahiert nur Links 
       * T extrahiert komplette Text-Absätze
       * Ü extrahiert Übersetzungen
       * P extrahiert Template-Parameter (Substring reicht)
       * E checkt nur auf Existenz
    * `plan`:
       * 1: die Merkmale, die in wiktionary_merkmal gespeichert werden
       * 2: die Merkmale, die in wiktionary_merkmal_text gespeichert werden   
       * 3: Reihenfolge und Liste aller Merkmale aus flexion / übersicht <br>
            sowie die Merkmale aus named_entities und lexeme_manuell
    * `sort`: Irgendwas zum Sortieren der Merkmale
    * `is_lex`: Ist das Merkmal ein Lexem?    
    
    '''
    
    # plan1: Normale Merkmale
    df1 = pak.dataframe(plan1, verbose=False)
    df1.columns = ['template','collect','merkmal']    
    df1['plan'] = 1
    
    # plan2: Ganze Sätze
    df2 = pak.dataframe(plan2, verbose=False)
    df2.columns = ['template','collect','merkmal']     
    df2['plan'] = 2
    
    #plan3: Merkmale aus flexion / übersicht
    df3 = pak.dataframe([ [m] for m in plan3 ], verbose=False)
    df3.columns = ['merkmal']
    df3['plan'] = 3
    df3['collect'] = ''    
    # Welche Merkmale kennzeichnen lediglich eine Gruppenzugehörigkeit?
    # Diese werden mit collect = 'E' markiert.    
    mask = df3.merkmal.str.startswith(('noSg','noPl','noFlex'))
    df3.loc[mask,'collect'] = 'E'
    df3 = sort_merkmale(df3, col_sort2='merkmal')    
    
    # alle
    result = pak.reset_index(pd.concat([df1,df2,df3]))
    result.template = result.template.fillna('')
    result.collect  = result.collect.fillna('') 
    result.sort     = result.sort.fillna('')    
    
    # is_lex
    result['is_lex'] = False
    searchfor = ['Nom', 'Gen', 'Dat', 'Akk','Pl','Sg','Präsens','Präteritum','Imp','Ptz',
                 'Konj','ich','du','ersiees','Positiv','Komparativ','Superlativ','alt', 'abk',
                 'lexAlt','lex', 'weib','männ','klein','VVIZU','Befehl']
    mask1 =  result.merkmal.str.contains('|'.join(searchfor))
    mask2 = ~result.merkmal.isin(['noPl','noSg','übersicht','Genus'])
    mask = mask1  &  mask2
    result.loc[mask,'is_lex'] = True
    
    result = pak.move_cols(result,'merkmal',0)
    return result




##########################################################################################################################
# ........................................................................................................................  
# member
# ........................................................................................................................  
##########################################################################################################################
#
# Funktion zum Sortieren der Wortarten und Merkmale
# außerdem Wortartenlisten (list_XXX), die für translate_tag eingesetzt werden
#

# Ersetzungen im member       
# wird in d01_tag_und_member ausgeführt
#
member_replaces = {  
       'Eigenname'                 :  '',     
       'Straßenname'               :  'Geo_straße',
       'Ortsnamengrundwort'        :  'Geo_ort',        
       'Ort'                       :  'Geo_ort',  
       'Stadt'                     :  'Geo_stadt',        
       'Land'                      :  'Geo_land',    
       'Toponym'                   :  'Geo',      
       'Wikivoyage'                :  'Geo',   
       'Vorname'                   :  'Person_vorname',    
       'Nachname'                  :  'Person_nachname',  
       'PRE'                       :  'Person_pre',       
       'adjektivische_Deklination' :  'adjNN',   
       'Wikispecies'               :  'Spezies',  
       'VMaßeinheiten'             :  'Einheit',    
     #  'Geo_Geo_Ort'               :  'Geo_Ort', 
     
    }

# Klassifizierung

list_lexeme_V             = ['Konjugierte_Form','Erweiterter_Infinitiv'] #'Erweiterter_Infinitiv' war draußen
list_lexeme_A             = ['Deklinierte_Form','Komparativ','Superlativ','Dekliniertes_Gerundivum']

list_NE                  = ['Vorname','Person_vorname','Eigenname','Toponym','Geo','Straßenname','Geo_straße','Stadt','Geo_stadt','Land','Geo_land','Ortsnamengrundwort','Ort', 'Geo_ort']
list_NE2                 = ['Nachname','Person_nachname','istName','Name','PRE','Person_pre']
list_main                = ['Substantiv','Verb','Adjektiv','Adverb','Pronomen']

list_PRO                 = ['Personalpronomen','Indefinitpronomen','Demonstrativpronomen','Possessivpronomen']
list_PRO                += ['Interrogativpronomen','Reflexivpronomen','Relativpronomen','Reziprokpronomen']
list_ADV                 = ['Modaladverb','Lokaladverb','Temporaladverb','Pronominaladverb','Interrogativadverb','Konjunktionaladverb']

list_TRUNC               = ['Präfix','Affix','Suffix','Interfix','Präfixoid','Suffixoid','Gebundenes_Lexem','oid',] 
list_ITJ                 = ['Partikel','Interjektion','Onomatopoetikum']
list_PTKANT              = ['Grußformel','Antwortpartikel',]
list_DIV                 = ['Kontraktion','Zahlwort']
list_main2               = ['Artikel','Ptz1','Ptz2']

# löschmich bezieht sich auf das Feld tag. In member sind diese Zugehörigkeiten noch vorhanden.
list_formel              = ['Redewendung','Geflügeltes_Wort','Formel','Sprichwort',]
list_merkmale            = ['adjektivische_Deklination','Zahlklassifikator','Wortverbindung','Abkürzung',]
list_partikel            = ['Partikel','Modalpartikel','Gradpartikel','Fokuspartikel','Negationspartikel','Vergleichspartikel']

# list_löschmich: alle löschmich zusammen
list_löschmich           = list_formel + list_merkmale + list_partikel

list_sonstige            = ['nurWortart','Numerale','Einheit','Hilfsverb','adjNN','Konjunktion','Subjunktion','Adposition','Präposition','Postposition','Aufzählung','lexAlt']
list_grammatik           = ['noSing','noSg','noPl','noSteig','noFlex']
list_thema               = ['Taxonomie','Wikispecies','Spezies','Wikivoyage','VMaßeinheiten','Präfix','Suffix']

list_intern              = ['manuell','ergänzt',] # manuell = stammt aus lexeme_manuell
                                                  # ergänzt = hier wurde etwas erraten




# priorität_member zum Sortieren der Reihenfolge
priorität_member         = list_lexeme_A + list_lexeme_V + list_NE + list_NE2 + list_main 
priorität_member        += list_PRO + list_ADV + list_TRUNC + list_ITJ + list_PTKANT + list_DIV + list_main2
priorität_member        += list_formel + list_merkmale + list_partikel
priorität_member        += list_sonstige + list_grammatik + list_thema + list_intern


def member_sortieren(series):
    '''
    wendet bpy.sort_by_priority_list auf eine Spalte an 
    '''
    return series.apply( lambda x: bpy.sort_by_priority_list( x, priorität_member ) )




##########################################################################################################################
# ........................................................................................................................  
# translate_tag: Wortarten >> tags
# ........................................................................................................................  
##########################################################################################################################
#
# erstellt ein DataFrame namens translate_tag,
# mit dem sich Wortarten laut Wiktionary in tags übersetzen lassen.
# Durchlauf2 bedeutet, dass diese Ersetzung doppelt durchläuft



translate_tag  = []

# Keine Grundform
translate_tag += [ (name,'LEX_V','Keine Grundform') for name in list_lexeme_V ]
translate_tag += [ (name,'LEX_A','Keine Grundform') for name in list_lexeme_A ]


# Zweierkombis
translate_tag += [('Nachname Substantiv',           'NE',     'Zweierkombis')]
translate_tag += [('Adjektiv Ptz1',                 'ADJA',   'Zweierkombis')]
translate_tag += [('Adjektiv Ptz2',                 'ADJA',   'Zweierkombis')]
translate_tag += [('Verb Hilfsverb',                'VAFIN',  'Zweierkombis')]         
translate_tag += [('Pronomen Personalpronomen',     'PPER',   'Zweierkombis')]
translate_tag += [('Pronomen Indefinitpronomen',    'PIAT',   'Zweierkombis')]
translate_tag += [('Pronomen Demonstrativpronomen', 'PDAT',   'Zweierkombis')]
translate_tag += [('Pronomen Possessivpronomen',    'PPOSS',  'Zweierkombis')]
translate_tag += [('Pronomen Interrogativpronomen', 'PWAT',   'Zweierkombis')]
translate_tag += [('Pronomen Reflexivpronomen',     'PRF',    'Zweierkombis')]
translate_tag += [('Pronomen Relativpronomen',      'PRELAT', 'Zweierkombis')]
translate_tag += [('Pronomen Reziprokpronomen',     'PRO',    'Zweierkombis')]
translate_tag += [('Konjunktion Subjunktion',       'KOUS',   'Zweierkombis')]
translate_tag += [('Adposition Postposition',       'APPO',   'Zweierkombis')]
translate_tag += [('Adposition Präposition',        'APPR',   'Zweierkombis')]
translate_tag += [('Adverb Negationspartikel',      'PTKNEG', 'Zweierkombis')]
translate_tag += [('Partikel_Vergleichspartikel',   'DIV',    'Zweierkombis')]


# Spezielle Einer 
translate_tag += [('Personalpronomen',     'PPER',   'Spezielle Einer')]
translate_tag += [('Indefinitpronomen',    'PIAT',   'Spezielle Einer')]
translate_tag += [('Demonstrativpronomen', 'PDAT',   'Spezielle Einer')]
translate_tag += [('Possessivpronomen',    'PPOSS',  'Spezielle Einer')]
translate_tag += [('Interrogativpronomen', 'PWAT',   'Spezielle Einer')]
translate_tag += [('Reflexivpronomen',     'PRF',    'Spezielle Einer')]
translate_tag += [('Relativpronomen',      'PRELAT', 'Spezielle Einer')]
translate_tag += [('Reziprokpronomen',     'PRO',    'Spezielle Einer')]

translate_tag += [('Subjunktion',          'KOUS',   'Spezielle Einer')]
translate_tag += [('Konjunktionaladverb',  'ADV',    'Spezielle Einer')] # Konkurrenz zu Konjunktion
translate_tag += [('Konjunktion',          'KON',    'Spezielle Einer')]
translate_tag += [('Postposition',         'APPO',   'Spezielle Einer')]
translate_tag += [('Präposition',          'APPR',   'Spezielle Einer')]
#translate_tag += [('Adposition',           'APPR', 'Spezielle Einer')] # Ist Prä- oder Postposition
translate_tag += [('Negationspartikel',    'PTKNEG', 'Spezielle Einer')]
translate_tag += [('Numerale',             'CARD',   'Spezielle Einer')]
translate_tag += [('Artikel',              'ART',    'Spezielle Einer')]
translate_tag += [('Hilfsverb',            'VAFIN',  'Spezielle Einer')]
translate_tag += [('Hilfsverb',            'VAFIN',  'Spezielle Einer')]
translate_tag += [('Erweiterter_Infinitiv','VVIZU',  'Spezielle Einer')]  # NEU
#translate_tag += [('Abkürzung',            'ABK',    'Spezielle Einer')]  # Eigener Tag


# Wortartenlisten (allgemeinere Klassifikation für den Rest)
translate_tag += [ (name,'NE',    'Wortartenlisten')   for name in list_NE ]
translate_tag += [ (name,'NE',    'Wortartenlisten')   for name in list_NE2 ]
translate_tag += [ (name,'PRO',   'Wortartenlisten')   for name in list_PRO ]
translate_tag += [ (name,'ADV',   'Wortartenlisten')   for name in list_ADV ]
translate_tag += [ (name,'TRUNC', 'Wortartenlisten')   for name in list_TRUNC ]
translate_tag += [ (name,'ITJ',   'Wortartenlisten')   for name in list_ITJ ]
translate_tag += [ (name,'PTKANT','Wortartenlisten')   for name in list_PTKANT ]
translate_tag += [ (name,'DIV',   'Wortartenlisten')   for name in list_DIV ]

# Spezial
translate_tag += [ (name,'NE','Spezial')      for name in ['NE Substantiv',]   ]

# Einer
translate_tag += [('Substantiv',   'NN',   'Einer')]
translate_tag += [('Verb',         'VVFIN','Einer')]
translate_tag += [('Adjektiv',     'ADJA', 'Einer')]
translate_tag += [('Adverb',       'ADV',  'Einer')]
translate_tag += [('Pronomen',     'PRO',  'Einer')]

wichtige_tags = ['LEX_V','LEX_A','NN','NE','VVFIN','ADJA','ADV','PRO','CARD','ART','TRUNC','ITJ','VAFIN','KON','PDAT','PRELAT']


# Vorrang manuell
translate_tag += [('PTKANT ITJ',   'PTKANT',   'Vorrang manuell Durchlauf2')]
translate_tag += [('ADJA Ptz2',    'ADJA',     'Vorrang manuell Durchlauf2')]


# Vorrang
translate_tag += [('LEX_V ' + name,   'LEX_V',   'Vorrang Durchlauf2')   for name in wichtige_tags ]
translate_tag += [('LEX_A ' + name,   'LEX_A',   'Vorrang Durchlauf2')   for name in wichtige_tags ]
translate_tag += [(name + ' TRUNC',   'TRUNC',   'Vorrang Durchlauf2')   for name in wichtige_tags ]
translate_tag += [(name + ' PTKANT',  'PTKANT',  'Vorrang Durchlauf2')   for name in wichtige_tags ]
translate_tag += [('PIAT DIV',        'PIAT',    'Vorrang Durchlauf2') ]
#translate_tag += [(name + ' PRO',     'PRO',     'Vorrang Durchlauf2')   for name in wichtige_tags ]

# kaputt 
translate_tag += [('TRUNCTRUNC',  'TRUNC',  'kaputt')]
translate_tag += [('LEX_ALAT',    'PRELAT', 'kaputt')]
translate_tag += [('NELAT',       'PRELAT', 'kaputt')]


# Doppelung Durchlauf2
translate_tag += [('ITJ ITJ',  'ITJ', 'Durchlauf2')]
translate_tag += [('NE NE',    'NE',  'Durchlauf2')]
translate_tag += [('ADV ADV',  'ADV', 'Durchlauf2')]

# Direkte Doppelungen
translate_tag += [(name + ' ' + name, name, 'Doppelung1') for name in wichtige_tags ]
translate_tag += [(name + ' ' + name, name, 'Doppelung2') for name in ['NE'] ]

# löschmich
translate_tag += [ (name,'','löschmich')        for name in list_löschmich ] # siehe Steuertabellen

# Test Struktur
for a,b,c in translate_tag:
    assert (a,b,c) == (a.strip(),b.strip(),c.strip())

    
# in DataFrame wandeln    
translate_tag = pak.dataframe(translate_tag, verbose=False).reset_index(drop=True)    
translate_tag.columns = ['quelle', 'ziel', 'notiz']    
# Dups entfernen
mask = translate_tag.duplicated(subset=['quelle'], keep='first')
translate_tag = pak.drop_rows(translate_tag, mask, verbose=False)    

    

    
    
##########################################################################################################################
# ........................................................................................................................  
# translate_tagZ: tags >> tagZ und tagZZ
# ........................................................................................................................  
##########################################################################################################################
# erstellt ein DataFrame namens translate_tagZ,
# mit dem sich Wortarten laut Wiktionary in tags übersetzen lassen.
#
translate_tagZ = bj_nlp.generate_translate_tags()
    




# alle_tags: Alle tags in sinnvoller Reihenfolge
alle_tags = list(translate_tagZ.tag)


def tag_sortieren(tagseries):
    '''
    wendet bpy.sort_by_priority_list auf die tag-Spalte an 
    '''
    result = tagseries.str.split().apply( lambda x: bpy.sort_by_priority_list( x, alle_tags ) )
    result = result.str.join(' ')
    return result



##########################################################################################################################
# ........................................................................................................................  
# translate_merkmal: Merkmale aus flexion
# ........................................................................................................................  
##########################################################################################################################
#

# translate_first1
translate_first1  = []
translate_first1 += [('  ',' ')] # spaces
translate_first1 += [ ('Partizip II',     'Ptz2') ]
translate_first1 += [ ('Partizip_II',     'Ptz2') ]
translate_first1 += [ ('PartizipII',      'Ptz2') ]
translate_first1 += [ ('Konjunktiv II',  'Konj2') ]
translate_first1 += [ ('Konjunktiv_II',  'Konj2') ]
translate_first1 += [ ('KonjunktivII',   'Konj2') ]
translate_first1 += [('  ',' ')] 

# translate_first2
translate_first2  = []
translate_first2 += [('  ',' ')] 
translate_first2 += [ ('Partizip I',      'Ptz1') ]
translate_first2 += [ ('Partizip_I',      'Ptz1') ]
translate_first2 += [ ('PartizipI',       'Ptz1') ]
translate_first2 += [ ('Konjunktiv I',   'Konj1') ]
translate_first2 += [ ('Konjunktiv_I',   'Konj1') ]
translate_first2 += [ ('KonjunktivI',    'Konj1') ]
translate_first2 += [('  ',' ')] 


a = {'kein Plural'  : 'noPl',        'kein Singular': 'noSg',        'Singular'             : 'Sg',          'Pluralformen'         : 'Pl',     'Plural' : 'Pl'         }
b = {'Nominativ'    : 'Nom',         'Genitiv'      : 'Gen',         'Dativ'                : 'Dat',         'Akkusativ'            : 'Akk'                             }
c = {'Imperativ'    : 'Imp',         'Gegenwart'    : 'Präsens',     'Weitere_Konjugationen': 'Weitere',     'keine weiteren Formen': 'noFlex'                          }
d = { '_ich'        : ' ich',        '_du'          : ' du',         '_er,sie,es'           : ' ersiees',    '_er, sie, es'         :' ersiees'                         }
e = { '_wir'        : ' wir',        '_ihr'         : ' ihr',        'Konjunktiv'           : 'Konj',        }

translate_merkmal = {**a, **b, **c, **d, **e }




















