"""PRACTICA 5: 25-02-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p5.py)
- Trabaja en la función envolvente_convexa (línea 95)
- Para comprobar su funcionamiento ve al final del código y ejecuta la comprobación correspondiente
- Sube el código .py a la tarea del CV al final de la clase
- Termina la práctica en casa durante los próximos días y súbela al CV
"""

import random
import math
import numpy as np
import matplotlib.pyplot as plt
ERROR = 1e-9

class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    # se puede definir un punto con coordenadas dadas así: p = Punto(2, 3)
    def __repr__(self):
        return "({0},{1})".format(self.x, self.y)  
    def __add__(self, other):
        return Punto(self.x + other.x, self.y + other.y)  
    def __sub__(self, other):
        return Punto(self.x - other.x, self.y - other.y)
    def __eq__(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) < ERROR
    def __hash__(self):
        return 1000000000*int(self.x) + 1000*int(self.y)

def prod_vect(u, v):
    return u.x * v.y - u.y * v.x
def det(a, b, c):
    return prod_vect(b - a, c - a)

def alineados(a: Punto, b: Punto, c: Punto) -> bool:
    # Devuelve True/False si los puntos a, b, c están alineados/no lo están
    return abs(det(a, b, c)) < ERROR

def orient(a: Punto, b: Punto, c: Punto) -> int:
    # 1/0/-1 si c a la izquierda/alineado/a la derecha de ab    
    d = det(a, b, c)
    if abs(d) < ERROR: return 0
    elif d > ERROR: return 1
    else: return -1

def punto_en_segmento(p, s):
    #p punto, s segmento = lista con dos puntos
    #devuelve True si p está dentro del segmento, incluyendo sus extremos
    if not alineados(p, s[0], s[1]):
        return False
    if abs(s[0].x - s[1].x) > ERROR:
        return min(s[0].x, s[1].x) - ERROR <= p.x <= max(s[0].x, s[1].x) + ERROR
    else:
        return min(s[0].y, s[1].y) - ERROR <= p.y <= max(s[0].y, s[1].y) + ERROR
def segmentos_se_cortan(s: list[Punto], t: list[Punto]) -> bool:
    # Input: s, t son listas con dos puntos, los extremos de los segmentos s y t.
    # Output: True/False decidiendo si s y t se cortan (incluyendo solaparse o cortarse en un extremo)
    # si los cuatro puntos están alineados
    if alineados(s[0], s[1], t[0]) and alineados(s[0], s[1], t[1]):
        return punto_en_segmento(s[0], t) or punto_en_segmento(s[1], t) or punto_en_segmento(t[0], s) or punto_en_segmento(t[1], s)        
    #si tres puntos están alineados (y no los cuatro) devuelve True solo si uno está dentro del otro segmento
    for p in s:
        if alineados(p, t[0], t[1]): return punto_en_segmento(p, t)        
    for p in t:
        if alineados(p, s[0], s[1]): return punto_en_segmento(p, s)        
    #(sabemos que no hay tres alineados) usamos xor = '^' (True ^ False = True, F^T=T T^T=F, F^F=F)
    return (orient(s[0], s[1], t[0]) * orient(s[0], s[1], t[1]) == -1) and (orient(t[0], t[1], s[0]) * orient(t[0], t[1], s[1]) == -1)

def punto_en_poligono(q: Punto, pol: list[Punto]) -> bool:
    # Input: q es un punto, pol es una lista de puntos que, en ese orden, son los vértices de un polígono (simple)
    # Output: True/False decidiendo si q está dentro de pol (incluyendo la frontera)
    # Contamos el número de cortes del polígono con un segmento que comienza en q y acaba fuera del polígono.
    # Si es par q está fuera y si es impar está dentro del polígono
    maxcoord = max(p.x for p in pol)
    # El segmento acaba en un punto cuya coordenada x es mayor que las de los vértices del polígono y su coordenada y es un real aleatorio
    t = [q, Punto(maxcoord + 1, random.uniform(-1, 1))]
    count = 0
    n = len(pol)
    for i in range(n):
        # Nos avisa si se da la improbable situación en que el segmento pasa por un vértice de pol (en cuyo no bastaría con contar intersecciones)
        # y empezamos de nuevo
        if alineados(t[0], t[1], pol[i]):
            # print(t[0], t[1], pol[i], "El rayo pasa por un vértice")
            return punto_en_poligono(q, pol)
        # Si q está encima de un lado del polígono puede fallar la cuenta de intersecciones pero la función debe devolver True
        if punto_en_segmento(q, [pol[i], pol[(i+1)%n]]): return True
        if segmentos_se_cortan([pol[i], pol[(i+1)%n]], t):
            count = count + 1
    return (count % 2 == 1)    

def puntos_tangencia_poligono(q: Punto, pol: list):
    """Encuentra los dos puntos donde cortan las tangentes desde el Punto q al polígono pol.
    En caso de ambigüedad porque la tangente contenga un lado del polígono, elegimos el vértice más cercano a q"""
    # IMPORTANTE: q está en el semiplano {x < 0} y pol está en el semiplano {x >= 0} 
    # Input: q es un punto, pol es una lista de puntos que, en ese orden, son los vértices de un polígono (simple)
    # Output: lista con 2 Puntos (en cualquier orden)  
    """el punto de tangencia "superior" es el punto de pol tal que el ángulo del segmento orientado que lo une con q es mayor
    (en caso de empate cogemos aquel para el que la distancia a q sea menor (<=> -distancia(q,p) es mayor)"""
    def angulo(p):    
        return math.atan2(p.y - q.y, p.x - q.x)
    def distancia2(p):
        return (q.x - p.x) * (q.x - p.x) + (q.y - p.y) * (q.y - p.y)

    punto_tangencia_up = max(pol, key=lambda p: (angulo(p), -distancia2(p)))
    """el punto de tangencia "inferior" es el que minimiza el ángulo (en caso de empate elegimos el de distancia menor)"""
    punto_tangencia_down = min(pol, key=lambda p: (angulo(p), distancia2(p)))    
    return [punto_tangencia_down, punto_tangencia_up]


def tangente_superior(pol1, pol2, inferior = False):
    #pol1 es un polígono convexo en x<0 y pol2 un polígono convexo en x>0
    #elegimos como puntos iniciales aquellos cuyas coordenadas x sean más cercanas (a la derecha en pol1 y a la izda en pol2), así solo se avanzará
    #en sentido positivo en pol1 y en sentido negativo en pol2 hasta llegar a la tangente superior
    n, m = len(pol1), len(pol2)
    i1, i2 = max(range(n), key = lambda i: (pol1[i].x, pol1[i].y)), min(range(m), key = lambda i: (pol2[i].x, pol2[i].y))
    if inferior: delta = -1
    else: delta = 1
    avanzo = True
    while avanzo:
        avanzo = False
        #si el punto adyacente siguiente de pol1 está a la izquierda de [pol1[i1], pol2[i2]] avanzamos en pol1
        if orient(pol1[i1], pol2[i2], pol1[(i1 + delta)%n]) == delta:
            i1 = (i1 + delta) % n
            avanzo = True
        #si el punto adyacente anterior de pol2 está a la izquierda de [pol1[i1], pol2[i2]] retrocedemos en pol2
        elif orient(pol1[i1], pol2[i2], pol2[(i2 - delta) % m]) == delta:
            i2 = (i2 - delta) % m
            avanzo = True
        #si no se cumplen ninguna de las dos condiciones anteriores es que estamos en la tangente externa superior 
    return [pol1[i1], pol2[i2]]

def tangentes_exteriores(pol1: list[Punto], pol2: list[Punto]) -> list[Punto]:
    """Encuentra las dos tangentes exteriores comunes a dos polígonos convexos"""
    # Input: pol1 y pol2 son dos polígonos convexos, pol1 en {x<0} y pol2 en {x>0}. Los polígonos están positivamente orientados
    # Output: una lista con 4 puntos (los dos primeros determinan una tangente y los dos últimos la otra)
    return tangente_superior(pol1, pol2) + tangente_superior(pol1, pol2, True)

################################ FIN LIBRERÍA GCOM ##########################################3

#Orient: 1 izquierda, 0 alineado, -1 derecha

def distancia(p:Punto, q:Punto)->float:
    #Distancia de p a q
    return math.sqrt((q.y - p.y)**2 + (q.x - p.x)**2)

def envolvente_convexa(puntos):
    # Input: lista de puntos
    # Output: lista ordenada positivamente de los puntos que componen la envolvente" convexa
    
    #1.- Tomamos el punto más bajo. Desempate: el de más a la izquierda
    ordenados = sorted(puntos, key=lambda p: (p.y, p.x)) #sorted ordena de menor a mayor
    punto_inicial = ordenados[0]

    #2.- Calculamos sus "ángulos relativos", y los ordenamos angularmente.
    nuevos_puntos = []
    for punto in ordenados[1:]: #Quitamos el punto_inicial
        nuevos_puntos.append([punto, math.atan2(punto.y - punto_inicial.y, punto.x - punto_inicial.x)])
    #Ordenar por ángulo, y para ángulos iguales por distancia decreciente (más lejano primero)
    nuevos_ordenados = sorted(nuevos_puntos, key=lambda p: (p[1], p[0].y, distancia(punto_inicial, p[0]))) 

    #------------------------------------------------------------------------- (*)

    lista_alineados_finales = nuevos_ordenados[::-1] #invertimos la lista
    indice = 0
    for punto in lista_alineados_finales:
        if punto[1] == lista_alineados_finales[0][1]:
            indice += 1
    indice -= 1

    #Los 'indice' últimos elementos de la lista nuevos_ordenados tienen la misma arcotangente. Invertimos ese orden
    elementos_con_la_misma_atan = lista_alineados_finales[:indice+1]
    print('elementos con la misma atan', elementos_con_la_misma_atan)

    for i in range(indice):
        nuevos_ordenados.pop()

    nuevos_ordenados = nuevos_ordenados + elementos_con_la_misma_atan

    #------------------------------------------------------------------------- (*)

    #3.- Nos olvidamos de las arcotangentes y nos quedamos solo con los puntos. Le añadimos el punto inicial.
    lista_puntos = [nuevos_ordenados[i][0] for i in range(len(nuevos_ordenados))]
    lista_puntos = [punto_inicial] + lista_puntos 

    print(lista_puntos)

    #4.- Iteramos sobre los puntos
    #El primero y el segundo siempre están
    envolvente = [lista_puntos[0],lista_puntos[1]]
    ultimo_lado = [envolvente[-2],envolvente[-1]]

    for punto in lista_puntos[2:]:
        ultimo_lado = [envolvente[-2],envolvente[-1]]
        # Mientras giremos a la derecha, eliminar el último
        while orient(ultimo_lado[0], ultimo_lado[1], punto) == -1:
            envolvente.pop()
            ultimo_lado = [envolvente[-2],envolvente[-1]]
        envolvente.append(punto)

    return envolvente

"""
Explicación de (*):
Nuestro criterio de desempate es la distancia al punto inicial. Pero esto nos crea un problema. En la "última" (posible) secuencia de puntos alineados, 
nuestro criterio los ordena en orden ascendente, pero al recorrer la envolvente en sentido antihorario, queremos que los recorra en orden descendente.
Por ello, lo que hacemos es lo siguiente:
1.- Invertimos la lista.
2.- Buscamos cuáes son los elementos con el mismo ángulo relativo.
3.- Nos guardamos un índice, que es el número de elementos con el mismo ángulo.
4.- Quitamos (por el final) el mismo número de elementos que 'índice'.
5.- Los volvemos añadir, pero esta vez, invertidos. Es decir, en orden "desdencente".
Por tanto, lo que tenemos es casi la misma lista que la inicial, pero con os últimos puntos invertidos de orden.
Hemos añadido funciones de orden lineal, así que no afecta a nuestra complejidad
"""
        

def comprueba_envolvente_convexa(puntos = None, envolvente = None):
    if envolvente is None:
        envolvente = envolvente_convexa(puntos)
    plt.plot([p.x for p in puntos], [p.y for p in puntos], 'bo')
    envolvente.append(envolvente[0])
    plt.plot([p.x for p in envolvente], [p.y for p in envolvente], 'ro-')
    plt.show()
    return


def genera_input(n_puntos, enteros = False):
    if enteros: puntos = [Punto(random.randint(0, 5), random.randint(0, 5)) for _ in range(n_puntos)]    
    else: puntos = [Punto(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(n_puntos)]    
    return list(set(puntos))

puntos = genera_input(100, True)
#puntos = [Punto(2,10),Punto(-1,3),Punto(-10,-10),Punto(8,-5),Punto(-15,1), Punto(1,0)]
#print(envolvente_convexa(puntos))
#puntos = [Punto(0,0),Punto(1,0), Punto(2,0), Punto(2,2), Punto(0,2), Punto(0,1)]
#puntos = [Punto(0,1), Punto(0,2), Punto(0,0)]
comprueba_envolvente_convexa(puntos, None)

