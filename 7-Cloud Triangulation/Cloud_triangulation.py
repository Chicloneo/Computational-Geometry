"""PRACTICA 7: 11-03-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p7.py)
- Trabaja en la función triangula_nube (línea 225)
- En la parte central del código hay varios algoritmos del cálculo de envolventes convexas
- Para comprobar su funcionamiento ve al final del código y ejecuta la comprobación correspondiente
- Sube el código .py a la tarea del CV al final de la clase
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

def ordena_angularmente(puntos: list[Punto]) -> list[Punto]:
    # Input: puntos es una lista de Punto
    # Output: lista de puntos ordenada angularmente (según el ángulo desde el origen)
    # Sugerencia: usar una función de comparación auxiliar como la esbozada
    def angulo(p: Punto) -> float:
        return math.atan2(p.y, p.x)
    return sorted(puntos, key = angulo)

def punto_en_triangulo(p: Punto, triangulo: list[Punto]) -> bool:
    # Input: p Punto y triangulo lista con 3 Puntos, los vértices del triángulo, que suponemos no alineados
    # Output: True/False si el punto p está en el interior del triángulo o no
    if orient(triangulo[0], triangulo[1], triangulo[2]) == -1:
        return punto_en_triangulo(p, triangulo[::-1])
    for i in range(len(triangulo)):
        if orient(triangulo[i-1], triangulo[i], p) != 1:
            return False
    return True

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

def puntos_tangencia_poligono(q: Punto, pol: list):
    # IMPORTANTE: q está en el semiplano {x < 0} y pol está en el semiplano {x >= 0} 
    # Input: q es un punto, pol es una lista de puntos que, en ese orden, son los vértices de un polígono (simple)
    # Output: lista con 2 Puntos (en cualquier orden)  
    def angulo(p):    
        return math.atan2(p.y - q.y, p.x - q.x)
    def distancia2(p):
        return (q.x - p.x) * (q.x - p.x) + (q.y - p.y) * (q.y - p.y)
    punto_tangencia_up = max(pol, key=lambda p: (angulo(p), -distancia2(p)))
    punto_tangencia_down = min(pol, key=lambda p: (angulo(p), distancia2(p)))    
    return [punto_tangencia_down, punto_tangencia_up]

################################ FIN LIBRERÍA GCOM ##########################################

##################### CÓDIGOS DE ENVOLVENTES CONVEXAS ########################################
def envolvente_convexa_Graham(puntos: list[Punto]) -> list[Punto]:
    """Cálculo de la envolvente convexa usando el algoritmo de Graham, generado por IA y retocado para casos extremos"""
    n = len(puntos)
    if n < 3: return puntos

    # 1. Encontrar el punto con la 'y' más baja (y la 'x' más baja en caso de empate)
    # Este será nuestro punto de pivote.
    pivote = min(puntos, key=lambda p: (p.y, p.x))

    # 2. Ordenar los puntos según el ángulo polar respecto al pivote
    # Usamos atan2 para calcular el ángulo de forma sencilla.
    def calcular_angulo(p):
        return math.atan2(p.y - pivote.y, p.x - pivote.x), (p.x-pivote.x)**2 + (p.y - pivote.y)**2
    
    # Quitamos el pivote de la lista para ordenar el resto
    puntos_restantes = [p for p in puntos if p != pivote]
    puntos_ordenados = sorted(puntos_restantes, key=calcular_angulo)

    lastangle = calcular_angulo(puntos_ordenados[-1])
    i = len(puntos_restantes) - 1
    while i >= 0 and abs(calcular_angulo(puntos_ordenados[i])[0] - lastangle[0]) < ERROR: i = i-1
    puntos_ordenados = puntos_ordenados[:i+1] + puntos_ordenados[i+1:][::-1]
    
    # 3. Construir la envolvente usando una pila (stack)
    envolvente = [pivote, puntos_ordenados[0]]

    for i in range(1, len(puntos_ordenados)):
        punto_actual = puntos_ordenados[i]
        
        # Mientras el giro no sea hacia la izquierda (CCW), eliminamos el último punto
        # orient(a, b, c) == 1 significa giro a la izquierda.
        while len(envolvente) > 1 and orient(envolvente[-2], envolvente[-1], punto_actual) == -1:
            envolvente.pop()
            
        envolvente.append(punto_actual)

    return envolvente

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

def envolvente_convexa_divide_y_venceras(puntos):
    """Cálculo de la envolvente convexa usando divide y vencerás"""
    # Input: lista de puntos
    # Output: lista ordenada positivamente de los puntos que componen la envolvente convexa
    #caso base: n = 1 o 2 puntos
    if len(puntos) <= 2: return puntos
    
    puntos.sort(key = lambda p: (p.x, p.y))
    mitad = len(puntos)//2
    
    pol1 = envolvente_convexa_divide_y_venceras(puntos[:mitad])
    pol2 = envolvente_convexa_divide_y_venceras(puntos[mitad:])
    
    tang_sup = tangente_superior(pol1, pol2)
    i1, i2 = pol1.index(tang_sup[0]), pol2.index(tang_sup[1])

    tang_inf = tangente_superior(pol1, pol2, inferior = True)
    j1, j2 = pol1.index(tang_inf[0]), pol2.index(tang_inf[1])
    
    if i1 == j1: pol = pol1[i1:]+pol1[:j1]
    elif i1 < j1: pol = pol1[i1:j1+1]
    else: pol = pol1[i1:]+pol1[:j1+1]
    if j2 == i2: pol.extend(pol2[j2+1:] + pol2[:i2+1])
    elif j2 < i2: pol.extend(pol2[j2:i2+1])
    else: pol.extend(pol2[j2:] + pol2[:i2+1])
     
    return pol


def envolvente_convexa_incremental(puntos): 
    """Cálculo de la envolvente convexa usando el algoritmo incremental"""
    n = len(puntos)
    if n < 3: return puntos

    puntos.sort(key = lambda p: (p.x, p.y)) #ordenamos los puntos de izquierda a derecha 
    hull = [puntos[-1], puntos[-2]] #inicializamos la hull con los dos puntos más a la derecha
    puntos_alineados = False #booleano para atender la situación en que los primeros puntos por la derecha están alineados
    for k in range(3, n+1):
        q = puntos[n-k]
        [p_inf, p_sup] = puntos_tangencia_poligono(q, hull)        
        i, j = hull.index(p_inf), hull.index(p_sup) 
        # las dos primeras condiciones del siguiente if solo se pueden dar cuando hay puntos alineados
        if i == j:
            hull.append(q) #si la tangente superior e inferior es la misma es porque los puntos que hemos procesado, incluido el actual, están todos alineados
            puntos_alineados = True
            continue
        if puntos_alineados: #si q es el primer punto no alineado tengo que decidir cómo orientar bien la envolvente (que hasta ahora era un segmento)
            if orient(hull[0], hull[1], q) != 1: hull.reverse()
            hull.append(q)
            puntos_alineados = False
        else: #caso "normal" en el que los puntos anteriores no están alineados
            if i < j: hull = [q] + hull[i:j+1]
            else: hull = [q] + hull[i:] + hull[:j+1]
    return hull

##################### FIN CÓDIGOS DE ENVOLVENTES CONVEXAS ########################################

def triangula_nube(puntos):
    """Input: lista de puntos
    Output: lista de los triángulos que forman una triangulación (cada triángulo es una lista con 3 puntos)
            o de las diagonales"""
    """Cálculo de la envolvente convexa usando el algoritmo de Graham, generado por IA y retocado para casos extremos"""
    triangulos = []
    lista_puntos = puntos
    pivote = min(puntos, key=lambda p: (p.y, p.x))
    puntos_restantes = [punto for punto in lista_puntos if punto != pivote] #quito el pivote

    def angulo_pivote(p:Punto):
        return math.atan2(p.y - pivote.y, p.x - pivote.x), math.sqrt((p.y - pivote.y)**2 + (p.x - pivote.x)**2)
    
    puntos_restantes_ordenados = sorted(puntos_restantes, key = angulo_pivote)
    n = len(puntos_restantes_ordenados) #la lista original tiene n+1 puntos

    for i in range(n-1):
        triangulos.append([pivote, puntos_restantes_ordenados[i], puntos_restantes_ordenados[i+1]])

    # Hasta aquí tenemos todos los triángulos desde el pivote (el abanico)
    puntos = [pivote] + puntos_restantes_ordenados
    

    # envolvente_convexa = envolvente_convexa_Graham(puntos_restantes_ordenados) 
    # no puedo hacer la envolvente convexa de puntos_restantes_ordenados, porque el algoritmo volvería a buscar un nuevo pivote y ordenar angularmente
    # una lista que no tiene el pivote
    # creo que no hace falta llamar a la función Graham, sino que hay que usar su misma filosofía <<<----------------------------------
    # if puntos_restantes_ordenados[i] not in envolvente_convexa: #añado su anterior y su siguiente ...  NO funciona si hay 2 vértices cóncavos

    envolvente = [puntos[0], puntos[1]]
    for i in range(2,len(puntos)):
        # Explicar la importancia del while (no puede ser if)
        while len(envolvente) > 0 and orient(envolvente[-2], envolvente[-1], puntos[i]) == -1: #len(envolvente) > 0 para salir del bucle cuando se vacíe 
            triangulos.append([envolvente[-2], envolvente[-1], puntos[i]])
            envolvente.pop()
        
        envolvente.append(puntos[i])

    return triangulos



def genera_nube_puntos(n, entero = False):
    size = 10    
    if entero: puntos = [Punto(random.randint(0, size), random.randint(0, size)) for _ in range(n)]
    else: puntos = [Punto(random.uniform(0, size), random.uniform(0, size)) for _ in range(n)]    
    return list(set(puntos))

def comprueba_triangulacion_nube(puntos):    
    #puntos = [Punto(8, 6), Punto(5, 9), Punto(12, 2), Punto(3, 14), Punto(14, 0), Punto(17, 7), Punto(8, 1), \
    #          Punto(11, 9), Punto(7, 14), Punto(2, 8), Punto(11, 16), Punto(15, 14)]
    outcome = triangula_nube(puntos)
    print(outcome)
    diagonales = [o for o in outcome if len(o) == 2]
    triangulos = [o for o in outcome if len(o) == 3]
    
    plt.plot([p.x for p in puntos], [p.y for p in puntos], 'bo')
    
    for s in diagonales:
        plt.plot([p.x for p in s], [p.y for p in s], color = 'red')
        
    for t in triangulos:
        t.append(t[0])                
        plt.fill([p.x for p in t], [p.y for p in t], alpha = 0.3)
        plt.plot([p.x for p in t], [p.y for p in t])
    
    plt.show() 


puntos = genera_nube_puntos(10, entero = False)
comprueba_triangulacion_nube(puntos)
