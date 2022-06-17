# coding=utf-8
# Copyright 2016 Ottokar Tilk and Tanel Alumäe
# The following code is available on:
# https://github.com/ottokart/punctuator2/blob/master/example/dont_run_me_run_the_other_script_instead.py
# In it, functions are defined to exchange all punctuation marks in a dataset for 
# descriptors of said punctuations.

from __future__ import division, print_function
from nltk.tokenize import word_tokenize

import nltk
import os
from io import open
import re
import sys

nltk.download("punkt")

NUM = "<NUM>"
BREAK = "<BREAK>"

EOS_PUNCTS = {".": ".PERIOD", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}
INS_PUNCTS = {",": ",COMMA", ";": ";SEMICOLON", ":": ":COLON"}

forbidden_symbols = re.compile(r"[\[\]\(\)\/\\\>\<\=\+\_\*]")
multiple_punct = re.compile(r"([\.\?\!\,\:\;])(?:[\.\?\!\,\:\;]){1,}")

def tokenize(input:str, puncts=[',', '.', ';', ':', '?', '!']):
  # Inicializamos una lista vacía que contendrá, en cada paso, los tokens
  # completos procesados hasta el momento.
  res = []

  # Se inicializa una cadena vacía que contendrá, en cada paso, la secuencia
  # parcial de caractéres de la cadena del token en procesamiento. 
  partial = ''

  # Reading type
  cur_read_type = None
  
  # En cada paso (hasta terminar de procesar todos los caracteres de la cadena)
  for i in range(len(input)):
    
    # Se lee el carácter i-ésimo de la cadena
    c_i = input[i] 
    
    # Si dicho carácter corresponde a un espacio o a un signo de puntuación
    # entonces, el token que estábamos procesando finaliza, luego
    if c_i in [' '] + puncts:
      
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
    
    #Y continúa el procesamiento del siguiente carácter.
  
  # El token leído en última instancia es añadido a la lista de tokens (siempre
  # que no sea vacío)
  res += [partial.lower()] if partial.strip() != '' else []

  # Finalmente, se devuelve la lista de tokens
  return res

def process_line(line):

    tokens =  tokenize(line.strip())
    output_tokens = []
    prev_token = 'null'

    for token in tokens:
        if token in INS_PUNCTS:
            if  prev_token not in INS_PUNCTS and prev_token not in EOS_PUNCTS:
                output_tokens.append(INS_PUNCTS[token])
        elif token in EOS_PUNCTS:
            if  prev_token not in INS_PUNCTS and prev_token not in EOS_PUNCTS:
                output_tokens.append(EOS_PUNCTS[token])
        elif re.fullmatch('\d+', token):
            output_tokens.append(NUM)

        else:
            output_tokens.append(token.lower())
        
        prev_token = token

    return " ".join(output_tokens + [BREAK])


def tokenize2(input:str):
  PUNCTS = EOS_PUNCTS.copy()
  PUNCTS.update(INS_PUNCTS)
  PUNCTS[" "] = " "

  # Inicializamos una lista vacía que contendrá, en cada paso, los tokens
  # completos procesados hasta el momento.
  res = []

  # Se inicializa una cadena vacía que contendrá, en cada paso, la secuencia
  # parcial de caractéres de la cadena del token en procesamiento. 
  partial = ''

  # Reading type
  cur_read_type = None
  
  # En cada paso (hasta terminar de procesar todos los caracteres de la cadena)
  for i in range(len(input)):
    
    # Se lee el carácter i-ésimo de la cadena
    c_i = input[i] 
    
    # Si dicho carácter corresponde a un espacio o a un signo de puntuación
    # entonces, el token que estábamos procesando finaliza, luego
    if c_i == ' ' or c_i in PUNCTS:
      
      # Ha de añadirse (junto al signo de corte), como nuevos tokens.
      # Sólo se añadirá no es vacío ( si no corresponde al espacio, resp.).
      if partial:
        res.append(partial)
         
      res.append(PUNCTS[c_i])
      
      # Y reseteamos la cadena parcial de token a vacío
      partial = ''
      cur_read_type = None
    
    # En otro caso, 
    else:
      # Añadimos el carácter a la cadena parcial del token procesamiento
      # si los tipos no coinciden entendemos que corresponden a cadenas distintas

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
    
    #Y continúa el procesamiento del siguiente carácter.
  
  # El token leído en última instancia es añadido a la lista de tokens (siempre
  # que no sea vacío)
  res += [partial] if partial.strip() != '' else []

  # Finalmente, se devuelve la lista de tokens
  return res 

def process_line2(line):
    PUNCTS = list(EOS_PUNCTS.values()) + list(INS_PUNCTS.values())
    tokens = tokenize2(line.strip())
    output_tokens = []
    last_is_punct = True
    union = False
    i=0
    while i < (len(tokens)):
        if tokens[i] in PUNCTS:
            if not last_is_punct:
                if  (i > 0) and (tokens[i-1] != ' ') and (i + 1 < len(tokens)) and (tokens[i+1] !=' '):
                  if (output_tokens[-1][-1].isdigit() and tokens[i+1][0].isdigit()) or  (not(output_tokens[-1][-1].isdigit()) and not(tokens[i+1][0].isdigit()) and tokens[i+1] not in PUNCTS) :
                      union = True
                
                else:
                    output_tokens.append(tokens[i])
                    last_is_punct = True
                    union = False

        elif tokens[i] != ' ':
            if union:
                output_tokens[-1] += tokens[i]
            else:
                output_tokens.append(tokens[i])
            last_is_punct = False
            union = False
        
        i += 1

    return " ".join(output_tokens + [BREAK])

def clear_endbreak_line(str):
  return re.sub('<BREAK>|<break>' , '', str.strip())
