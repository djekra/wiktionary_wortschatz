
import numpy      as np
import pandas     as pd 

import bpyth      as bpy
import pandasklar as pak 
import string

from termcolor import colored    


def search_str(df,find, without=[]):
    ''' Durchsucht die wichtigsten str-Spalten.
    '''
    if type(without) is str:
        without = [without]    
    without += [ 'tag','tag_0','tag_1','tagZ','tagZZ','member','doc_lemma','doc_tag','meta']
    return pak.search_str( df, find, without)   




def print_color(msg, color):
    if color:
        try:
            msg = colored(str(msg), color, attrs=['reverse','bold'])
        except:
            pass   
    print(msg)  
   
    

    
def ergänze_felder(df):
    '''
    Ergänzt die Felder lemma_lower, isupper, lemma_len
    '''
    df = df.copy()
    
    # lemma_lower
    df['lemma_lower']     = df.lemma.str.lower() 
    df = pak.move_cols(df,'lemma_lower', 'lemma')

    # isupper schreiben (Feld wurde nicht übernommen, das gab Probleme)
    df['isupper'] = df.lemma.str[0].str.isupper()

    # isupper: Ziffern am Anfang gelten auch als Großbuchstabe
    mask = df.lemma.str.contains('^[0-9]')
    pak.check_mask(df, mask, 0, 600)
    df.loc[mask,'isupper'] = True

    df = pak.move_cols(df,'isupper','lemma_lower')

    # lemma_len: Wie viele Wörter?
    df['lemma_len'] = df.lemma.str.split().str.len()
    df = pak.move_cols(df,'lemma_len','isupper')    
    
    return df
    

    
    
    
def pflege_tag_felder(df, translate_tagZ, feld='tag'):
    '''
    Schreibt die Felder tag_0, tag_1, tagZ, tagZZ.
    Braucht das Feld tag im DataFrame df.
    Parameter: Übersetzungstabelle translate_tagZ
    '''
    
    # alte Felder sicherheitshalber löschen
    df = pak.drop_cols(df,[ feld+'_0', feld+'_1', feld+'Z', feld+'ZZ'])    
    
    # reset_index
    df = df.reset_index(drop=True)    
    
    
    # Problem: zu viele tag  
    mask = (df[feld].str.count(' ') + 1)  > 2
    df.loc[mask,feld] = df[mask][feld].str.replace('PRO','',regex=False).str.strip()
    
    # Fehler: zu viele tag      
    mask = (df[feld].str.count(' ') + 1)  > 2    
    pak.check_mask( df, mask, 0, 10, verbose=False )    
    
    
    # Doppeltags splitten 
    try:
        df[[feld+'_0', feld+'_1']] = df[feld].str.split(' ', n=1, expand=True)
    except:
        print('Keine Doppeltags gefunden')
        df[feld+'_0'] = df[feld].copy()
        df[feld+'_1'] = None       
    df = pak.move_cols(df, [feld+'_0', feld+'_1'], feld)    
    
    
    # Übersetzungstabelle translate_tagZ anwenden
    df = pak.update_col( df, translate_tagZ, left_on=feld+'_0', right_on='tag', col='tagZ',  col_rename=feld+'Z',    verbose=False )
    df = pak.update_col( df, translate_tagZ, left_on=feld+'_0', right_on='tag', col='tagZZ', col_rename=feld+'ZZ_0', verbose=False )
    df = pak.update_col( df, translate_tagZ, left_on=feld+'_1', right_on='tag', col='tagZZ', col_rename=feld+'ZZ_1', verbose=False )
    
    df[feld+'ZZ'] = df[feld+'ZZ_0'].fillna('') + df[feld+'ZZ_1'].fillna('')
    df = pak.drop_cols(df,[feld+'ZZ_0',feld+'ZZ_1'])
    df = pak.move_cols(df, [feld+'Z',feld+'ZZ'], feld+'_1')   
    
    
    # tagZZ: Spaces und Doppelungen streichen
    t = { ' ':'',  'AX':'A', 'NX':'N', 'PX':'P', 'VX':'V', 'AP':'A', 'VA':'A', 'PV':'V',
         'AA':'A', 'NN':'N', 'VV':'V', 'PP':'P', 'PA':'P', 'XX':'X', 'XZ':'X', 'ZA':'Z', 'ZN':'Z', 'ZV':'Z', 'ZP':'Z', 'ZX':'Z', 'ZZ':'Z',}
    mask = (df[feld+'ZZ'].str.len() > 1)
    df.loc[mask,feld+'ZZ'] = pak.replace_str( df[mask][feld+'ZZ'], t)   
    mask = (df[feld+'ZZ'].str.len() > 1)  # immer noch
    if df[mask].shape[0] > 0:
        print('pflege_tag_felder Error:', df[mask].shape[0], 'Datensätze haben kein eindeutiges ' + feld + 'ZZ')
        #raise Exception(msg)
    #df.loc[mask,'tagZZ'] = df[mask].tagZZ.str[0] 
    
    def processNan(x):
        return bpy.random_str( size=10, mix=string.ascii_letters + '0123456789' )
    
    # random statt NaN oder leer
    for c in [feld+'_1']:
        df[c] = df[c].fillna('')
        df[c] = df[c].apply(lambda x: processNan(x) if x=='' else x)      
        
        
    # change_datatype
    for c in [feld, feld+'_0', feld+'_1', feld+'Z', feld+'ZZ']:
        df[c] = pak.change_datatype( df[c], 'str' )
        
    
    #df[c] = df[c].fillna(np.nan)
    
    # Alle tagZZ sind jetzt genau 1 Zeichen lang
    mask = (df[feld+'ZZ'].str.len() > 1)
    #check_mask(df, mask, 0, 0, verbose=False)    
    #print('#')
    return df



# Schreibt einen neuen tag
# stellt optional sicher, dass manuelle Quellen nicht überschrieben werden
#
def change_tag( df, mask, tag_neu, manuelle_kürzel, manuelle_quellen_schützen=True, feld='tag', ):
    
    mask_M = df.lemma_id.str.endswith(manuelle_kürzel)
    anz = df[mask_M & mask].shape [0]
    if anz > 0:
        print_color( str(anz) + ' manuelle Datensätze sollen überschrieben werden', color='red')
    if manuelle_quellen_schützen:
        assert anz == 0
        
    print( df[mask].shape[0], 'Datensätze')
    #df.loc[mask,'notiz'] = df[feld] + ' >> ' + tag_neu     
    df.loc[mask,feld]    = tag_neu       
        



def pflege_translate_tabelle(df, translate_tagZ, wiktionary_lemma, translate_lex=None ):
    
    # vorher sicherheitshalber löschen
    result = pak.drop_cols(df, ['lemma_tag', 'lemma_tagZZ','lemma_lower', ])
    
    if translate_lex is not None:    
        
        translate_lex_ranked  = pak.rank(translate_lex, col_score='score', cols_group='data_id', on_conflict='first')
        
        # lemma_home
        result['lemma_home'] = ''

        # lemma_id ist in wiktionary_lemma
        mask1 =  result.lemma_id.isin(wiktionary_lemma.lemma_id)
        mask2 = ~result.lemma_id.isin(translate_lex_ranked.data_id)
        mask = mask1  &  mask2
        result.loc[mask,'lemma_home'] = 'L'

        # lemma_id ist in translate_lex_ranked
        mask1 = ~result.lemma_id.isin(wiktionary_lemma.lemma_id)
        mask2 =  result.lemma_id.isin(translate_lex_ranked.data_id)
        mask = mask1  &  mask2
        result.loc[mask,'lemma_home'] = 'T'

        # lemma_id ist in beiden Tabellen
        mask1 = result.lemma_id.isin(wiktionary_lemma.lemma_id)
        mask2 = result.lemma_id.isin(translate_lex_ranked.data_id)
        mask = mask1  &  mask2
        result.loc[mask,'lemma_home'] = 'B'   

        if 'data_id' in result.columns:
            # data_home
            result['data_home'] = ''

            # data_id ist in wiktionary_lemma
            mask1 =  result.data_id.isin(wiktionary_lemma.lemma_id)
            mask2 = ~result.data_id.isin(translate_lex_ranked.data_id)
            mask = mask1  &  mask2
            result.loc[mask,'data_home'] = 'L'

            # data_id ist in translate_lex_ranked
            mask1 = ~result.data_id.isin(wiktionary_lemma.lemma_id)
            mask2 =  result.data_id.isin(translate_lex_ranked.data_id)
            mask = mask1  &  mask2
            result.loc[mask,'data_home'] = 'T'

            # data_id ist in beiden Tabellen
            mask1 = result.data_id.isin(wiktionary_lemma.lemma_id)
            mask2 = result.data_id.isin(translate_lex_ranked.data_id)
            mask = mask1  &  mask2
            result.loc[mask,'data_home'] = 'B'      

            # data aus translate_lex_ranked
            result = pak.update_col(result,          
                                    translate_lex_ranked,
                                    on='data_id',
                                    col='data',
                                   )            
    
    # Mit oder ohne translate_lex_ranked 
    # lemma aus wiktionary_lemma
    result = pak.update_col(result,          
                            wiktionary_lemma,
                            on='lemma_id',
                            col='lemma' 
                           )
    
    if 'data_id' in result.columns:
        # data aus wiktionary_lemma
        result = pak.update_col(result,          
                                wiktionary_lemma,
                                left_on='data_id',
                                right_on='lemma_id',
                                col='lemma',
                                col_rename='data'
                               )    
        
        
        # data_tagZZ aus wiktionary_lemma
        result = pak.update_col(result,          
                                wiktionary_lemma,
                                left_on='data_id',
                                right_on='lemma_id',
                                col='tagZZ',
                                col_rename='data_tagZZ',
                                cond='null'
                               )       
        result['data_tagZZ'] = result.data_tagZZ.fillna('')        
        
    
    # lemma_tag aus wiktionary_lemma
    result = pak.update_col(result,
                            wiktionary_lemma, 
                            on='lemma_id',
                            col='tag', # rename später
                           )
    
    # score aus wiktionary_lemma
    result = pak.update_col(result,          
                            wiktionary_lemma,
                            on='lemma_id',
                            col='score',
                            col_rename='lemma_score'
                           )      

    result = pflege_tag_felder(result, translate_tagZ)
    result = pak.drop_cols(result, ['tag_0', 'tag_1', 'tagZ']) # wir wollen nur tagZZ, alles andere direkt wieder löschen      
    result = pak.rename_col(result, 'tag','lemma_tag')  
    result = pak.rename_col(result, 'tagZZ','lemma_tagZZ')  
    if 'score' in result.columns and not 'data_score' in result.columns:
        print('renaming score --> data_score')
        result = pak.rename_col(result, 'score','data_score')      
    
    result['lemma_lower']  = result.lemma.str.lower() 
    result = pak.move_cols(result, ['data_id','data_home','data','data_tag','data_tagZZ','data_score','member','lemma_id','lemma_home','lemma','lemma_tag','lemma_tagZZ','lemma_score'])
    result = pak.reset_index(result)
    return result
    
    

def set_translate_lex_score(translate_lex, lexeme_manuell):
    
    translate_lex['f1'] = 1 + translate_lex.data_id.str.count('_')  * translate_lex.data_id.str.count('_')
    translate_lex['f2'] = 1 + translate_lex.lemma_id.str.count('_') * translate_lex.lemma_id.str.count('_')    
    
    translate_lex['score'] = translate_lex.score.fillna(0)              
    mask = translate_lex.score == 0
    print(translate_lex[mask].shape[0],'Datensätze werden neu bewertet')
    translate_lex.loc[mask,'score'] = (translate_lex[mask].lemma_score * 4.0 + translate_lex[mask].data_score)  /  translate_lex[mask].f1  /  translate_lex[mask].f2
    #translate_lex.loc[mask,'score'] /= translate_lex[mask].f1
    #translate_lex.loc[mask,'score'] /= translate_lex[mask].f2
    #translate_lex.loc[mask,'score'] /= translate_lex[mask].f1
    #translate_lex.loc[mask,'score'] /= translate_lex[mask].f2    
    
    mask2 = translate_lex.data_id.str.endswith('_1')
    translate_lex.loc[mask & mask2,'score'] /= 2
    mask2 = translate_lex.data_id.str.endswith('_2')
    translate_lex.loc[mask & mask2,'score'] /= 3    
    mask2 = translate_lex.data_id.str.endswith('_3')
    translate_lex.loc[mask & mask2,'score'] /= 4   
    mask2 = translate_lex.data_id.str.endswith('_4')
    translate_lex.loc[mask & mask2,'score'] /= 5        
    mask2 = translate_lex.data_id.str.endswith('_5')
    translate_lex.loc[mask & mask2,'score'] /= 6   
    mask2 = translate_lex.data_id.str.endswith('_6')
    translate_lex.loc[mask & mask2,'score'] /= 7       

    mask2 = translate_lex.lemma_id.str.endswith('_1')
    translate_lex.loc[mask & mask2,'score'] /= 2
    mask2 = translate_lex.lemma_id.str.endswith('_2')
    translate_lex.loc[mask & mask2,'score'] /= 3    
    mask2 = translate_lex.lemma_id.str.endswith('_3')
    translate_lex.loc[mask & mask2,'score'] /= 4   
    mask2 = translate_lex.lemma_id.str.endswith('_4')
    translate_lex.loc[mask & mask2,'score'] /= 5        
    mask2 = translate_lex.lemma_id.str.endswith('_5')
    translate_lex.loc[mask & mask2,'score'] /= 6   
    mask2 = translate_lex.lemma_id.str.endswith('_6')
    translate_lex.loc[mask & mask2,'score'] /= 7   
    
    mask = pak.isin(translate_lex, lexeme_manuell, left_on=['data','lemma'],right_on=['lex','lemma'])
    translate_lex.loc[mask,'score'] += 2
    translate_lex.loc[mask,'score'] *= 20

    mask = pak.isin(translate_lex, lexeme_manuell, on=['lemma','lemma_tag'])
    translate_lex.loc[mask,'score'] += 1
    translate_lex.loc[mask,'score'] *= 10    
    
    translate_lex = pak.drop_cols(translate_lex,['f1','f2'])
    return translate_lex



# Morphologische Analyse    
#    
#
def analyze_hunspell(zeile, col_check, col_result, hunspellinstance):
    ''' 
    df.apply(analyze_hunspell, col_check='A', col_result='B', hunspellinstance=hun, axis=1)
    '''
    try:
        result = list(hunspellinstance.analyze(zeile[col_check]))
        zeile[col_result] = result    
        #zeile[col_result] = hunspellinstance.analyze(zeile[col_check])
    except:
        pass 
    return zeile


# Rechtschreibprüfung    
#    
def verify_hunspell(zeile, col_check, col_result, hunspellinstance):
    ''' 
    liefert 1=verifiziert, 0=nicht verifiziert, -1=Besonderes Unicode-Zeichen
    df.apply(verify_hunspell, col_check='A', col_result='B', hunspellinstance=hun, axis=1)
    '''
    try:
        if hunspellinstance.spell(zeile[col_check]):
            zeile[col_result] = 1
        else:
            zeile[col_result] = 0
    except UnicodeEncodeError:
        zeile[col_result] = -1               # Sonderzeichen  
    return zeile









# Lädt die Lexeme zum Testen der Ergebnisse
#
def lade_lex_text(lex_test_filename, level):
    
    lex_test = pak.load_excel( lex_test_filename )   
    lex_test['level'] = lex_test.level.fillna(0)    
    mask = lex_test.level > level
    lex_test = pak.drop_rows(lex_test,mask)
    lex_test = lex_test.fillna('')
    
    mask = lex_test.lemma == ''
    lex_test.loc[mask,'lemma'] = lex_test[mask].lex

    mask = lex_test.lemma_tag == ''
    lex_test.loc[mask,'lemma_tag'] = lex_test[mask].lex_tag  
    
    spalten = ['lemma','lemma_tag','member','level']
    lemma_test = pak.reset_index(lex_test[spalten].drop_duplicates())
    
    lemma_test = pak.rename_col(lemma_test,'lemma_tag','tag_soll')
    lemma_test = pak.rename_col(lemma_test,'member',   'member_soll')
    lemma_test = pak.move_cols(lemma_test,'level')
    lemma_test['check_tag'] = ''

    lex_test = pak.rename_col(lex_test,'lex_tag',  'lex_tag_soll')
    lex_test = pak.drop_cols(lex_test,['lemma_tag','member','quelle','def'])
    lex_test = pak.move_cols(lex_test,'level')
    lex_test['check_tag'] = ''    
    
    return lex_test, lemma_test




def check_lemma_test(lemma_test, wiktionary_lemma):
    
    if 'section_id2' in wiktionary_lemma.columns:
        wiktionary_lemma = pak.rename_col(wiktionary_lemma,'section_id2','lemma_id')

    ## lemma und tag_0  -->  lemma_id 
    lemma_test, mask = pak.update_col(lemma_test, 
                                      wiktionary_lemma, 
                                      left_on=[ 'lemma','tag_soll'], 
                                      right_on=['lemma','tag_0'], 
                                      col='lemma_id', 
                                      col_score='score', 
                                      cond='null', 
                                      return_mask=True,
                                      verbose=False)
    lemma_test.loc[mask,'check_tag'] = 'OK'

    ## lemma und tag_1  -->  lemma_id 
    lemma_test, mask = pak.update_col(lemma_test, 
                                      wiktionary_lemma, 
                                      left_on=[ 'lemma','tag_soll'], 
                                      right_on=['lemma','tag_1'], 
                                      col='lemma_id', 
                                      col_score='score', 
                                      cond='null', 
                                      return_mask=True,
                                      verbose=False)
    lemma_test.loc[mask,'check_tag'] = 'OK'

    ## lemma -->  lemma_id 
    lemma_test = pak.update_col(lemma_test, 
                                wiktionary_lemma, 
                                left_on=[ 'lemma'], 
                                right_on=['lemma'], 
                                col='lemma_id', 
                                col_score='score', 
                                cond='null',
                                verbose=False)

    # tag_ist
    lemma_test = pak.update_col(lemma_test, 
                                wiktionary_lemma, 
                                on='lemma_id', 
                                col='tag', 
                                col_rename='tag_ist',
                                col_score='score', 
                                verbose=False)
    
    # member_ist
    lemma_test = pak.update_col(lemma_test, 
                                wiktionary_lemma, 
                                on='lemma_id', 
                                col='member', 
                                col_rename='member_ist',
                                col_score='score', 
                                verbose=False)
    
    lemma_test = pak.move_cols(lemma_test,'lemma_id','level')
    lemma_test = pak.move_cols(lemma_test,'tag_ist','tag_soll')
    lemma_test = lemma_test.fillna('')
    
    # check_tag
    def check_tag(zeile):
        if zeile.check_tag != '':
            return zeile
        if zeile.tag_soll == zeile.tag_ist:
            zeile.check_tag = 'OK'    
        elif zeile.tag_soll in zeile.tag_ist:
            zeile.check_tag = 'ok'
        return zeile    

    # Zeilenweise anwenden
    lemma_test = lemma_test.apply(check_tag, axis=1)    
    
    # check_member
    def check_member(zeile):
        if len(zeile.member_soll) == 0:
            zeile.check_member = 'ok'
        elif zeile.member_soll in zeile.member_ist:
            zeile.check_member = 'OK'
        return zeile    

    # Zeilenweise anwenden
    lemma_test['check_member'] = ''
    lemma_test = lemma_test.apply(check_member, axis=1)    
    
    return lemma_test





def check_lex_test(lex_test, translate_lex):

    # data und data_tag_0  -->  lex_id 
    lex_test, mask = pak.update_col(lex_test, 
                                    translate_lex, 
                                    left_on=[ 'lex', 'lex_tag_soll'], 
                                    right_on=['data','data_tag_0'], 
                                    col='data_id', 
                                    col_rename='lex_id', 
                                    col_score='score', 
                                    return_mask=True,
                                    verbose=False)
    lex_test.loc[mask,'check_tag'] = 'OK'

    # data und data_tag_1  -->  lex_id 
    lex_test, mask = pak.update_col(lex_test, 
                                    translate_lex, 
                                    left_on=[ 'lex', 'lex_tag_soll'], 
                                    right_on=['data','data_tag_1'], 
                                    col='data_id', 
                                    col_rename='lex_id', 
                                    col_score='score', 
                                    cond='null', 
                                    return_mask=True,
                                    verbose=False)
    lex_test.loc[mask,'check_tag'] = 'OK'

    # data -->  lex_id 
    lex_test = pak.update_col(lex_test, 
                              translate_lex, 
                              left_on=[ 'lex'], 
                              right_on=['data'], 
                              col='data_id', 
                              col_rename='lex_id', 
                              col_score='score', 
                              cond='null',
                              verbose=False)

    # lex_id  -->  data_tag
    # lex_id  -->  lemma_ist
    lex_test = pak.update_col(lex_test, translate_lex, left_on='lex_id', right_on='data_id', col='data_tag', col_rename='lex_tag_ist', col_score='score',verbose=False)
    lex_test = pak.update_col(lex_test, translate_lex, left_on='lex_id', right_on='data_id', col='lemma',    col_rename='lemma_ist',   col_score='score',verbose=False)

    lex_test = pak.move_cols(lex_test,'lex_id','level')
    lex_test = pak.move_cols(lex_test,'lex_tag_soll','lex')
    lex_test = pak.move_cols(lex_test,'lex_tag_ist','lex_tag_soll')
    lex_test = pak.move_cols(lex_test,'lemma_ist','lemma')   
    lex_test = lex_test.fillna('')
    
    # check_tag_lex
    def check_tag_lex(zeile):
        if zeile.check_tag != '':
            return zeile    
        if zeile.lex_tag_soll == zeile.lex_tag_ist:
            zeile.check_tag = 'OK'    
        elif zeile.lex_tag_soll in zeile.lex_tag_ist:
            zeile.check_tag = 'ok'
        return zeile    

    # Zeilenweise anwenden
    lex_test = lex_test.apply(check_tag_lex, axis=1)    

    return lex_test




# Lemma finden
#
# DERZEIT NICHT VERWENDET
#
def find_lemma(zeile, col, pos, col_result, germalemmainstance):
    ''' 
    df.apply(find_lemma, col='lemma', pos='ADJ', col_result='lemma_ger', germalemmainstance=lemmatizer, axis=1)
    '''     
    lemma = germalemmainstance.find_lemma(zeile[col], pos)
    zeile[col_result] = lemma
    
    return zeile