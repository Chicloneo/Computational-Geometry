"""PRACTICA 8: 18-03-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p8.py)
- Trabaja en la función triangula_delaunay_bruta (línea 112)
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
        return 1000000000 * int(self.x) + 1000 * int(self.y)


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
    if abs(d) < ERROR:
        return 0
    elif d > ERROR:
        return 1
    else:
        return -1


def ordena_angularmente(puntos: list[Punto]) -> list[Punto]:
    # Input: puntos es una lista de Punto
    # Output: lista de puntos ordenada angularmente (según el ángulo desde el origen)
    # Sugerencia: usar una función de comparación auxiliar como la esbozada
    def angulo(p: Punto) -> float:
        return math.atan2(p.y, p.x)

    return sorted(puntos, key=angulo)


def punto_en_triangulo(p: Punto, triangulo: list[Punto]) -> bool:
    # Input: p Punto y triangulo lista con 3 Puntos, los vértices del triángulo, que suponemos no alineados
    # Output: True/False si el punto p está en el interior del triángulo o no
    if orient(triangulo[0], triangulo[1], triangulo[2]) == -1:
        return punto_en_triangulo(p, triangulo[::-1])
    for i in range(len(triangulo)):
        if orient(triangulo[i - 1], triangulo[i], p) != 1:
            return False
    return True


def punto_en_segmento(p, s):
    # p punto, s segmento = lista con dos puntos
    # devuelve True si p está dentro del segmento, incluyendo sus extremos
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
        return punto_en_segmento(s[0], t) or punto_en_segmento(s[1], t) or punto_en_segmento(t[0],
                                                                                             s) or punto_en_segmento(
            t[1], s)
        # si tres puntos están alineados (y no los cuatro) devuelve True solo si uno está dentro del otro segmento
    for p in s:
        if alineados(p, t[0], t[1]): return punto_en_segmento(p, t)
    for p in t:
        if alineados(p, s[0], s[1]): return punto_en_segmento(p, s)
        # (sabemos que no hay tres alineados) usamos xor = '^' (True ^ False = True, F^T=T T^T=F, F^F=F)
    return (orient(s[0], s[1], t[0]) * orient(s[0], s[1], t[1]) == -1) and (
                orient(t[0], t[1], s[0]) * orient(t[0], t[1], s[1]) == -1)


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

def dentro_circunf(a, b, c, d):
    # Utiliza la IA para obtener esta función
    """Input: cuatro puntos a, b, c, d
    Output: 1/0/-1 dependiendo de si d está dentro/sobre/fuera de la circunferencia circunscrita de a, b, c"""

    # PASO 1: Trasladamos el sistema de coordenadas para que 'd' sea el origen (0,0).
    # Esto reduce el cálculo de un determinante 4x4 a uno 3x3, haciéndolo mucho más rápido.
    adx = a.x - d.x
    ady = a.y - d.y
    bdx = b.x - d.x
    bdy = b.y - d.y
    cdx = c.x - d.x
    cdy = c.y - d.y

    # PASO 2: Calculamos los menores del determinante 3x3
    abdet = adx * bdy - bdx * ady
    bcdet = bdx * cdy - cdx * bdy
    cadet = cdx * ady - adx * cdy

    # PASO 3: Elevamos los puntos al paraboloide z = x^2 + y^2
    alift = adx ** 2 + ady ** 2
    blift = bdx ** 2 + bdy ** 2
    clift = cdx ** 2 + cdy ** 2

    # PASO 4: Calculamos el determinante final
    incircle_det = alift * bcdet + blift * cadet + clift * abdet

    # PASO 5: Ajuste de orientación.
    # El signo del determinante asume que a, b, c están en orden antihorario (CCW).
    # Si están en orden horario, el signo se invierte. Debemos comprobar su orientación.
    orient_abc = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    # Si el triángulo a,b,c es horario (CW), invertimos el signo del determinante
    if orient_abc < -ERROR:
        incircle_det = -incircle_det

    # PASO 6: Devolvemos el resultado considerando el margen de tolerancia (ERROR)
    if abs(incircle_det) < ERROR:
        return 0  # d está exactamente sobre la circunferencia (Cocircular)
    elif incircle_det > 0:
        return 1  # d está estrictamente dentro de la circunferencia
    else:
        return -1  # d está estrictamente fuera de la circunferencia


#print(dentro_circunf(Punto(1,1),Punto(-1,1), Punto(-1,-1), Punto(0,0)))

def ordena_angularmente_foco(puntos: list[Punto], foco:Punto) -> list[Punto]:
    def angulo(p: Punto) -> float:
        ang = math.atan2(p.y - foco.y, p.x - foco.x)
        return ang if ang >= 0 else ang + 2 * math.pi
    return sorted(puntos, key=angulo)

def triangula_conciclicos(puntos:list[Punto])->list[list[Punto]]:
    """
    Input: lista de puntos concíclicos
    Output: lista de triangulos
    """
    foco = puntos[0]
    lista_puntos = puntos[1:]
    ordenados = ordena_angularmente_foco(lista_puntos, foco)
    #print(ordenados)

    triangulos = []

    for i in range(len(ordenados) - 1):
        triangulos.append([foco, ordenados[i], ordenados[i+1]])

    return triangulos


def triangulacion_delaunay_bruta(puntos):
    """ Input: lista de los puntos de la nube
    Output: lista de triángulos (lista de tres puntos = vértices) """
    #triangulos = triangula_conciclicos(puntos)
    triangulos = []
    conciclicos_totales = []
    for i in range(len(puntos)):
        for j in range(i+1, len(puntos)):
            for k in range(j+1, len(puntos)):
                conciclicos = [puntos[i], puntos[j], puntos[k]]
                posible_triangulo = [puntos[i], puntos[j], puntos[k]]
                triangulo_valido = True #Si nunca se encuentra algún punto dentro, es válido
                for l in range(len(puntos)):
                    if l != i and l!= j and l!=k:
                        if dentro_circunf(puntos[i], puntos[j], puntos[k], puntos[l]) == 1: 
                            triangulo_valido = False
                            break
                        if dentro_circunf(puntos[i], puntos[j], puntos[k], puntos[l]) == 0: 
                            conciclicos.append(puntos[l])

                if triangulo_valido: #el triángulo es válido si no tiene en el interior o si (no tiene en el interior + tiene conciclicos)
                    if len(conciclicos) > 3:
                        if set(conciclicos) not in conciclicos_totales:
                            conciclicos_totales.append(set(conciclicos))
                            triangulos_correctos = triangula_conciclicos(conciclicos)
                            triangulos.extend(triangulos_correctos)
                    else:
                        triangulo_correcto = posible_triangulo
                        triangulos.append(triangulo_correcto)
    return triangulos


def genera_nube_puntos(n, entero=False):
    size = 10
    if entero:
        puntos = [Punto(random.randint(0, size), random.randint(0, size)) for _ in range(n)]
    else:
        puntos = [Punto(random.uniform(0, size), random.uniform(0, size)) for _ in range(n)]
    return list(set(puntos))


def comprueba_triangulacion_nube(puntos):
    # puntos = [Punto(8, 6), Punto(5, 9), Punto(12, 2), Punto(3, 14), Punto(14, 0), Punto(17, 7), Punto(8, 1), \
    #          Punto(11, 9), Punto(7, 14), Punto(2, 8), Punto(11, 16), Punto(15, 14)]
    outcome = triangulacion_delaunay_bruta(puntos)
    diagonales = [o for o in outcome if len(o) == 2]
    triangulos = [o for o in outcome if len(o) == 3]

    plt.plot([p.x for p in puntos], [p.y for p in puntos], 'bo')

    for s in diagonales:
        plt.plot([p.x for p in s], [p.y for p in s], color='red')

    for t in triangulos:
        t.append(t[0])
        plt.fill([p.x for p in t], [p.y for p in t], alpha=0.3)
        plt.plot([p.x for p in t], [p.y for p in t])

    plt.show()


#puntos = genera_nube_puntos(10, False)
#comprueba_triangulacion_nube(puntos)
# Caso con puntos concíclicos
puntos = [Punto(11.924500897298753, 10.0), Punto(10.962250448649376, 11.666666666666666), Punto(9.037749551350624, 11.666666666666666),\
Punto(8.075499102701247, 10.0), Punto(9.037749551350624, 8.333333333333334), Punto(10.962250448649376, 8.333333333333334), Punto(14, 18), \
Punto(4, 6), Punto(18, 2), Punto(4, 12), Punto(14, 0), Punto(8, 4), Punto(5, 10), Punto(4, 8), Punto(20, 12), Punto(2, 11), Punto(4, 0), Punto(18, 0)]
#puntos = [Punto(1,0),Punto(0,1), Punto(-1,0), Punto(0,-1)]
comprueba_triangulacion_nube(puntos)