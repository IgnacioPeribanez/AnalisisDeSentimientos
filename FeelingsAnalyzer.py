from sklearn.model_selection import train_test_split
import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from imblearn.under_sampling import RandomUnderSampler
from halo import Halo

importando = Halo(text="Importando nuestro CSV", spinner='dots')
bolsa = Halo(text="Generando bolsa de palabras", spinner='dots')
entrenando = Halo(text="Entrenando la IA", spinner='dots')

importando.start()
# Importamos el csv y lo introducimos en un DataFrame.
df = pd.read_csv('Data.csv')
importando.stop_and_persist(symbol='🦄'.encode('utf-8'), text="CSV importado")

# Creamos un DataFrame en el que equilibraremos los datos positivos y negativos.
df_comentario, df_comentario['Valoracion'] = RandomUnderSampler().fit_resample(df[['Comentario']], df['Valoracion'])

# Creamos un DataFrame en el que equilibraremos los datos positivos y negativos.
train, test = train_test_split(df_comentario, train_size=0.75, random_state=50)

# Creamos los datos de entrenamiento y de test.
x_train, y_train, x_test, y_test = train['Comentario'], train['Valoracion'], test['Comentario'], test['Valoracion']

bolsa.start()
# Creamos la bolsa de palabras, separandolas en train y test.
vectorizer = CountVectorizer(analyzer="word", lowercase=False)
x_train_transform = vectorizer.fit_transform(x_train)
x_test_transform = vectorizer.transform(x_test)
bolsa.stop_and_persist(symbol='🦄'.encode('utf-8'), text="Bolsa generada")

entrenando.start()
# Entrenamos la IA con los datos de entrenamiento.
clf = SVC().fit(x_train_transform, y_train)
entrenando.stop_and_persist(symbol='🦄'.encode('utf-8'), text="IA Entrenada")

# Probamos el acierto de nuestra IA mediante los datos de test y lo mostramos por pantalla.
print("\nLa IA tiene un", round(clf.score(x_test_transform, y_test)*100, 2), "%","de acierto")

while (True) :
    # Menu
    print("\n------------------------------------")
    print("0-. Finalizar programa")
    # Pedimos el comentario a analizar
    comentario = [input("Introduce un comentario: ")]
    if (comentario[0] == '0') :
        break
    else :
        # Lo convertimos a minusculas
        comentario[0] = comentario[0].lower()
        # Condicion (Si el comentario es 0, es negativo)
        if (clf.predict(vectorizer.transform(comentario)) == 0) :
            print("El comentario es negativo")
        else :
            print("El comentario es positivo")
    print("------------------------------------")        
