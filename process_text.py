# coding=utf-8
# elaborated by vicramgon

# Librerías
import os
from io import open
import re
import sys

################################################################################
# FUNCIONES                                                                    #
################################################################################

def tokenize(sent, puncts=[',', '.', ';', ':', '?', '!']):
  """
    Corresponde a la función de tokenización de frases con respecto a un conjunto 
    de símbolos de puntuación. Esta tokenización considera todos los caracteres
    en su versión minúscula (si existe). No considera los espacios como tokens

    Parámetros
    ----------
    sent : str
        La frase de entrada para la tokenización

    puncts : list(str), optional
        El conjunto símbolos considerados como símbolos de puntuación. El valor 
        por defecto es [',', '.', ';', ':', '?', '!']

    Salida
    ------
    list(str)
        La lista de tokens asociado.

  """
  # Inicializamos una lista vacía que contendrá, en cada paso, los tokens
  # completos procesados hasta el momento.
  res = []

  # Se inicializa una cadena vacía que contendrá, en cada paso, la secuencia
  # parcial de caractéres de la cadena del token en procesamiento. 
  partial = ''

  # Guardamos el tipo de datos del último carácter de partial
  # que lo identifica como numérico o no numérico (cadena)
  cur_read_type = None
  
  # En cada paso (hasta terminar de procesar todos los caracteres de la cadena)
  for i in range(len(sent)):
    
    # Se lee el carácter i-ésimo de la cadena
    c_i = sent[i] 
    
    # Si dicho carácter corresponde a un espacio o a un signo de puntuación
    # entonces, el token que estábamos procesando finaliza, luego
    if c_i == ' '  or c_i in puncts:
      
      # Ha de añadirse (junto al signo de corte), como nuevos tokens.
      # Sólo se añadirá no es vacío ( si no corresponde al espacio, resp.). 
      res += list(filter(lambda x: x.strip() != '', [partial.lower(), c_i]))
      
      # Y reseteamos la cadena parcial de token a vacío
      partial = ''
      cur_read_type = None
    
    # En otro caso, 
    else:
      # Añadimos el carácter a la cadena parcial del token procesamiento
      # si los tipos no coinciden entendemos que corresponden a cadenas distintas
      # Y por ende, partimos guardamos el token anterior e inicializamos uno nuevo
      # con el carácter leído y su tipo
      if (c_i.isdigit()):
          if(cur_read_type == 'string'):
            res += [partial.lower()]
            partial = ''
              
          cur_read_type = 'number'
      
      else:
          if(cur_read_type == 'number'):
            res += [partial.lower()]
            partial = ''
   
          cur_read_type = 'string'
      
      
      partial += c_i
    
    #Se continúa el procesamiento del siguiente carácter.
  
  # El token leído en última instancia es añadido a la lista de tokens (siempre
  # que no sea vacío)
  res += [partial.lower()] if partial.strip() != '' else []

  # Finalmente, se devuelve la lista de tokens
  return res

  # Nótese que se consideran todas las cadenas en minúscula



def tokenize2(sent, puncts={".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}):
  """
    Corresponde a la función de tokenización de frases con respecto a un conjunto 
    de símbolos de puntuación, considera además los espacios como tokens

    Parámetros
    ----------
    sent : str
        La frase de entrada para la tokenización

    puncts : dict(str, str), optional
        Un diccionario con los símbolos originales y los respectivos tokens. El
        valor por defecto es {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}

    Salida
    ------
    list(str)
        La lista de tokens asociado.

  """

  # Inicializamos una lista vacía que contendrá, en cada paso, los tokens
  # completos procesados hasta el momento.
  res = []

  # Se inicializa una cadena vacía que contendrá, en cada paso, la secuencia
  # parcial de caractéres de la cadena del token en procesamiento. 
  partial = ''

  # Reading type
  cur_read_type = None
  
  # En cada paso (hasta terminar de procesar todos los caracteres de la cadena)
  for i in range(len(sent)):
    
    # Se lee el carácter i-ésimo de la cadena
    c_i = sent[i] 
    
    # Si dicho carácter corresponde a un espacio o a un signo de puntuación
    # entonces, el token que estábamos procesando finaliza, luego
    if c_i == ' ' or c_i in puncts:
      
      # Ha de añadirse (junto al signo de corte), como nuevos tokens.
      # Sólo se añadirá no es vacío ( si no corresponde al espacio, resp.).
      if partial:
        res.append(partial)
         
      res.append(puncts[c_i] if c_i != ' ' else c_i)
      
      # Y reseteamos la cadena parcial de token a vacío
      partial = ''
      cur_read_type = None
    
    # En otro caso, 
    else:
      # Añadimos el carácter a la cadena parcial del token procesamiento
      # si los tipos no coinciden entendemos que corresponden a cadenas distintas
      # Y por ende, partimos guardamos el token anterior e inicializamos uno nuevo
      # con el carácter leído y su tipo
      if (c_i.isdigit()):
          if(cur_read_type == 'string'):
            res += [partial]
            partial = ''
              
          cur_read_type = 'number'
      
      else:
          if(cur_read_type == 'number'):
            res += [partial]
            partial = ''
   
          cur_read_type = 'string'
      
      
      partial += c_i
    
    #Se continúa el procesamiento del siguiente carácter.
  
  # El token leído en última instancia es añadido a la lista de tokens (siempre
  # que no sea vacío)
  res += [partial] if partial.strip() != '' else []

  # Finalmente, se devuelve la lista de tokens
  return res 

def process_line(line, puncts= {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}):
    """
      Corresponde a la función de procesamiento de una linea o cadena del fichero.
      Realiza la tokenización de la frase, con los términos en minúscula, tokenización
      de los números, y elimina los signos de puntuación consecutivos. Se marca
      el final del linea con un token de final de linea, "<BREAK>".

      Parámetros
      ----------
      line : str
          La frase de entrada para la tokenización

      puncts : dict(str, str), optional
        Un diccionario con los símbolos originales y los respectivos tokens. El
        valor por defecto es {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}

      Salida
      ------
        str
          La cadena con los elementos tokenizados.

    """
    # Se tokeniza la frase
    tokens =  tokenize(line.strip(), puncts=puncts)

    # Se crea una lista que almacenará los tokens finales
    output_tokens = []
    prev_token = 'null'

    # Para cada token
    for token in tokens:
        # Si el token es un signo de puntuación
        if token in puncts:
            # si el token anterior no era de puntuación
            if  prev_token not in puncts:
                # Se añade el nuevo token al conjunto final de tokens
                output_tokens.append(puncts[token])

            # En otro caso, el token se descarta
        
        # Si el token es numérico entonces se le asigna el token de numeración
        # "<NUM>"
        elif re.fullmatch('\d+', token):
            output_tokens.append("<NUM>")
        
        # Si no, el token corresponde a una cadena, que es guardada como token 
        # final (en minúscula)
        else:
            output_tokens.append(token.lower())
        
        # Se actualiza el último token leído
        prev_token = token

    # Se devuelve la cadena finalizada por un token de final de linea
    return " ".join(output_tokens + ["<BREAK>"])




def process_line2(line, puncts= {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}):
    """
      Corresponde a la función de procesamiento de una linea o cadena del fichero.
      Realiza la tokenización de la frase, manteniendo mayúsculas, tokenización 
      de los números, y eliminación de signos de puntuación, al inicio de la linea, 
      consecutivos y aquellos que no estén separados por algún espacio y separen
      elementos del mismo distinto tipo. Se marca el final del linea con un token 
      de final de linea, "<BREAK>".

      Parámetros
      ----------
      line : str
          La frase de entrada para la tokenización

      puncts : dict(str, str), optional
        Un diccionario con los símbolos originales y los respectivos tokens. El
        valor por defecto es {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}

      Salida
      ------
        str
          La cadena con los elementos tokenizados.

    """
    # Tomamos el conjunto de los tokens asociados a los s'imbolos de puntuación
    PUNCTS = puncts.values()

    # Se tokeniza la frase (manteniendo los espacios y las mayúsculas)
    tokens = tokenize2(line.strip(), puncts=puncts)

    # Se inicializa una memoria que almacenará los tokens finales
    output_tokens = []

    # Se mantiene un supervisor que indica si el último elemento leído es un signo
    # de puntuación. 
    # Al considerarlo verdadero de base, si hay tokens al inicio de la linea se eliminan
    last_is_punct = True

    # Se mantiene un supervisor que indica si hay que unir los tokens porque 
    # son del mismo tipo y están separados por signos de puntuación sin espacios
    union = False

    # Para cada token
    i=0
    while i < (len(tokens)):
        # Si corresponde a un signo de puntuación
        if tokens[i] in PUNCTS:
            # y el último leído no es también signo de puntuación (e.o.c. se descarta)
            if not last_is_punct:
                # y no está separado por algún espacio
                if  (i > 0) and (tokens[i-1] != ' ') and (i + 1 < len(tokens)) and (tokens[i+1] !=' '):
                  # pero separa elementos de distinto tipo (e.o.c se descarta)
                  if (output_tokens[-1][-1].isdigit() and tokens[i+1][0].isdigit()) or  (not(output_tokens[-1][-1].isdigit()) and not(tokens[i+1][0].isdigit()) and tokens[i+1] not in PUNCTS) :
                      union = True
                
                # os está separado por algún espacio a izquierda o derecha
                else:
                    output_tokens.append(tokens[i])
                    last_is_punct = True
                    union = False
        # Si el token leído no es un signo de puntuación, entonces
        elif tokens[i] != ' ':
            # Se une al anterior si el supervisor lo indica
            if union:
                output_tokens[-1] += tokens[i]
            # En otro caso, se añade como token nuevo
            else:
                output_tokens.append(tokens[i])
            
            # Se actualizan los valores de los supervisores
            last_is_punct = False
            union = False
        
        # Se continúa con el procesamiento del siguiente token
        i += 1

    # Se devuelve la cadena de los tokens finales con el token de final de línea
    return " ".join(output_tokens)


def clear_endbreak_line(line):
  """
    Elimina el token de final de linea de la frase dada.

    Parámetros
    ----------
    line : str
        La frase de entrada
    Salida
    ------
      str
        La frase sin el token de final de linea

  """
  # Se devuelve la cadena eliminando el final de línea.
  return re.sub('<BREAK>|<break>' , '', line.strip())
