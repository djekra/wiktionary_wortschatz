import mwparserfromhell
import re
from x22_my_node   import *
import pandas   as pd
#import modin.pandas as pd


# plan ist ein Ausschnitt aus plan_merkmal
#
def extract_all( zeile, plan, step=None, verbose=False ):
    
    # mwparserfromhell
    wikicode = mwparserfromhell.parse(zeile.wikitext) 
    
    result = [] # das wird eine Liste von Dataframes
    
    for z in plan.itertuples():
        templatename = z.template
        collect      = z.collect  
        merkmal      = z.merkmal  
        
        if verbose:
            print(templatename,collect,merkmal)
        
        # apply erzeugt eine Series von DataFrames
        # tolist macht daraus eine Liste
        # concat macht aus diesen Listen DataFrames        
        
        if 'P' in collect:
            df = extract_parameters( zeile, templatename=templatename, merkmal=merkmal, wikicode=wikicode) 
        elif 'E' in collect:
            df = extract_exists(     zeile, templatename=templatename, merkmal=merkmal, wikicode=wikicode )               
        else:
            df = extract(            zeile, templatename=templatename, merkmal=merkmal, wikicode=wikicode, collect=collect, step=step)
        result.append(df)
    
    del wikicode
    result = pd.concat(result) # Alle DataFrames zu einem Ganzen zusammenfügen
    return result



  

def extract(zeile,                       # Datensatz einer Section, also eine Zeile des wiktionary als Series
            templatename,                # Name, z.B. 'Sinnverwandte Wörter'
            merkmal,                     # neuer Name für diese Inhalte
            löschen=True,                # sollen mit löschmich gekennzeichnete Nodes gelöscht werden?
            collect='LTÜ',               # Sollen Links, Text, Übersetzungen ausgegeben werden?    
            wikicode=None,               # Der auszuwertende Wikicode wird mitgeliefert 
            step=None                    # Nach welchem Schritt soll abgebrochen werden? Fürs Debugging  
           ):
    
    result = pd.DataFrame()
    collect_text  = 'T' in collect
    collect_links = 'L' in collect    
    collect_trans = 'Ü' in collect       
    #print(collect_text,collect_links,collect_trans)
    
    # wikicode auf 1 bestimmten Abschnitt beschränken
    wikicode = extract_after_template(wikicode, templatename)  
    if step == 1:
        return wikicode
    
    # In Zeilen splitten, die mit [1], [2] etc. beginnen
    wikicode_list = split_wikicode(wikicode)   
    if step == 2:
        return wikicode_list    
    
    # Zeilen analysieren
    mynode_list  = [[ myNode().analyze(node).cleanup(collect_text=collect_text) for node in line] for line in wikicode_list]    
    if step == 3:
        return mynode_list    

    # 
    list_list = []
    for line_id, line in enumerate(mynode_list): # das sind keine Zeilen, sondern Absätze

        # alles auf Null
        num_akt   = []   # aktuelle Zuordnung zu einer Bedeutung   
        meta_akt  = ''   # aktuelle Meta-Kennzeichnung
        text_akt  = ''   # gesammelter Text

        for node_id, node in enumerate(line):

            if löschen  and  node.löschmich:
                continue

            # auslesen und Kontext setzen. Das geht nur am Anfang.
            if node.node_type == 'Nummerierung'   and   node_id <= 3:              
                num_akt  = node.node_num              
            if node.node_meta != ''   and   node_id <= 3:                         
                meta_akt = node.node_meta  
                #debug_akt = 
            if collect_text:
                
                # meta als text aufnehmen
                t = node.node_meta.strip()
                #if t  and  len(t.split(maxsplit=1)[0]) > 1: # erstes Wort länger als 1 Buchstabe
                text_akt += ' '  
                text_akt += t     
                
                # text
                t = node.node_text.strip()
                if t  and  len(t.split(maxsplit=1)[0]) > 2: # erstes Wort länger als 2 Buchstabe
                    text_akt += ' '  
                text_akt += t      
                  

            # Link: Ergebnis-myNode erzeugen 
            if collect_links  and  (node.node_link != ''):
                item = myNode()
                item.node_num     = num_akt
                item.node_meta    = meta_akt   
                item.node_link    = node.node_link   
                item.node_text    = node.node_text 
                item.node_kontext = node.node_kontext  
                item.node_debug   = node.node_debug   
                #item.node_debug   = [line_id,node_id]                
                list_list.append(item.aslist())    
            
            # Nur Übersetzungen
            elif collect_trans  and  (node.node_text != '')  and  (node.node_kontext == 'Ü'):
                item = myNode()
                item.node_num     = num_akt
                item.node_meta    = meta_akt   
                item.node_link    = node.node_link   
                item.node_text    = node.node_text 
                item.node_kontext = node.node_kontext  
                item.node_debug   = node.node_debug                 
                list_list.append(item.aslist())                   
                
        # Text Ergebnis-myNode erzeugen 
        if collect_text  and  len(text_akt.strip()) > 0:  
            item = myNode()
            item.node_num     = num_akt
            item.node_meta    = myNode.reinige_text(meta_akt) # reinigen muss hier nachgeholt werden     
            item.node_text    = text_akt.strip().replace("'''''","").replace("''","").strip()   
            list_list.append(item.aslist())                    
                
    result = pd.DataFrame(list_list, columns=['node_num','node_meta','node_link','node_text','node_kontext','node_debug',])
    result['section_id']  = zeile.section_id 
    result['section_id2'] = zeile.section_id2     
    result['merkmal']     = merkmal  
    return result
     

    
# Gegenstück zu extract. Liest die Parameter von Templates aus.
def extract_parameters(zeile, templatename, merkmal, wikicode):
    template = get_first_template(wikicode, templatename)
    if not template:
        return pd.DataFrame()
    list_list = [[template.name, p.name, str(p.value).strip()] for p in template.params]
    result = pd.DataFrame(list_list, columns=['node_debug','node_kontext','node_text'])
    result.node_debug      = result.node_debug.astype('str')
    result.node_kontext    = result.node_kontext.astype('str').str.replace('Bild','').str.strip()    
    result['section_id']   = zeile.section_id 
    result['section_id2']  = zeile.section_id2    
    result['merkmal']      = merkmal  
    return result

  
    
# Gegenstück zu extract. Checkt die Existenz eines Templates.
def extract_exists(zeile, templatename, merkmal, wikicode ):
    template = get_first_template(wikicode, templatename)
    if not template:
        return pd.DataFrame()
    result = pd.DataFrame([['exists']], columns=['node_text'])
    result['section_id']   = zeile.section_id 
    result['section_id2']  = zeile.section_id2    
    result['merkmal']      = merkmal    
    return result   
    
    
    
# Liefert das erste Template mit dem angegebenen Namen
def get_first_template(wikicode, templatename):

    # try exact match
    match     = lambda node: (node.name==templatename)   # nimmt einen Node und liefert True oder False      
    templates = wikicode.filter_templates(recursive=False, matches=match)    
    if len(templates) > 0:
        return templates[0]    
    
    # try partial match    
    match = lambda node: (templatename in node.name)  # nimmt einen Node und liefert True oder False      
    templates = wikicode.filter_templates(recursive=False, matches=match)  
    if len(templates) > 0:
        return templates[0]       
    
    return None




# Liefert alle Templates mit dem angegebenen Namen
def get_all_templates(wikicode, templatename):

    match = lambda node: (templatename in node.name)  # nimmt einen Node und liefert True oder False  
    #match = lambda node: (node.name==templatename)   # nimmt einen Node und liefert True oder False  
    templates = wikicode.filter_templates(recursive=False, matches=match)    

    if len(templates) == 0:
        return None
    return templates



# Saugt alles aus einem bestimmten, per Template markierten Abschnitt
# und liefert es als Wikicode zurück
def extract_after_template(wikicode, templatename):
    result   = mwparserfromhell.wikicode.Wikicode(nodes=[])
    template = get_first_template(wikicode, templatename)
    raw      = None
    if template:  
        try:
            startindex = wikicode.index(template) # startindex
        except:
            return result
        for i in range(1, 1000):
            raw_pre = raw
            try:
                raw = wikicode.get( startindex + i)
            except IndexError:
                break
            if isinstance(raw, mwparserfromhell.nodes.template.Template)   and  str(raw_pre)[-1]  == '\n' :  # nächstes Template
                #print({str(raw_pre)[-1]})
                break  
            result.append(raw)

    return result    




# Nimmt einen Wikicode-Abschnitt und splittet ihn auf
# Liefert eine Liste von Node-Listen
def split_wikicode(wikicode):

    result = []
    re_liste_einzeln = re.compile('^\[[0-9, –\-]+\]$')  # Listeneintrag in einem eigenen Node    (Bsp.:Oberbegriffe von 'Haus')    
    re_liste_in_text = re.compile('^\[[0-9,\-– ]+\]')  # Listeneintrag am Anfang eines Text-Node (Bsp.:Bedeutungen von 'Haus')
    #print('hi2')

    # Schnittstellen kennzeichnen
    for node in wikicode.nodes:
        node_type  = type(node).__name__   # Tag, Text oder Wikilink   
        if node_type == 'Text': 
            text = node.value.strip()
            
            # Listeneintrag in einem eigenen Node
            if re_liste_einzeln.match(text):
                result.append(-77) # Schnittstelle kennzeichnen
                result.append(node)
                
            # Listeneintrag am Anfang eines Text-Node
            elif re_liste_in_text.match(text):
                result.append(-77) # Schnittstelle kennzeichnen
                zwei_teile = text.split(']', 1)
                teil_1 = mwparserfromhell.nodes.text.Text( zwei_teile[0] + ']' )
                teil_2 = mwparserfromhell.nodes.text.Text( zwei_teile[1].strip())  
                result.append(teil_1)
                result.append(teil_2)    
                #print('text=' + text, teil_1, teil_2)    
                
            # Normaler Text
            else:
                result.append(node)
                
        # Irgendwas anderes
        else:
            result.append(node)
        
    #return result

    output = []
    output.append([])
    for node in result:
        if node == -77:
            output.append([])  
        else:
            output[-1].append(node)

    return output         