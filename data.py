# coding: utf-8
# adapted by vicramgon
from __future__ import division

import random
import os
import sys
import operator
import pickle
import codecs
import fnmatch

# PARÁMETROS DEL SCRIPT

# Fichero donde se guardarán los datos de entrenamiento
DATA_PATH = "./punctdata"

# Token de representación de final de frase (distinto al de final de línea)
END = "</S>"

# Token para los términos desconocidos (no presentes en el vocabulario)
UNK = "<UNK>"

# Token para la respresentación de los espacios
SPACE = "_SPACE"

# Tamaño máximo del vocabulario
MAX_WORD_VOCABULARY_SIZE = 100000

# Mínimo número de ocurrencias de las palabras del vocabulario en el conjunto de
# entrenamiento
MIN_WORD_COUNT_IN_VOCAB = 2

# Longitud máxima de la frase
MAX_SEQUENCE_LEN = 200

# Ficheros del directorio de salida en los que se guardarán las vectorizaciones
# de los archivos correspondientes. 
TRAIN_FILE = os.path.join(DATA_PATH, "train")
DEV_FILE = os.path.join(DATA_PATH, "dev")

# Ficheros del directorio de salida en los que se guardarán los vocabularios de
# términos y símbolos de puntuación
WORD_VOCAB_FILE = os.path.join(DATA_PATH, "vocabulary")
PUNCT_VOCAB_FILE = os.path.join(DATA_PATH, "punctuations")

# Tokens que se utilizarán como símbolos de puntuación (es importante que posean como primer elemento el signo 
# correspondiente y sean coherentes con los especificados en el procesamiento de ficheros o con los que aparecen en ]
# el fichero de entrada)
PUNCTUATION_VOCABULARY = {SPACE, ",COMMA", ".PERIOD", "?QUESTIONMARK", "!EXCLAMATIONMARK", ":COLON", ";SEMICOLON"}
PUNCTUATION_MAPPING = {} # Opcional si algún signo de puntuación se sustituye por otro

# Tokens que sirven como final de frase (no de línea). Típicamente en inglés toda frase termina con ./?/!
EOS_TOKENS = {".PERIOD", "?QUESTIONMARK", "!EXCLAMATIONMARK"}

# Signos de puntuación que se descartan (opcional)
CRAP_TOKENS = {}  

###############################################################################################################################
# FUNCIONES 
###############################################################################################################################

def add_counts(word_counts, line):
    """
      Función para llevar la cuenta de las ocurrencias de cda una de las palabras

      Parámetros
      ----------
      word_counts : dict(str, int)

          Un diccionario (o similar) que contiene la cuenta de las ocurrencias de 
          cada uno de los términos hasta el momento. ¡ES MODIFICADO!

      line : str

          Una cadena correspondiente a la linea tokenizada del fichero de datos

      Salida
      ------
        None
          Modifica el diccionario pasado como parámetro añadiendo la cuenta de las
          ocurrencias de las palabras de la frase.
    """
    # Para cada token de la frase,
    for w in line.split():
        # Si el token no corresponde a un término
        if (
            w in CRAP_TOKENS
            or w in PUNCTUATION_VOCABULARY
            or w in PUNCTUATION_MAPPING
        ): 
            # se desprecia
            continue
        
        # En otro caso, se contabiliza la ocurrencia para el término correspondiente
        word_counts[w] = word_counts.get(w, 0) + 1

# Función para la creación del vocabulario a partir de los términos y su número de
# ocurrencias
def create_vocabulary(word_counts):
    """
      Función para la creación del vocabulario a partir de los términos y su número de 
      ocurrencias
      
      Parámetros
      ----------
      word_counts : dict(str, int)

          Un diccionario (o similar) que contiene la cuenta de las ocurrencias de 
          cada uno de los términos hasta el momento. ¡ES MODIFICADO!

      Salida
      ------
        None
          Modifica el diccionario pasado como parámetro añadiendo la cuenta de las
          ocurrencias de las palabras de la frase.
    """

    # Se constuye el vocabulario con los MAX_WORD_VOCABULARY_SIZE términos con más
    #ocurrencias que poseen más de las ocurrencias mínimas
    vocabulary = [
        wc[0]
        for wc in reversed(sorted(word_counts.items(), key=operator.itemgetter(1)))
        if wc[1] >= MIN_WORD_COUNT_IN_VOCAB and wc[0] != UNK
    ][
        :MAX_WORD_VOCABULARY_SIZE
    ]  # Unk will be appended to end

    # END Y UNK se añaden también al vocabulario.
    vocabulary.append(END)
    vocabulary.append(UNK)

    print("Vocabulary size: %d" % len(vocabulary))
    return vocabulary

# Construye un diccionario a partir de un iterable según la posición (clave) de 
# sus elementos (valor)
def iterable_to_dict(arr):
    return dict((x.strip(), i) for (i, x) in enumerate(arr))

# Abre el fichero especificado como vocabulario y construye un diccionario según
# el orden (dado por las líneas) en que aparecen los términos del fichero
def read_vocabulary(file_name):
    with codecs.open(file_name, "r", "utf-8") as f:
        vocabulary = f.readlines()
        print('Vocabulary "%s" size: %d' % (file_name, len(vocabulary)))
        return iterable_to_dict(vocabulary)

# Escribe en el fichero dedicado al vocabulario los términos del vocabulario en 
# orden de las claves.
def write_vocabulary(vocabulary, file_name):
    with codecs.open(file_name, "w", "utf-8") as f:
        f.write("\n".join(vocabulary))


def write_processed_dataset(input_files, output_file):
    """
      Función para el procesamiento de los datos de los ficheros, para su vectorización
      de acuerdo al vocabulario de palabras y el de puntuaciones, generando los datos
      de entrenamiento y validación para el modelo.
      
      Parámetros
      ----------
      input_files : list(str)
        Contiene las rutas de los ficheros correspondientes al conjunto de ejemplos
        procesado (entrenamiento o validación)
      
      output_file : str
        Ruta al fichero donde se guardarán las vectorizaciones de los datos procesados

      Salida
      ------
        None
        
        Escribe los ficheros correspondientes.
    """

    # Se inicializa una lista vacía que almacenará las vectorizaciones de las frases 
    # se han hecho hasta el momento
    data = []

    # Se leen los vocabularios de términos y puntuaciones
    word_vocabulary = read_vocabulary(WORD_VOCAB_FILE)
    punctuation_vocabulary = read_vocabulary(PUNCT_VOCAB_FILE)

    # Se inicializan dos contadores que reflejan el número total de tokens leídos
    # y el número de tokens que son UNK (sólo para datos para el usuario)
    num_total = 0
    num_unks = 0

    # Se inicializan las listas que contendrán las vectorizaciones de los elementos
    # de la frase procesada en cada instante
    current_words = []
    current_punctuations = []

    # Se inicializa un supervisor que refleja cuál es el último elemento que corresponde
    # a un signo de final de frase (para dejar frases consistentes en caso de que haya 
    # que partirlas por ser demasiado largas)
    last_eos_idx = 0

    # Se inicializa un supervisor que refleja si el anterior elemento corresponde 
    # a un elemento de puntuación, para evitar los signos de puntuación consecutivos.
    # Como se inicia True, entonces todos los tokens de puntuación al inicio de la frase son
    # descartados.
    last_token_was_punctuation = True  

    # Se inicializa un supervisor que indica si hay que esperar hasta leer un símbolo de final de
    # frase (no de línea) para considerar una nueva frase (para el caso de las fragmentaciones)
    skip_until_eos = False  

    # Para cada token de cada linea de cada archivo
    for input_file in input_files:
        with codecs.open(input_file, "r", "utf-8") as text:
            for line in text:
                for token in line.split():

                    # Si el token es de puntuación y ha de ser mapeado a otro entonces se hace el mapeo
                    if token in PUNCTUATION_MAPPING:
                        token = PUNCTUATION_MAPPING[token]

                    # Si no se debe empezar la frase hasta un símbolo de final de frase
                    if skip_until_eos:
                        # si se lee un nuevo símbolo de final de frase, se desactiva el supervisor
                        # y, en el siguiente paso empezará la lectura de una nueva frase
                        if token in EOS_TOKENS:
                            skip_until_eos = False

                        # en otro caso el token se descarta y se sigue esperando la llegada de un
                        # token de final de frase.
                        continue

                    # en otro caso (se está en procesamiento activo de la frase)

                    # Si el token pertenece a los descartables, se descarta
                    elif token in CRAP_TOKENS:
                        continue

                    # Si el token corresponde a un signo de puntuación
                    elif token in punctuation_vocabulary:

                        # Si el anterior token también era de puntuación, entonces el nuevo se descarta
                        if last_token_was_punctuation:
                            continue

                        # En otro caso, si el token corresponde a un token de final de frase, se actualiza
                        # la referencia del último token de final de frase
                        if token in EOS_TOKENS:
                            last_eos_idx = len(current_punctuations)

                        # Se añade el id (entero, int) correspondiente al token de puntuación, según el 
                        # vocabulario de puntuaciones
                        punctuation = punctuation_vocabulary[token]

                        # al vector (lista) de puntuaciones de la frase
                        current_punctuations.append(punctuation)

                        # se activa la marca de último token puntuación
                        last_token_was_punctuation = True

                    # En otro caso, si es un término (no una puntuación)
                    else:
                        # Si el último token procesado era también un término, entonces corresponde 
                        # añadir el símbolo de espacio como símbolo de puntuación.
                        if not last_token_was_punctuation:
                            current_punctuations.append(punctuation_vocabulary[SPACE])

                        # Se toma el id (entero, int) correspondiente al término procesado, según el
                        # vocabulario de palabras. Si no aparece se marca como UNK (con el id corresp.)
                        word = word_vocabulary.get(token, word_vocabulary[UNK])

                        # Se añade el id correspondiente al término al vector de palabras correspondiente a
                        # la frase actual
                        current_words.append(word)
                        
                        # Se desactiva la marca de último término puntuación.
                        last_token_was_punctuation = False

                        # Se incrementa el número total de términos procesados
                        num_total += 1

                        # Y se incrementa el número total de UNKs, si procede
                        num_unks += int(word == word_vocabulary[UNK])

                    # Si se ha llegado al tamaño de secuencia máxima, 
                    if ( len(current_words) == MAX_SEQUENCE_LEN ):  

                        # Entonces el último token procesado corresponde a un término (y no a un símbolo de puntuación)
                        # de donde se sigue inmediatamente que, como se inicia con la lectura de un término y se van intercalando
                        # términos y símbolos de puntuación, entonces debe haber un símbolo de puntuación menos que el número de 
                        # términos
                        assert len(current_words) == len(current_punctuations) + 1, (
                            "#words: %d; #punctuations: %d"
                            % (len(current_words), len(current_punctuations))
                        )

                        # Si la referencia del último signo de puntuación es 0, entonces la frase es demasiado larga,
                        # luego se descarta y se empieza a intentar leer una nueva. (Considere aumentar el tamaño de secuencia)
                        if last_eos_idx == 0:
                            skip_until_eos = True

                            current_words = []
                            current_punctuations = []

                            last_token_was_punctuation = True 
                        
                        # En otro caso, se añade la secuencia como secuencia de entrenamiento
                        else:
                            # Para ello se toman los términos procesados de las secuencias, sustituyendo la última por un END
                            # y el número de puntuaciones. Este par configura un ejemplo del conjunto de entrenamiento o validación
                            subsequence = [
                                current_words[:-1] + [word_vocabulary[END]],
                                current_punctuations
                            ]

                            data.append(subsequence)

                            # Comenzamos la lectura de la siguiente frase desde el último signo de puntuación leído.
                            current_words = current_words[last_eos_idx + 1 :]
                            current_punctuations = current_punctuations[
                                last_eos_idx + 1 :
                            ]

                        last_eos_idx = 0  # sequence always starts with a new sentence

    # Se muestra el ratio de desconocidos entre los tokens leídos
    print("%.2f%% UNK-s in %s" % (num_unks / num_total * 100, output_file))

    # Y se guardan los elementps como un archivo binario.
    with open(output_file, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    # Si quieres ver el aspecto de los ficheros (las vectorizaciones) descomenta las siguientes líneas

    with open(output_file + ".txt" , "w") as f:
        for entry in data:
          f.write(str(entry) + '\n')


def create_dev_test_train_split_and_vocabulary(root_path, build_vocabulary, train_output, dev_output):
    """
      Función para la creación de los ficheros vectorizados de entrenamiento y validación 
      
      Parámetros
      ----------
      root_path : ruta de la carpeta en la que se encuentran los ficheros de entrenamiento y 
                  validación. Los archivos deben finalizar con las extensiones .train.txt y 
                  .dev.txt, respectivamente.
      
      build_vocabulary : bool
        Indica si es necesario construir el vocabulario (true) o ya se ha creado previamente (false)
      
      train_output : str
          Nombre del fichero en el que se escribirán las vectorizaciones de los datos de entrenamiento.
          
      dev_output : str
          Nombre de los ficheros donde se escribirán las vectorizaciones de los datos de validación. 

      Salida
      ------
        None
        
        Escribe los ficheros correspondientes.
    """

    # Se inicializan dos listas que contendrán las rutas de los ficheros de 
    # entrenamiento y validación, respectivamente. 
    train_txt_files = []
    dev_txt_files = []
  
    # Si es necesario construir el vocabulario se inicia el contador de ocurrencias
    # de palabras vacío
    if build_vocabulary:
        word_counts = dict()

    # Se almacena cada archivo del directorio de datos, en la lista según la
    # extensión del fichero.
    for root, _, filenames in os.walk(root_path):
        for filename in fnmatch.filter(filenames, "*.txt"):

            path = os.path.join(root, filename)
            
            if filename.endswith(".dev.txt"):
                dev_txt_files.append(path)

            elif filename.endswith(".train.txt"):
                train_txt_files.append(path)

                # Para los ficheros de entrenamiento se cuentan las ocurrencias
                # de cada palbra para la construcción de lvocabulario (si procede)
                if build_vocabulary:
                    with codecs.open(path, "r", "utf-8") as text:
                        for line in text:
                            add_counts(word_counts, line)
    
    # Si es necesario, se construye el vocabulario de acuerdo al contador de 
    # de ocurrencias y se guarda en el fichero correspondiente
    if build_vocabulary:
        vocabulary = create_vocabulary(word_counts)
        write_vocabulary(vocabulary, WORD_VOCAB_FILE)
        punctuation_vocabulary = iterable_to_dict(PUNCTUATION_VOCABULARY)
        write_vocabulary(punctuation_vocabulary, PUNCT_VOCAB_FILE)

    # Se procesan los distintos archivos de entrenamiento y validación y se 
    # escriben en los ficheros correspondientes.
    write_processed_dataset(train_txt_files, train_output)
    write_processed_dataset(dev_txt_files, dev_output)



if __name__ == "__main__":
    """
      SCRIPT

      Corresponde al script de generación de datos de entrenamiento. Toma el directorio de 
      en el que se encuentran los ficheros de texto con las frases de entrenamiento y validación
      y genera (según la extensión .train.txt o .dev.txt) archivos binarios con las vectorizaciones
      de las frases, con respecto a los vocabularios de palabras y puntuaciones (también generados).

      Parámetros
      ----------
      1. Ruta al directorio con los datos de las frases tokenizadas de entrenamiento y validación
    """

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        sys.exit(
            "The path to the source data directory with txt files is missing. The command should be: python data.py {folder with train, test and dev splits}"
        )

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    else:
        sys.exit("Data already exists")

    create_dev_test_train_split_and_vocabulary(
        path, True, TRAIN_FILE, DEV_FILE
    )

