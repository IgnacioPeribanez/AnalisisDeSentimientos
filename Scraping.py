from bs4 import BeautifulSoup
import requests
import pandas
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Pedimos el articulo que quiere buscar el usuario.
Articulo = (input("Que artículo buscas: "))
# Pedimos la cantidad de productos a buscar.
cantidad = int(input("Cuantos artículos buscas: "))

# La url de la que sacaremos los productos.
URL = 'https://www.amazon.es/s?k=' + Articulo

headers = {"User-Agent": "Mozilla/1.1 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate, br", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

# Pagina sobre la que realizaremos el scrap.
page = requests.get('https://www.amazon.es/s?k=' + Articulo, headers=headers)
# Convertimos la pagina a html.
soup1 = BeautifulSoup(page.content, "html.parser")
soup2 = BeautifulSoup(soup1.prettify(), "html.parser")

# Lista de urls de los productos a analizar.
urls = soup2.findAll('a', class_='a-link-normal s-no-outline', limit=cantidad)

# Lista de comentarios del scrap.
comentarios = list()
# Lista de valoraciones del scrap.
estrellas = list()

# Método que escribe los comentarios de una pagina, con su valoracion convertida a 1 o 0.
def escribir(comments, stars):
    # Bucle de comentarios de una pagina.
    for comentario,  estrella in zip(comments, stars):
        # Limpiamos emoticonos, teclas especiales...
        comentario = " ".join(comentario.get_text().strip().split())
        try:
            # Comprobamos el idioma del comentario, si es español intentaremos introducirlo en la lista.
            if (detect(comentario) == "es") :
                # Limpiamos el comentario.
                comentario = comentario.lower()
                comentario = re.sub(r'[^\w\s]', '', comentario)
                comentario = re.sub(u"[àáâãäå]", 'a', comentario)
                comentario = re.sub(u"[èéêë]", 'e', comentario)
                comentario = re.sub(u"[ìíîï]", 'i', comentario)
                comentario = re.sub(u"[òóôõö]", 'o', comentario)
                comentario = re.sub(u"[ùúûü]", 'u', comentario)
                comentario = re.sub(u"[ñ]", 'n', comentario)
                comentario = re.sub(u"[ç]", 'c', comentario)
                comentarios.append(comentario)
                # Condicion para clasificar las estrellas.
                if (len(estrella.findChild("span", { "class" : "a-icon-alt" }).get_text()) == 55) :
                    if (str(estrella.findChild("span", { "class" : "a-icon-alt" }).get_text())[19:20] > "3") :
                        estrellas.append("1")
                    else :
                        estrellas.append("0")
                else : 
                    if (str(estrella.findChild("span", { "class" : "a-icon-alt" }).get_text())[18:19] > "3") :
                        estrellas.append("1")
                    else :
                        estrellas.append("0")   
        except LangDetectException:
            print("No se ha podido introducir el comentario")
                
# Contador de productos
producto = 1
# Bucle por producto
for i in urls:
    # Sacamos la pagina de reviews del producto
    review = i['href'].replace('dp', 'product-reviews')
    page = requests.get(("https://www.amazon.es" + review ), headers=headers)
    # Convertimos la pagina a html.
    soup1 = BeautifulSoup(page.content, "html.parser")
    soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
    # Cogemos la pagina siguiente de reviews
    siguiente =  soup2.findAll('li', class_='a-last')
    # Cogemos la pagina siguiente de reviews
    final =  soup2.findAll('li', class_='a-disabled a-last')
    # Contador para gestionar la primera pagina.
    contador = '0'
    while True :
        print("------------------")
        print("Producto:" + str(producto))
        print("------------------")
        # Condicion (Si es la primera pagina)
        if contador == '0' :
            print('Página(1): https://www.amazon.es/' + review)
            # Guardamos las estrellas y comentarios
            stars = soup2.findAll('div', class_='a-section celwidget')
            comments = soup2.findAll('span', class_='a-size-base review-text review-text-content')
        else :
            # Condicion (Si hay una pagina siguiente de reviews, la primera vez que se ejecute cogera la 2a pagina).
            if len(siguiente) > 0 : 
                # Sacamos la pagina a analizar con el "siguiente" de la anterior pagina.
                page = requests.get('https://www.amazon.es/' + str((siguiente[0].findChild("a"))['href']), headers=headers)
                print('Página(' + str(int(contador) + 1) + '): https://www.amazon.es/' + str((siguiente[0].findChild("a"))['href']))
                # Convertimos la pagina a html.
                soup1 = BeautifulSoup(page.content, "html.parser")
                soup2 = BeautifulSoup(soup1.prettify(), "html.parser")
                # Guardamos las estrellas y comentarios.
                stars = soup2.findAll('div', class_='a-section celwidget')
                comments = soup2.findAll('span', class_='a-size-base review-text review-text-content')
                # Guardamos la siguiente pagina que usaremos en la condicion de arriba.
                siguiente =  soup2.findAll('li', class_='a-last')
                # Guardamos la cantidad de etiquetas "a-disabled a-last" que hay.
                final =  soup2.findAll('li', class_='a-disabled a-last')
                # Condicion (Si existe la etiqueta anterior, significa que es la ultima pagina de reviews de ese producto).
                if len(final) == 1 : 
                    # Ecribimos los comentarios en la lista.
                    escribir(comments,stars)
                    # Rompemos el bucle de este producto.
                    break 
        # Condicion (Si no hay pagina siguiente)
        if (len(siguiente) == 0) :
            # Paramos bucle
            break
        else :
            # Ecribimos los comentarios en la lista.
            escribir(comments,stars)
        # Contador de primera pagina.
        contador = str(int(contador) + 1)
        # Mostramos comentarios obtenidos por el programa en tiempo real.
        print('Comentarios obtenidos: ' + str(len(comentarios)))
    # Contador de producto.
    producto = producto + 1

# Enviamos los datos a pandas.
datos = pandas.DataFrame({"Valoracion": estrellas, "Comentario": comentarios})
print(datos)
# Exportamos el pandas a un csv, sin index, y separado con ",".
datos.to_csv('prueba.csv', encoding='utf-8', sep=',', index=False)