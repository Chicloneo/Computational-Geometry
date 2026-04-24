"""PRACTICA 9: 25-03-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p9.py)
- Trabaja en la función arregla (línea 184)
- Para comprobar su funcionamiento ve al final del código y ejecuta la comprobación correspondiente
- Sube el código .py a la tarea del CV al final de la clase
"""

import random
import math
import numpy as np
import matplotlib.pyplot as plt
ERROR = 1e-9

from libreria_gcom_p9 import *


def triangulacion_delaunay_bruta(puntos): #algoritmo O(n^4) que devuelve una triangulación de Delaunay
    n = len(puntos)
    triangulos = []   
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n): # estudiamos el triangulo i, j, k 
                if alineados(puntos[i], puntos[j], puntos[k]): continue # si están alineados no lo debe incluir como triangulo
                vacia, l = True, 0
                conciclicos = set([i, j, k]) # guardamos los índices de los puntos sobre la circunferencia
                while vacia and l < n:
                    valor = dentro_circunf(puntos[i], puntos[j], puntos[k], puntos[l])
                    if valor == 1: vacia = False
                    elif valor == 0 and l not in conciclicos: # los índices i, j, k, l corresponden a puntos concíclicos
                        conciclicos.add(l)
                    l = l+1
                if vacia and len(conciclicos) == 3: # no hay puntos dentro ni sobre la circunferencia
                    triangulos.append([puntos[i], puntos[j], puntos[k]])
                    continue
                elif vacia: # no hay puntos dentro pero sí sobre la circunferencia, triangulamos el polígono circunscrito resultante 
                    # para no triangular varias veces lo mismo, solo lo hacemos si i,j,k son los menores índices de los concíclicos                 
                    indices = sorted(list(conciclicos))
                    if indices[0] == i and indices[1] == j and indices[2] == k:
                        # triangulamos usando un punto como foco, ordenando angularmente
                        foco = puntos[indices[-1]]
                        indices.pop()
                        def angulo(p: Punto) -> float:
                           return math.atan2(p.y - foco.y, p.x - foco.x)
                        indices.sort(key = lambda l: angulo(puntos[l]))
                        for m in range(len(indices) - 1):
                            triangulos.append([foco, puntos[indices[m]], puntos[indices[m+1]]])                                               
                         
    return triangulos



def convierte_lista_triangulos_a_DCEL(triangulos):
    malla = DCEL() # Creamos una única malla vacía
    
    # Diccionario temporal para emparejar gemelas súper rápido
    # Llave: (PuntoA, PuntoB), Valor: Instancia de Arista
    registro_gemelas = {}

    for t in triangulos:
        # Forzamos orientación antihoraria
        if orient(t[0], t[1], t[2]) == -1: 
            t[0], t[1] = t[1], t[0]

        cara = Cara()
        malla.lista_caras.append(cara)

        # 1. Instanciamos las 3 aristas
        e0 = Arista(t[0], t[1])
        e1 = Arista(t[1], t[2])
        e2 = Arista(t[2], t[0])

        e0.cara = e1.cara = e2.cara = cara
        cara.arista_incidente = e0

        # 2. Enlazamos el ciclo interior
        e0.siguiente, e0.anterior = e1, e2
        e1.siguiente, e1.anterior = e2, e0
        e2.siguiente, e2.anterior = e0, e1

        # 3. Guardamos vértices (asegurando higiene)
        malla.lista_vertices[t[0]] = e0
        malla.lista_vertices[t[1]] = e1
        malla.lista_vertices[t[2]] = e2

        # 4. Registramos en la malla
        malla.lista_aristas[e0] = e0
        malla.lista_aristas[e1] = e1
        malla.lista_aristas[e2] = e2

        # 5. Buscamos y asignamos gemelas al vuelo
        registro_gemelas[(t[0], t[1])] = e0
        registro_gemelas[(t[1], t[2])] = e1
        registro_gemelas[(t[2], t[0])] = e2

        # Comprobamos si las aristas opuestas ya fueron creadas por un triángulo adyacente anterior
        if (t[1], t[0]) in registro_gemelas:
            e0.gemela = registro_gemelas[(t[1], t[0])]
            e0.gemela.gemela = e0
        if (t[2], t[1]) in registro_gemelas:
            e1.gemela = registro_gemelas[(t[2], t[1])]
            e1.gemela.gemela = e1
        if (t[0], t[2]) in registro_gemelas:
            e2.gemela = registro_gemelas[(t[0], t[2])]
            e2.gemela.gemela = e2

# --- NUEVO: CREACIÓN DE LA CARA EXTERIOR ---
    
    # 1. Inicializamos la cara exterior
    cara_ext = Cara()
    malla.cara_exterior = cara_ext
    malla.lista_caras.append(cara_ext)
    
    # 2. Identificamos las aristas de la frontera interior
    # Son aquellas que, tras procesar todos los triángulos, no encontraron gemela
    aristas_frontera = [e for e in malla.lista_aristas.keys() if e.gemela is None]
    
    # Diccionario para empalmar el ciclo exterior en O(n)
    # Llave: vértice de origen de la arista exterior, Valor: la semi-arista exterior
    dic_ext_por_origen = {}
    aristas_exteriores = []

    # 3. Creamos las aristas exteriores y las emparejamos
    for e_int in aristas_frontera:
        # El origen de la exterior es el destino de la interior.
        # (Usamos e_int.siguiente.origen asumiendo que es la forma segura de obtener el final)
        origen_ext = e_int.siguiente.origen 
        destino_ext = e_int.origen
        
        # Instanciamos la arista exterior
        e_ext = Arista(origen_ext, destino_ext) # Ajusta los parámetros a tu __init__
        e_ext.cara = cara_ext
        
        # Asignamos gemelas mutuamente
        e_int.gemela = e_ext
        e_ext.gemela = e_int
        
        # Registramos
        malla.lista_aristas[e_ext] = e_ext
        dic_ext_por_origen[origen_ext] = e_ext
        aristas_exteriores.append(e_ext)

    # 4. Cosemos el ciclo exterior (.siguiente y .anterior)
    for e_ext in aristas_exteriores:
        # Sabemos que e_ext termina en 'destino_ext' (que es e_ext.gemela.origen).
        # Por pura topología, la arista exterior siguiente DEBE empezar en ese vértice.
        destino = e_ext.gemela.origen
        
        e_siguiente = dic_ext_por_origen[destino]
        
        # Enlazamos
        e_ext.siguiente = e_siguiente
        e_siguiente.anterior = e_ext

    # 5. Asignamos una arista cualquiera a la cara exterior
    if aristas_exteriores:
        cara_ext.arista_incidente = aristas_exteriores[0]

    return malla



def estropea(triangulacion : DCEL) -> DCEL:     
    while True:
        e = random.choice(list(triangulacion.lista_aristas.keys())) 
        eg = e.gemela
        if eg is not None and e.cara != triangulacion.cara_exterior and eg.cara != triangulacion.cara_exterior:
            c = e.cara
            e.anterior.siguiente = eg.siguiente
            eg.siguiente.anterior = e.anterior
            e.siguiente.anterior = eg.anterior
            eg.anterior.siguiente = e.siguiente
            c.arista_incidente = e.anterior
            triangulacion.lista_vertices[e.origen] = eg.siguiente
            triangulacion.lista_vertices[e.final] = e.siguiente
            triangulacion.lista_aristas.pop(e, None)
            triangulacion.lista_aristas.pop(eg, None)
            triangulacion.lista_caras.remove(eg.cara)
            eg.cara, eg.anterior.cara, eg.siguiente.cara = c, c, c            
            return
    

def arregla(triangulacion: DCEL) -> DCEL:
    # A la triangulacion le falta una arista! Encuéntrala y añádela

    # Para saber si estamos trabajando de forma adecuada con la DCEL podemos
    # utilizar un "inspector", ejecutando la siguiente línea
    # triangulacion.inspector_integridad()
    
    #Hay una cara con 4 lados

    #1 Buscamos la cara con 4 lados
    for cara in triangulacion.lista_caras:
        if len(cara.lista_lados()) == 4:
             cara_mala = cara
             break
    indice_cara_mala = triangulacion.lista_caras.index(cara_mala)
        
    #2 Definimos variables auxiliares
    # Muy importante. Nunca "reorganizar" punteros.
    a  = cara_mala.arista_incidente
    v1 = a.origen
    v2 = a.final
    v3 = a.siguiente.final
    v4 = a.anterior.origen

    b = a.siguiente
    c = a.siguiente.siguiente
    d = a.anterior

    # Creamos la arista y sus atributos. Modificamos los atributos de las aristas.
    e = Arista(v3,v1)
    e.anterior  = b
    e.siguiente = a

    a.anterior  = e #a.siguiente es el mismo
    b.siguiente = e #b.anterior es el mismo

    # Creamos la gemela y sus atributos. Modificamos los atributos de las aristas.
    f = Arista(v1,v3)
    e.gemela    = f
    f.anterior  = d
    f.siguiente = c
    
    f.gemela    = e
    c.anterior  = f
    d.siguiente = f

    # Creamos las caras y sus atributos. Modificamos los atributos
    cara_e = Cara(a)
    cara_f = Cara(c)

    e.cara = cara_e # lo actualizamos para los 3
    a.cara = cara_e
    b.cara = cara_e

    f.cara = cara_f
    c.cara = cara_f
    d.cara = cara_f

    # Modificamos la DCEL
    triangulacion.lista_aristas[e] = e
    triangulacion.lista_aristas[f] = f
    del(triangulacion.lista_caras[indice_cara_mala])
    triangulacion.lista_caras.extend([cara_e, cara_f])

    print(triangulacion.inspector_integridad)

    return triangulacion

"""
def arregla(triangulacion: DCEL) -> DCEL:
# A la triangulacion le falta una arista! Encuéntrala y añádela

# Para saber si estamos trabajando de forma adecuada con la DCEL podemos
# utilizar un "inspector", ejecutando la siguiente línea
# triangulacion.inspector_integridad()
#Hay una cara con 4 lados

#1 Buscamos la cara con 4 lados
for cara in triangulacion.lista_caras:
if len(cara.lista_lados()) == 4:
cara_mala = cara
break
indice_cara_mala = triangulacion.lista_caras.index(cara_mala)
#2 Definimos variables auxiliares
a = cara_mala.arista_incidente
v1 = a.origen
v2 = a.final
v3 = a.siguiente.final
v4 = a.anterior.origen

# Creamos la arista y sus atributos. Modificamos los atributos de las aristas.
b = Arista(v3,v1)
b.anterior = a.siguiente
b.siguiente = a

a.anterior = b # a.siguiente es el mismo
a.siguiente.siguiente = b

# Creamos la gemela y sus atributos. Modificamos los atributos de las aristas.
c = Arista(v1,v3)
b.gemela = c
c.anterior = a.anterior
c.siguiente = a.anterior.anterior
c.gemela = b

a.anterior.siguiente = c
a.siguiente.siguiente.anterior = c

# Creamos las caras y sus atributos. Modificamos los atributos
cara_b = Cara(a)
b.cara = cara_b
cara_c = Cara(a.anterior)
c.cara = cara_c

a.cara = cara_b
a.siguiente.cara = cara_b

c.siguiente.cara = cara_c
c.anterior.cara = cara_c

# Modificamos la DCEL
triangulacion.lista_aristas[b] = b
triangulacion.lista_aristas[c] = c
del(triangulacion.lista_caras[indice_cara_mala])
triangulacion.lista_caras.extend([cara_b, cara_c])

print(triangulacion.inspector_integridad)

return triangulacion
"""



def genera_nube_puntos(n, entero = False):
    size = 10    
    if entero: puntos = [Punto(random.randint(0, size), random.randint(0, size)) for _ in range(n)]
    else: puntos = [Punto(random.uniform(0, size), random.uniform(0, size)) for _ in range(n)]    
    return list(set(puntos))


def comprueba_triangulacion(puntos):
    
    triangulos = triangulacion_delaunay_bruta(puntos)
    triangulacion = convierte_lista_triangulos_a_DCEL(triangulos)
    estropea(triangulacion)
    arregla(triangulacion)
    
    # Extra: en el diccionario "grado" introduce el valor del grado de cada vértice de la triangulación
    grado = {}
    for p in triangulacion.lista_vertices.keys():
        e_inicial = triangulacion.lista_vertices[p]    
        g = 0
        e = e_inicial
        tope = e.gemela is None        
        while not tope:            
            e = e.gemela.siguiente # giro en sentido negativo
            g += 1
            tope = e.gemela is None
            if e == e_inicial: break              
        if tope: # p está en la envolvente y no se puede girar 360º recorriendo todas las aristas que salen de p
                 # así que nos movemos en sentido positivo desde e hasta encontrar envolvente de nuevo (arista sin gemela)
            g = 1                   
            while e.anterior.gemela is not None:            
                e = e.anterior.gemela # giro en sentido positivo
                g += 1                
            g += 1
        grado[p] = g        
    triangulacion.plot(grado)
    
    return

puntos = genera_nube_puntos(10, entero = False)
comprueba_triangulacion(puntos)

