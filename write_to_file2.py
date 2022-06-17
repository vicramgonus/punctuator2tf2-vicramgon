# coding = utf-8
# adapted by vicramgon

from process_text import process_line2, clear_endbreak_line
from sklearn.model_selection import train_test_split
import sys

# Signos contemplados como signos de puntuación
PUNCTS = {".": ".PERIOD", ",": ",COMMA", ";": ";SEMICOLON", 
        ":": ":COLON", "?": "?QUESTIONMARK", "!": "!EXCLAMATIONMARK"}

"""
  SCRIPT

  Corresponde al script de procesamiento de los datos. Toma un archivo y procesa
  cada una de las lineas según las funciones de procesamiento del módulo process_text.py
  (funciones de versión 2). Además, según las opciones, parte el conjunto de datos
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
"""

# We process the input text according to the processing script

try:
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

# Punctuation marks processed
test_text = [clear_endbreak_line(process_line2(elem, puncts=PUNCTS)) for elem in lines]
print("Done processing the text")

with open(sys.argv[2] + "/processed_text.test.txt", "w", encoding="utf-8") as test_file:
    for item in test_text:
        test_file.write("%s\n" % item)

print("Done saving files to data directory")