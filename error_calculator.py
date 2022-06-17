# coding: utf-8

"""
Computes and prints the overall classification error and precision, recall, F-score over punctuations.
"""

from numpy import nan
import data
import codecs
import sys

MAPPING = {}

# Función de cómputo del error
def compute_error(target_paths, predicted_paths, only_puncts=True):
    """
    Corresponde a la función de evaluación de las métricas de error entre dos 
    colecciones de archivos de textos, ground truth y predichos. 

    Parámetros
    ----------
    target_paths : list(str)
        Rutas a los archivos de texto con los textos originales (ground truth)

    ppredicted_paths : list(str)
        Rutas a los archivos de texto con los textos predichos.

    Salida
    ------
    None

  """

    # Cargamos el diccionario de de puntuaciones
    punctuation_vocabulary = data.read_vocabulary(data.PUNCT_VOCAB_FILE)

    # Inicializamos los contadores para las métricas
    counter = 0         # Contador total de los elementos analizados
    total_correct = 0   # Contador total de las predicciones correctas

    correct = 0.        # Contador total de los símbolos de puntuación/mayúsculas colocados correctamente
    substitutions = 0.  # Contador total de los errores de sustitución
    deletions = 0.      # Contador total de los errores de omisión
    insertions = 0.     # Contador total de los errores de inserción

    true_positives = {}  # Contador de TP
    false_positives = {} # Contador de FP
    false_negatives = {} # Contador de FN

    # Para cada par de archivos (truth, predicted)
    for target_path, predicted_path in zip(target_paths, predicted_paths):

        # Mantenemos dos variables que corresponden al signo de puntuación procesado en cada momento
        # en el texto de origen y el texto predicho
        target_punctuation = " "
        predicted_punctuation = " "

        # Mantenemos dos índices de la posición de la cadena del token actual inspeccionado en cada una de las cadenas
        t_i = 0
        p_i = 0

        with codecs.open(target_path, 'r', 'utf-8') as target, codecs.open(predicted_path, 'r', 'utf-8') as predicted:
            # Leemos los textos correspondientes a cada uno de los archivos
            target_stream = target.read().split()
            predicted_stream = predicted.read().split()
            
            
            while True:
                # obtenemos el signo de puntuación correspondiente al target obviando las puntuaciones consecutivas y mapeándolo, si procede
                if data.PUNCTUATION_MAPPING.get(target_stream[t_i], target_stream[t_i]) in punctuation_vocabulary:
                    while data.PUNCTUATION_MAPPING.get(target_stream[t_i], target_stream[t_i]) in punctuation_vocabulary: # skip multiple consecutive punctuations
                        target_punctuation = data.PUNCTUATION_MAPPING.get(target_stream[t_i], target_stream[t_i])
                        target_punctuation = MAPPING.get(target_punctuation, target_punctuation)
                        t_i += 1
                
                # En otro caso, el signo de puntuación corresponde al espacio
                else:
                    target_punctuation = " "

                # Obtenemos el signo de puntuación actual en el texto predicho. Si no es un signo actual el token analizado entonces se establece al espacio
                if predicted_stream[p_i] in punctuation_vocabulary:
                    predicted_punctuation = MAPPING.get(predicted_stream[p_i], predicted_stream[p_i])
                    p_i += 1
                else:
                    predicted_punctuation = " "

                # Comprobamos si la predicción es correcta (contemplando tanto los signos de puntuación como las mayúsculas, si procede)
                is_correct = int(target_punctuation == predicted_punctuation) * int(only_puncts or target_stream[t_i] == predicted_stream[p_i]) 

                # Incrementamos los contadores del número de elementos procesados y de las predicciones totales correctas (si procede)
                counter += 1 
                total_correct += is_correct

                # Según el caso, incrementamos los contadores de predicciones activas correctas, omisiones, insercciones y sustituciones, ...
                if predicted_punctuation == " " and target_punctuation != " ":
                    deletions += 1
                    false_negatives[target_punctuation] = false_negatives.get(target_punctuation, 0.) + 1.
                elif predicted_punctuation != " " and target_punctuation == " ":
                    insertions += 1
                    false_positives[predicted_punctuation] = false_positives.get(predicted_punctuation, 0.) + 1.
                elif predicted_punctuation != " " and target_punctuation != " " and predicted_punctuation == target_punctuation:
                    correct += 1
                    true_positives[target_punctuation] = true_positives.get(target_punctuation, 0.) + 1.
                elif predicted_punctuation != " " and target_punctuation != " " and predicted_punctuation != target_punctuation:
                    substitutions += 1
                    false_positives[predicted_punctuation] = false_positives.get(predicted_punctuation, 0.) + 1.
                    false_negatives[target_punctuation] = false_negatives.get(target_punctuation, 0.) + 1.
                elif not(only_puncts) and target_stream[t_i][0].isupper() and predicted_stream[p_i][0].isupper():
                    correct += 1
                    true_positives["·M"] = true_positives.get("·M", 0.) + 1.
                elif not(only_puncts) and target_stream[t_i][0].isupper() and predicted_stream[p_i][0].islower():
                    deletions += 1
                    false_negatives["·M"] = false_negatives.get("·M", 0.) + 1.
                elif not(only_puncts) and target_stream[t_i][0].islower() and predicted_stream[p_i][0].isupper():
                    insertions += 1
                    false_positives["·M"] = false_positives.get("·M", 0.) + 1.

                # Si los términos apuntados no son iguales (en minúscula) entonces las cadenas no son unificables. 
                # Nótese que se incrementa t_i y p_i en una unidad extra sólo si son signos de puntuación, respectivamente
                # Por lo que ambos apuntan en este momento a un término, luego si no son iguales en minúscula las cadenas
                # no son unificables. 
                assert target_stream[t_i].lower() == predicted_stream[p_i].lower(), \
                        ("File: %s \n" + \
                        "Error: %s (%s) != %s (%s) \n" + \
                        "Target context: %s \n" + \
                        "Predicted context: %s") % \
                        (target_path,
                        target_stream[t_i], t_i, predicted_stream[p_i], p_i,
                        " ".join(target_stream[t_i-2:t_i+2]),
                        " ".join(predicted_stream[p_i-2:p_i+2]))
                
                # Se incrementan los índices
                t_i += 1
                p_i += 1

                # Si se llega al final del fichero entonces se sigue con un nuevo fichero
                if t_i >= len(target_stream)-1 and p_i >= len(predicted_stream)-1:
                    break
    
    #Se inicializan los contadores globales de TP, FP y FN
    overall_tp = 0.0
    overall_fp = 0.0
    overall_fn = 0.0

    print("-"*46)
    print("{:<16} {:<9} {:<9} {:<9}".format('PUNCTUATION','PRECISION','RECALL','F-SCORE'))

    # Para cada símbolo de puntuación mostramos las métricas Precision, Recall y F-score
    for p in list(punctuation_vocabulary.keys()) + ([] if only_puncts else ["·M"]):

        if p == data.SPACE:
            continue


        overall_tp += true_positives.get(p,0.)
        overall_fp += false_positives.get(p,0.)
        overall_fn += false_negatives.get(p,0.)

        punctuation = p
        precision = (true_positives.get(p,0.) / (true_positives.get(p,0.) + false_positives[p])) if p in false_positives else nan
        recall = (true_positives.get(p,0.) / (true_positives.get(p,0.) + false_negatives[p])) if p in false_negatives else nan
        f_score = (2. * precision * recall / (precision + recall)) if (precision + recall) > 0 else nan        
        print("{:<16} {:<9} {:<9} {:<9}".format(punctuation, round(precision*100,3), round(recall*100,3), round(f_score*100,3)))
    print("-"*46)
    # Calculamos y mostramos las métricas generales
    pre = overall_tp/(overall_tp+overall_fp) if overall_fp else nan
    rec = overall_tp/(overall_tp+overall_fn) if overall_fn else nan
    f1 = (2.*pre*rec)/(pre+rec) if (pre + rec) else nan
    print("{:<16} {:<9} {:<9} {:<9}".format("Overall", round(pre*100,3), round(rec*100,3), round(f1*100,3)))
    print("Err: %s%%" % round((100.0 - float(total_correct) / float(counter-1) * 100.0), 2))
    print("SER: %s%%" % round((substitutions + deletions + insertions) / (correct + substitutions + deletions) * 100, 1))


if __name__ == "__main__":

    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        sys.exit("Ground truth file path argument missing")

    if len(sys.argv) > 2:
        predicted_path = sys.argv[2]
    else:
        sys.exit("Model predictions file path argument missing")
    if len(sys.argv) > 3 and sys.argv[3]=='--withM':
        only_puncts = False
    else:
        only_puncts = True

    compute_error([target_path], [predicted_path], only_puncts=only_puncts)    
        
