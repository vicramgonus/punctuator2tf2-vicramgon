# coding = utf-8
# Adaptado por vicramgon

from process_text import process_line
from sklearn.model_selection import train_test_split
import sys

# Se procesan los datos de ejemplo dados según los métodos de procesamiento
# presentes en process_text

# Signos contemplados como signos de puntuación
PUNCTS = {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}

"""
  SCRIPT

  Corresponde al script de procesamiento de los datos. Toma un archivo y procesa
  cada una de las lineas según las funciones de procesamiento del módulo process_text.py
  (funciones de versión 1). Además, según las opciones, parte el conjunto de datos
  en tres conjuntos: entrenamiento, dev y test y los guarda en el directorio establecido
  como parámetro con los nombres processed_text.train.txt, processed_text.dev.txt 
  y processed_text.test.txt, respectivamente.

  Parámetros
  ----------
  1. Ruta al fichero de ejemplos de texto.
  2. Ruta al directorio destino donde se almacenarán los ficheros
  3. Tamaño (proporción) de ejemplos no tomados para entrenamiento
  4. Tamaño (proporción) de ejemplos tomados para test(sobre los no tomados para 
     entrenamiento)

  Si el 3 y el 4 no están presentes se considerará que corresponde todo al conjunto
  de test. Si no, si 4 no está presente se considerá que corresponde a la partición
  para entrenamiento y evaluación.

  Salida
  ------
    str
      La cadena con los elementos tokenizados.
"""


try:
    # Se lee el fichero con los ejemplos (en caso de que exista y corresponda a
    # un fichero de texto)
    if len(sys.argv) > 1:
        float(sys.argv[1])
        print("There is no specified text to process")
        sys.exit(0)
except ValueError:
    with open(sys.argv[1], "r") as file:
        lines = file.readlines()

if not isinstance(lines[0], str):
    print("The input text needs to be a list of strings")
    sys.exit(0)
   
print(f"Number of rows in file: {len(lines)}")

#Se procesa cada una de las lineas del fichero
processed_text = [process_line(elem, puncts=PUNCTS) for elem in lines]
print("Done processing the text")


# Se separa el conjunto de ejemplos en train, dev y test, según los parámetros
# recibidos.
if len(sys.argv) > 4:
    train_text, tmp_text = train_test_split(
        processed_text, test_size=float(sys.argv[3]), random_state=42
    )
    dev_text, test_text = train_test_split(
        tmp_text, test_size=float(sys.argv[4]), random_state=42
    )

elif len(sys.argv) == 4:
    train_text, dev_text = train_test_split(
        processed_text, test_size=float(sys.argv[3]), random_state=42
    )

else:
    test_text = processed_text

# Se escriben los documentos con los ejemplos correspondientes en los archivos del
# directorio pasado como parámetro.
if len(sys.argv) >= 4:
  with open(sys.argv[2] + "/processed_text.train.txt", "w", encoding="utf-8") as train_file:
      for item in train_text:
          train_file.write("%s\n" % item)

  with open(sys.argv[2] + "/processed_text.dev.txt", "w", encoding="utf-8") as dev_file:
      for item in dev_text:
          dev_file.write("%s\n" % item)

if len(sys.argv) != 4:
  with open(sys.argv[2] + "/processed_text.test.txt", "w", encoding="utf-8") as test_file:
      for item in test_text:
          test_file.write("%s\n" % item)

print("Done saving files to data directory")