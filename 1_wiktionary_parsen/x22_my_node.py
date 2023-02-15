import re
import string

# Klasse zum Auswerten von mwparserfromhell.Wikicode
class myNode():
    
    def __init__(self, node_type='init', node_text=''):
        self.node_type    = node_type
        self.node_num     = []         # Falls node_type == Nummerierung: Die Nummerierung        
        self.node_link    = ''         # Verweis auf eine Seite
        self.node_text    = node_text  # Einfach nur Text  
        self.node_meta    = ''         # Meta-Anmerkungen
        self.node_kontext = ''         # Hier wird Kontext 'nach oben' hochbefördert. 'Ü' kennzeichnet Übersetzungen.      
        self.löschmich    = False      # Kennzeichnung, ob der Node sinnlos ist
        self.node_debug   = ''         # hier wird Information zum Debuggen durchgeschleift     
    
    
    
    # für print
    def __repr__(self):
        result = ''
        if self.löschmich:
            result += 'DEL'         
        if self.node_type == 'Text': 
            result += '♒ '
        elif self.node_type == 'Nummerierung': 
            result += '🔢 '         
        elif self.node_type == 'NewLine': 
            result += '␤'               
        elif self.node_type == 'Wikilink': 
            result += '⮕ ' 
        elif self.node_type == 'Tag': 
            result += '☔ '             
        elif self.node_type == 'Template': 
            result += '⭕ '   
        else:
            result += '✧ ' + self.node_type               
            
        if len(self.node_num) != 0:
            result += '⢎' + str(self.node_num)               
        if self.node_meta != '':
            result += '☯' + self.node_meta            
        if self.node_link != '':
            result += '→' + self.node_link
        if (self.node_text != '')  and  (self.node_text != self.node_link):
            result += '☷' + str(self.node_text)  
        if self.node_kontext != '':
            result += '☕' + self.node_kontext             
        if self.node_debug != '':
            result += '❓' + self.node_debug            
             
        return result
        
    
    def aslist(self):
        return [  self.node_num, 
                  self.node_meta,
                  self.node_link, 
                  self.node_text,
                  self.node_kontext,
                  self.node_debug      ]
    
    
    
    
    # Nimmt einen einzelnen mwparserfromhell-Node und analysiert ihn
    # liefert einen myNode, der das Ergebnis enthält
    def analyze(self, node=None):
        if node:
            self.node = node
            self.node_type = type(node).__name__   # Tag, Text, Wikilink, Template 
        self.node_num     = []    # Falls node_type == Nummerierung: Die Nummerierung            
        self.node_link    = ''    # Verweis auf eine Seite
        self.node_text    = ''    # Einfach nur Text  
        self.node_meta    = ''    # Meta-Anmerkungen
        self.node_kontext = ''    # Hier wird Kontext 'nach oben' hochbefördert. Z.B. für Check auf Meta      
        self.löschmich    = False # Kennzeichnung, ob der Node sinnlos ist
        self.node_debug   = ''    # hier wird Information zum Debuggen durchgeschleift     
              
        # Text
        if self.node_type == 'Text': 
            if node.value == '\n':
                self.node_type = 'NewLine'
            self.node_text = node.value.strip()
            
            
            # Nummerierung
            re_liste  = re.compile('^\[[0-9, –\-]+\]$')  # Normaler Listeneintrag (Bsp.:Oberbegriffe von 'Haus')       
            if re_liste.match(self.node_text):
                self.node_type = 'Nummerierung'
                self.node_num  = myNode.nummerierung_to_list(self.node_text)   
                self.node_text = ''
                             
        
        # Wikilink
        elif self.node_type == 'Wikilink': 
            
            if node.title: # verlinkter Begriff
                self.node_link = str(node.title)
                self.node_text = str(node.title)
            if node.text: # Soll was Abweichendes angezeigt werden?
                self.node_text = str(node.text) 
                
        # Template
        elif self.node_type == 'Template':
            
            name = str(node.name) # z.B. 'Ü'
            params = node.params  # z.B. ['goh', 'hūs']
            #self.node_debug = 'Template name={0} params={1} source={2}'.format(name, params, str(node)) 

            if name == 'K': # kursiv
                try:
                    name             = params[0]   # z.B. {{K|ugs.}}
                    self.node_meta   = params[0]   # z.B. {{K|gehoben}}
                    self.node_debug  = ''
                except:
                    self.node_debug = 'Template name={0} params={1} source={2}'.format(name, params, str(node)) 
                
            if name == 'Ü': # Übersetzungen
                try:
                    self.node_text    = params[1]
                    self.node_kontext = 'Ü' 
                    self.node_debug   = ''
                except:
                    self.node_debug = 'Template name={0} params={1} source={2}'.format(name, params, str(node))                     
            elif name == 'ugs.':
                self.node_meta    = 'umgangssprachlich'
                self.node_debug   = ''       
            elif name == 'va.':  
                self.node_meta    = 'veraltet'             
                self.node_debug   = ''  
            elif name == 'österr.':  
                self.node_meta    = 'österreichisch'             
                self.node_debug   = '' 
            elif name == 'CH&LI':  
                self.node_meta    = 'schweizerisch'             
                self.node_debug   = ''  
            elif name == 'schweiz.':  
                self.node_meta    = 'schweizerisch'             
                self.node_debug   = ''                  
            elif name == 'vatd.':  
                self.node_meta    = 'veraltend'             
                self.node_debug   = ''  
            elif name == 'landsch.':  
                self.node_meta    = 'landschaftlich'             
                self.node_debug   = ''   
            elif name == 'übertr.':  
                self.node_meta    = 'übertragen'             
                self.node_debug   = '' 
            elif name == 'abw.':  
                self.node_meta    = 'abwertend'             
                self.node_debug   = ''      
            elif name == 'intrans.':  
                self.node_meta    = 'intransitiv'             
                self.node_debug   = ''   
            elif name == 'trans.':  
                self.node_meta    = 'transitiv'             
                self.node_debug   = ''  
            elif name == 'geh.':  
                self.node_meta    = 'gehoben'             
                self.node_debug   = ''                  
            elif name == 'scherzh.':  
                self.node_meta    = 'scherzhaft'             
                self.node_debug   = ''
            elif name == 'refl.':  
                self.node_meta    = 'reflexiv'             
                self.node_debug   = ''                        
            elif name == 'fachspr.':  
                self.node_meta    = 'fachsprachlich'             
                self.node_debug   = ''  
            elif name == 'fam.':  
                self.node_meta    = 'familiär'             
                self.node_debug   = ''                      
                
            else:
                self.node_meta    = name                             

        # Tag- Also z.B. eine Formatierung, oder auch '<ref name="DudenOnline"/>'        
        elif self.node_type == 'Tag': 
                            
            # Inhalt untersuchen und das erste Element hochbefördern
            children = self.node.contents
            if len(children) > 0:
                
                # Ersten Text nehmen
                nodes = children.filter_text() 
                if len(nodes) > 0:
                    node_0 = myNode().analyze(nodes[0])  #node_0 = myNode(nodes[0])
                    self.node_text    = node_0.node_text 
                    self.node_kontext = node_0.node_kontext                      
                    self.node_debug   = node_0.node_debug                       
                    #print('Text', self.node_text)
                    
                # Ersten Wikilink nehmen und dabei ggf. das bisherige Ergebnis überschreiben
                nodes = children.filter_wikilinks()
                if len(nodes) > 0:
                    node_0 = myNode().analyze(nodes[0])
                    self.node_link    = node_0.node_link
                    self.node_text    = node_0.node_text  
                    self.node_kontext = node_0.node_kontext                        
                    self.node_debug   = node_0.node_debug                       
                    #print('Wikilink')                    
                
                # Erstes Template nehmen und dabei ggf. das bisherige Ergebnis überschreiben
                nodes = children.filter_templates()
                if len(nodes) > 0:
                    node_0 = myNode().analyze(nodes[0])
                    self.node_link    = node_0.node_link
                    self.node_text    = node_0.node_text 
                    self.node_kontext = node_0.node_kontext                        
                    self.node_debug   = node_0.node_debug                     
                    #print('Template', str(node_0)                       
                        
            # löschmich
            elif self.node.tag == 'ref':
                self.node_debug = 'ref'
                self.löschmich  = True                        
                        
            else: # irgendein anderer Tag, wahrscheinlich leer
                if str(node) != '':
                    self.node_debug = 'str(node)=' + str(node)                    
                self.löschmich = True
            
            # Check auf Meta
            # Keine Übersetzung und kursiv 
            if (self.node_kontext != 'Ü')  and  ((self.node.wiki_markup == "''")  or  (self.node.wiki_markup == "'''''")): 
                self.node_meta = self.node_text
                self.node_text = '' 
                self.node_link = ''    
                                                
        return self
    

    
    
    
    # reinigen
    def cleanup(self, collect_text=False):

        if self.node_type == 'NewLine':
            return self
        
        # Wikipedia-Links: Den Text stattdessen nehmen
        if self.node_link.startswith('w:'): 
            self.node_link = self.node_text
          
        # verbotene Wörter in meta streichen
        if self.node_meta and len(self.node_meta) > 0:    
            verboten =  ['zumeist ', 'nach ', 'in ', 'Bei ', 'bei ', 'nur ', '1996 ', 'seit ', 'meist ', 'mit ', 'ohne ']
            verboten += ['auch ', 'als ', 'kein ', 'sich ', 'von ', 'siehe ',]
            pattern = re.compile(r'\b(' + r'|'.join(verboten) + r')\b\s*')
            #pattern = r'\b(?:{})\b'.format('|'.join(verboten))   # 
            #print('self.node_meta', self.node_meta)
            self.node_meta = pattern.sub('', str(self.node_meta))  
            self.node_meta = self.node_meta.strip()
            self.node_meta = self.node_meta.split()[0]            
            
        if not collect_text:    
            self.node_link  = myNode.reinige_text(self.node_link)        
            self.node_text  = myNode.reinige_text(self.node_text) 
            self.node_meta  = myNode.reinige_text(self.node_meta)
            self.node_debug = self.node_debug.strip() 

        
        # löschmich
        if not collect_text  and  (len(self.node_text + self.node_meta) < 3)  and   (self.node_type != 'Nummerierung'):
            self.löschmich = True   
            
        return self

    
    
##############################################################################                
###
### Hilfsmethoden
###
##############################################################################   


    # Hilfsmethode für cleanup
    @staticmethod
    def reinige_text(text):
        text = text.rstrip(string.punctuation)
        text = text.strip()           
        text = text.strip("‚‘»«„“")           
        text = text.strip()   
        return text    


    # Nimmt eine Nummerierung der Form [1, 3-7, 15] an 
    # liefert eine Liste
    @staticmethod
    def nummerierung_to_list(text):
        text = text.replace('-','–').strip(string.punctuation + ' ').split(',')
        result = []
        for portion in text:
            if not portion:
                continue
            try:
                # Einzelne Zahl
                result.append(int(portion))
            except ValueError:
                # Bereich 
                intervall = portion.strip().split('–')
                try:
                    von = int(intervall[0])
                    bis = int(intervall[-1])
                    result += list(range(von, bis+1))
                except ValueError:
                    print('ERROR'+portion+'ERROR')

        
        result = list(set(result))
        result.sort()
        return result
