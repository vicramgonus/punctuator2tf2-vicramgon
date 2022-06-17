# coding: utf-8  # by vicramgon
from __future__ import division

import models, data, main
from process_text import clear_endbreak_line
import re

import sys
import codecs

import tensorflow as tf
import numpy as np
import re

# PARÁMETROS DEL SCRIPT 

# Tamaño máximo de la secuencia 
MAX_SUBSEQUENCE_LEN = 200

# Signos de puntuación de fin de frase o intermedios
EOS_PUNCTS = {".": ".PERIOD", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}
INS_PUNCTS = {",": ",COMMA", ";": ";SEMICOLON", ":": ":COLON"}

# Función para pasar a un array columna
def to_array(arr, dtype=np.int32):
    # minibatch of 1 sequence as column
    return np.array([arr], dtype=dtype).T

# Función de restauración de la puntuación
def restore(text, word_vocabulary, reverse_punctuation_vocabulary, model):
    """
    Corresponde a la función de puntuación y capitalización de un texto/línea
    a partir del modelo predictor. 

    Parámetros
    ----------
    text : str
        El texto para ser puntuado y capitalizado

    word_vocabulary : dict(str,int)
        Correspondiente al vocabulario de términos utilizado en el modelo, esto es
        el que relaciona cada término con el correspondiente id (entero, int) que
        le corresponde.

    reverse_punctuation_vocabulary : dict(int,str)
        Correspondiente al vocabulario de puntuaciones utilizado en el modelo, pero 
        en el sentido inverso, que relaciona cada id con el token de puntuación 
        correspondiente.

    model : models.GRU
        Modelo predictor 

    Salida
    ------
    None

  """
    # Inicializamos un contador que indica el término de la secuencia que se está 
    # analizando
    i = 0

    # Inicializamos una cadena que servirá como almacén de la frase restaurada
    res = ""

    # Mientras no se haya llegado al final del texto
    while True:
        # Se toma la subsecuencia desde el último término leído (el siguiente)
        # hasta el tamaño máximo de la secuencia.
        subsequence = text[i:i+MAX_SUBSEQUENCE_LEN]

        # Si el tamaño de la subsecuencia es 0, fin, ya se ha terminado de procesar
        # el texto
        if len(subsequence) == 0:
            break

        # Se vectoriza la subsecuencia correspondiente
        converted_subsequence = [ word_vocabulary["<NUM>"] if re.fullmatch('\d+', w) else word_vocabulary.get(w, word_vocabulary[data.UNK]) for w in subsequence]

        # y se obtienen las probabilidades para cada signo de puntuación y cada término de la secuencia
        # otorgadas por el modelo predictor.
        y = predict(to_array(converted_subsequence), model)

        # se añade el primer término de la subsecuencia (para la que no hay predicción) 
        res += subsequence[0]

        # se establece una marca del último símbolo de puntuación final que se ha generado
        last_eos_idx = 0

        # Se obtienen los signos de puntuación asignados a cada uno de los términos de la 
        # secuencia.
        punctuations = []
        for y_t in y:
            # Para ello, se considera como signo de puntuación aquél que maximiza la probabilidad 
            # en base a las probabilidades dadas por el predictor
            p_i = np.argmax(tf.reshape(y_t, [-1]))
            punctuation = reverse_punctuation_vocabulary[p_i]

            punctuations.append(punctuation)


            # Se actualiza la marca correspondiente al último signo de puntuación final generado
            # (en realidad el índice siguiente a dicho signo de puntuación)
            if punctuation in data.EOS_TOKENS:
                last_eos_idx = len(punctuations) 
        


        # Si se ha generado algún signo de puntuación final, se establece la marca
        # step al último generado
        if last_eos_idx != 0:
            step = last_eos_idx
        # Y si no, al final de la subsecuencia
        else:
            step = len(subsequence) - 1

        # Durante step pasos (hasta el último signo de puntuación o en su defecto hasta el final de la susecuencia)
        for j in range(step):
            # Si el símbolo de puntuación correspondiente es final
            if punctuations[j] in EOS_PUNCTS:
                # Entonces se añade el símbolo (no el token) y el término siguiente, iniciándolo en mayúscula.
                head = ' ' + subsequence[1+j][0].upper() if j < step - 1 else ' '
                tail = subsequence[1+j][1:].lower() if head and len(subsequence[1+j]) > 1 else ' '
                res += punctuations[j][0] + head + tail
            
            # Si la palabra siguiente corresponde a un token "<UNK>" entonces se establece en mayúscula 
            elif j < step - 1 and subsequence[1+j] == word_vocabulary[data.UNK]:
                # Entonces se añade el símbolo (no el token) y el término siguiente, iniciándolo en mayúscula.
                head = ' ' if punctuations[j] == data.SPACE else punctuations[j][0]
                tail = ' ' + subsequence[1+j][0].upper() + (subsequence[1+j][1:].lower() if len(subsequence[1+j]) > 1 else ' ')
                res += head + tail 
            else:
                # En otro caso se añade el símbolo (no el token) y el término en minúscula
                head = ' ' if punctuations[j] == data.SPACE else punctuations[j][0]
                tail = ' ' + subsequence[j+1].lower() if j < step - 1 else ' '
                res += head + tail

        # Si se ha llegado al final del texto, el bucle finaliza
        if subsequence[-1] == data.END:
            break
        
        # Si no se sigue procesando desde el elemento siguiente al último signo de puntuación final o, en su defecto,
        # desde el siguiente elemento al último de la subsecuencia
        i += step

    # Finalmente, se capitaliza la primera palabra de la frase
    return res[0].upper() + (res[1:] if len(res) > 1 else ' ')

# La función de predicción que corresponde al softmax de las salidas dadas por la red
def predict(x, model):
    return tf.nn.softmax(net(x))

if __name__ == "__main__":
    """
      SCRIPT

      Corresponde al script de regeneración de la puntuación. Tomando un fichero de texto sin 
      puntuaciones ni mayúsculas, y un modelo predictor (que da las probabilidades asociadas a
      cada signo de puntuación para cada término del texto), genera un nuevo archivo con el 
      texto puntuado y capitalizado.

      Parámetros
      ----------
      1. Ruta al archivo de texto de test (sin signos de puntuación ni mayúsculas)
      2. La ruta al modelo GRU (Model.pcl), que actuará como modelo predictor
      3. La ruta del fichero que almacenará el texto puntuado.
    """
    if len(sys.argv) > 1:
        model_file = sys.argv[1]
    else:
        sys.exit("Model file path argument missing")

    if len(sys.argv) > 2:
        input_file = sys.argv[2]
    else:
        sys.exit("Input file path argument missing")

    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    else:
        sys.exit("Output file path argument missing")

    # Se carga el vocabulario y se inicializa una matriz con 1s (según el tamaño del vocabulario y el batch size)
    vocab_len = len(data.read_vocabulary(data.WORD_VOCAB_FILE))
    x_len = vocab_len if vocab_len < data.MAX_WORD_VOCABULARY_SIZE else data.MAX_WORD_VOCABULARY_SIZE + data.MIN_WORD_COUNT_IN_VOCAB
    x = np.ones((x_len, main.MINIBATCH_SIZE)).astype(int)

    # Se carga el modelo
    print("Loading model parameters...")
    net, _ = models.load(model_file, x)

    print("Building model...")

    # Se construyen los vocabularios de puntuación y términos
    word_vocabulary = net.x_vocabulary
    punctuation_vocabulary = net.y_vocabulary

    reverse_word_vocabulary = {v:k for k,v in word_vocabulary.items()}
    reverse_punctuation_vocabulary = {v:k for k,v in punctuation_vocabulary.items()}

    print("Restoring punctuation...")
    # Se leen las lineas del fichero
    with codecs.open(input_file, 'r', 'utf-8') as f:
        lines = f.readlines()

    # Si no tiene se aborta
    if len(lines) == 0:
        sys.exit("Input file empty.")

    # En otro caso, se abre el fichero que almacenará las frases puntadas y capitalizadas
    with open(output_file, 'a') as fout:
      li = 0
      # Para cada linea
      for l in lines:
        if li % 1000 == 0:
            print(f"line{li}")
        # Se obtiene el texto
        input_text = re.sub('\s+', ' ', l.strip())
        # Se eliminan las puntuaciones y se añade el token del final
        text = [w for w in input_text.split() if w not in punctuation_vocabulary and w not in data.PUNCTUATION_MAPPING] + ["<BREAK>", data.END]
        # Se puntua y capitaliza el texto de la linea
        punct_text = restore(text, word_vocabulary, reverse_punctuation_vocabulary, net)
        # Se vuelca al archivo de salida
        fout.write(clear_endbreak_line(punct_text)+'\n')
        # Leemos la siguiente linea 
        li += 1

