#Entrego esta práctica con retraso, porque falté el día de la práctica 4 debido a falta justificada.

"""PRACTICA 4: 18-02-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p4.py)
- Obtén la función envolvente_convexa_IA preguntando a una IA (línea 95)
- Trabaja en las funciones "rodea_la_finca", "arbol_caido"
- Para comprobar su funcionamiento ve al final del código y ejecuta la comprobación correspondiente
- Sube el código .py a la tarea del CV al final de la clase
"""

import random
import math
#import numpy as np
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
        return abs(self.x - other.x) + abs(self.y + other.y) < ERROR
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

################################ FIN LIBRERÍA GCOM ##########################################3

def envolvente_convexa_IA(puntos):
    # Input: lista de puntos
    # Output: lista ordenada positivamente de los puntos que componen la envolvente convexa
    # Eliminamos duplicados por coordenadas
    pts_unique = list({(p.x, p.y): p for p in puntos}.values())
    n = len(pts_unique)
    if n == 0:
        return []
    if n == 1:
        return [pts_unique[0]]

    # Ordenar por x, luego por y
    pts_sorted = sorted(pts_unique, key=lambda p: (p.x, p.y))

    # Construcción de la envolvente: Monotone Chain (Andrew)
    lower = []
    for p in pts_sorted:
        while len(lower) >= 2 and det(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts_sorted):
        while len(upper) >= 2 and det(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenar sin repetir los extremos
    convex = lower[:-1] + upper[:-1]
    return convex

def comprueba_envolvente_convexa(puntos = None, envolvente = None):
    if envolvente is None:
        envolvente = envolvente_convexa_IA(puntos)
    plt.plot([p.x for p in puntos], [p.y for p in puntos], 'bo')
    envolvente.append(envolvente[0])
    plt.plot([p.x for p in envolvente], [p.y for p in envolvente], 'ro-')
    plt.plot(0,0, 'ko')
    plt.text(0,0,'Casa')
    plt.show()
    return

def distancia(P:Punto, Q:Punto) -> float:
    return math.sqrt((Q.x-P.x)**2 + (Q.y-P.y)**2)

def rodea_la_finca(puntos):
    """Pepita vive en (0,0) y tiene una finca (poligonal convexa) vallada, de forma que cada tramo (rectilíneo) de valla une
    dos de sus árboles. También tiene otros árboles en el interior de su finca. Hoy tiene que instalar un sensor en cada árbol del borde de la finca.
    Camina a velocidad constante 1 y tarda tiempo 2 en colocar cada sensor. Al final de la tarea volverá a su casa.
    Encuentra el camino que permita a Pepita completar la tarea más rápido y el tiempo que tardará."""
    # Input: lista de puntos con la posición de sus árboles (los del borde de la finca y los interiores)
    # Output: tiempo mínimo que tardará Pepita
    
    casa = Punto(0,0)
    distancias = [distancia(casa,puntos[i]) for i in range(len(puntos))]
    # elegimos el árbol más cercano para iniciar (valor float) y su índice
    start_dist = distancias[0]
    indice = 0
    for i in range(len(distancias)):
        if distancias[i] < start_dist:
            start_dist = distancias[i]
            indice = i
    start_point = puntos[indice]

    #construyo los segmentos que recorre Pepita. Cuando llega al último (sin repetir el primero) vuelve a su casa.
    recorrido = [casa, start_point] + puntos[indice:] + puntos[:indice] + [casa]
    distance = 0
    # sumamos las distancias entre elementos consecutivos
    for i in range(len(recorrido)-1):
        distance += distancia(recorrido[i],recorrido[i+1])
    # sumamos 1 segundo por cada punto (porque tarda en ellos un segundo más)
    return distance + len(puntos)
    

def genera_input(n_puntos):
    puntos = [Punto(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(n_puntos)]    
    if punto_en_poligono(Punto(0,0), envolvente_convexa_IA(puntos)): return puntos
    else: return genera_input(n_puntos)

puntos = genera_input(10)
comprueba_envolvente_convexa(puntos, None)
#print("El tiempo que tardará Pepita es: ", rodea_la_finca(puntos))

def perimetro(puntos):
    distance = 0
    for i in range(len(puntos)):
        distance += distancia(puntos[i],puntos[(i+1)%len(puntos)])
    return distance

def arbol_caido(puntos):
    """Una tormenta ha destrozado la valla de la finca y derribado un árbol del borde. Pepita tiene que colocar una cinta provisional
    que rodee su finca, de árbol en árbol siguiendo la antigua valla excepto en torno al árbol caído, de forma que todos sus árboles queden
    en el interior. Como no sabe qué árbol se ha caído, solo puede calcular una cota superior para la longitud de cinta que necesita."""
    # Input: lista de puntos con la posición de sus árboles (los del borde de la finca y los interiores)
    # Output: máxima longitud de cinta que necesitará

    # hacemos copias para no modificar la lista original
    puntos_aux = puntos[:]            # copia superficial
    del puntos_aux[0]
    cota_superior = perimetro(envolvente_convexa_IA(puntos_aux))

    # comprobamos borrando cada posible árbol del borde
    for i in range(1, len(puntos)):
        puntos_aux = puntos[:]        # copia fresca en cada iteración
        del puntos_aux[i]
        val = perimetro(envolvente_convexa_IA(puntos_aux))
        if val > cota_superior:
            cota_superior = val

    return cota_superior


puntos = genera_input(10)
comprueba_envolvente_convexa(puntos)
print("La longitud máxima de cinta que necesitará Pepita es: ", arbol_caido(puntos))



