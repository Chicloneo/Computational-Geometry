"""PRACTICA 3: 11-02-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p1.py)
- Trabaja en las funciones "interseca_segmentos" (línea 85), "tangentes_exteriores" (línea 93)
- Para comprobar su funcionamiento ve al final del código y ejecuta la comprobación correspondiente
- Sube el código .py a la tarea del CV al final de la clase
"""

import random
import math
import numpy as np
import matplotlib.pyplot as plt
ERROR = 1e-9
import numpy as np
from multiprocessing import Pool

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

def prod_vect(u, v):
    return u.x * v.y - u.y * v.x
def det(a, b, c):
    return prod_vect(b - a, c - a)

def alineados(a: Punto, b: Punto, c: Punto) -> bool:
    # Devuelve True/False si los puntos a, b, c están alineados/no lo están
    return abs(det(a, b, c)) < ERROR

def orient(a: Punto, b: Punto, c: Punto) -> int:
    """ 1/0/-1 si c a la izquierda/alineado/a la derecha de ab"""    
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
    

def interseca_segmentos(s: list[Punto], t: list[Punto]):
    # Input: dos segmentos (listas con dos puntos)
    # Output: None / un punto / un segmento (lista con dos puntos) en función de si su intersección es vacía / un punto / un segmento
    # output = None / output = Punto(3,7) / 

    if not segmentos_se_cortan(s,t):
        return None
    
    else:
        if alineados(s[0],s[1],t[0]) and alineados(s[0],s[1],t[1]): #se cortan en un segmento
            #buscamos cuál es el punto de t (t_0 o t_1) que está dentro de s
            if s[0].x <= t[0].x and t[0].x <= s[1].x:
                if s[1].x <= t[1].x:
                    return [t[0],s[1]]
                if t[1].x <= s[0].x:
                    return [s[0],t[0]]
            if s[0].x <= t[1].x and t[1].x <= s[1].x:
                if t[0].x <= s[0].x:
                    return [s[0],t[1]]
                if s[1].x <= t[0].x:
                    return [t[1],s[1]]
            
        if not (alineados(s[0],s[1],t[0]) and alineados(s[0],s[1],t[1])): #se cortan en un punto
            # y - y_{1} = m(x - x_{1})
            vector_director_s = s[1] - s[0]
            x_1_s = s[0].x
            y_1_s = s[0].y
            m_s = vector_director_s.y / vector_director_s.x
            
            vector_director_t = t[1] - t[0]
            x_1_t = t[0].x
            y_1_t = t[0].y
            m_t = vector_director_t.y / vector_director_t.x
            
            # Sistema:
            #  1x + 6y = 27
            #  7x - 3y = 9

            # Matriz de coeficientes (A)
            A = np.array([[m_s, -1], [m_t, -1]])

            # Vector de términos independientes (B)
            B = np.array([m_s * x_1_s - y_1_s, m_t * x_1_t - y_1_t])

            # Resolver el sistema
            x,y = np.linalg.solve(A, B)
            #punto corte es de tipo 'numpy.float64'
            #El output tiene que estar en formato Punto
            return Punto(x,y)


def tangentes_exteriores(pol1: list[Punto], pol2: list[Punto]) -> list[Punto]:
    """Encuentra las dos tangentes exteriores comunes a dos polígonos convexos"""
    # Input: pol1 y pol2 son dos polígonos convexos, pol1 en {x<0} y pol2 en {x>0}. Los polígonos están positivamente orientados
    # Output: una lista con 4 puntos (los dos primeros determinan una tangente y los dos últimos la otra)
    
    tangente_arriba = [pol1[0], pol2[0]]
    hemos_cambiado = True
    while hemos_cambiado:
        hemos_cambiado = False
        for punto in pol1:
            if orient(tangente_arriba[0],tangente_arriba[1],punto) == 1:
                tangente_arriba[0] = punto
                hemos_cambiado = True

        for punto in pol2:
            if orient(tangente_arriba[0],tangente_arriba[1],punto) == 1:
                tangente_arriba[1] = punto
                hemos_cambiado = True

    tangente_abajo = [pol1[0], pol2[0]]
    hemos_cambiado = True
    while hemos_cambiado:
        hemos_cambiado = False
        for punto in pol1:
            if orient(tangente_abajo[0],tangente_abajo[1],punto) == -1:
                tangente_abajo[0] = punto
                hemos_cambiado = True

        for punto in pol2:
            if orient(tangente_abajo[0],tangente_abajo[1],punto) == -1:
                tangente_abajo[1] = punto
                hemos_cambiado = True

    return tangente_arriba + tangente_abajo


def comprueba_interseccion_segmentos(s = None, t = None):
    alguno_es_None = s is None or t is None
    def punto_aleatorio():        
        return Punto(random.uniform(0, 1), random.uniform(0, 1))
    if s is None:
        s = [punto_aleatorio(), punto_aleatorio()]
    if t is None:
        t = [punto_aleatorio(), punto_aleatorio()]
    if alguno_es_None and random.randint(0,3) == 1: t[0] = s[0]
    def rectifica(seg, n):
        match n % 3:
            case 0: seg[1].x = seg[0].x
            case 1: seg[1].y = seg[0].y
        return seg
    if alguno_es_None: s, t = rectifica(s, random.randint(0,3)), rectifica(t, random.randint(0,3))
    
    respuesta = interseca_segmentos(s, t)
    plt.plot([p.x for p in s], [p.y for p in s], 'bo-')
    plt.plot([p.x for p in t], [p.y for p in t], 'bo-')
    if respuesta is None:
        texto = 'Los segmentos NO se cortan'        
    elif isinstance(respuesta, Punto):
        plt.plot(respuesta.x, respuesta.y, 'ro')
        texto = 'Los segmentos se cortan en un punto'
    else: 
        plt.plot([p.x for p in respuesta], [p.y for p in respuesta], 'red')
        texto = 'Los segmentos se cortan en un segmento'
    plt.title(texto)
    plt.show()
    return


def simetriaOY(pol):
    pol_simetrico = [Punto(-p.x, p.y) for p in pol]
    return pol_simetrico[::-1]
def simetriaOX(pol):
    pol_simetrico = [Punto(p.x, -p.y) for p in pol]
    return pol_simetrico[::-1]

t0 = [Punto(0,0), Punto(2, 0), Punto(1,1)]
t1 = [Punto(0,0), Punto(1,1), Punto(0, 2)]
triangulos = [t0, simetriaOX(t0), t1, simetriaOY(t1)]
c0 = [Punto(0,0), Punto(2, 0), Punto(1,1), Punto(-1, 1)]
c1 = [Punto(0,0), Punto(2, 0), Punto(1,2), Punto(0, 1)]
c2 = [Punto(0,0), Punto(2, 0), Punto(3,1), Punto(-1, 2)]
cuadrilateros = [c0, c1, c2]
cuadrilateros += [simetriaOX(c) for c in cuadrilateros]
cuadrilateros += [simetriaOY(c) for c in cuadrilateros]

def genera_poligono_convexo(n):
    if n == 3: return random.choice(triangulos)
    if n == 4: return random.choice(cuadrilateros)
    radio = 1
    ang = [2 * math.pi * i / n for i in range(n)]
    eps = 5/n
    perturbacion = [Punto(eps * random.uniform(0,1), eps * random.uniform(0,1)) for _ in range(n)]
    pol = [Punto(radio * math.cos(ang[i]), radio * math.sin(ang[i])) + perturbacion[i] for i in range(n)]
    #comprobamos que es convexo el resultado
    for i in range(n):
        if orient(pol[i], pol[(i+1) % n], pol[(i+2) % n]) != 1 or segmentos_se_cortan([pol[i-3], pol[i-2]], [pol[i-1], pol[i]]):
            return genera_poligono_convexo(n)
    return pol

def comprueba_tangentes_exteriores(pol1 = None, pol2 = None, n_vertices = 8):
    # --- Plotting ---
    if pol1 is None:
        pol1 = genera_poligono_convexo(random.randint(3, n_vertices+1))
    if pol2 is None:
        pol2 = genera_poligono_convexo(random.randint(3, n_vertices+1))
    max_x = max(p.x for p in pol1)
    pol1 = [p - Punto(max_x+1, 0) for p in pol1]
    min_x = min(p.x for p in pol2)
    pol2 = [p - Punto(min_x-1, 0) for p in pol2]   
    # Close the polygon for plotting
    plot_data_x1, plot_data_x2 = [p.x for p in pol1], [p.x for p in pol2]
    plot_data_x1.append(pol1[0].x)
    plot_data_x2.append(pol2[0].x)
    plot_data_y1, plot_data_y2 = [p.y for p in pol1], [p.y for p in pol2]
    plot_data_y1.append(pol1[0].y)
    plot_data_y2.append(pol2[0].y)
    
    plt.fill(plot_data_x1, plot_data_y1, alpha = 0.2, color = 'blue')
    plt.fill(plot_data_x2, plot_data_y2, alpha = 0.2, color = 'blue')

    respuestas = tangentes_exteriores(pol1, pol2)
    plt.plot([respuestas[0].x, respuestas[1].x], [respuestas[0].y, respuestas[1].y], 'red')
    plt.plot([respuestas[2].x, respuestas[3].x], [respuestas[2].y, respuestas[3].y], 'red')
    plt.show()

# Para comprobar segmentos aleatorios
#s = [Punto(1,1),Punto(4,1)]
#t = [Punto(3,1),Punto(6,1)]
s = [Punto(1,1),Punto(2,2)]
t = [Punto(1,2),Punto(2,1)]
#comprueba_interseccion_segmentos()
#comprueba_interseccion_segmentos(s,t)
# Para comprobar segmentos elegidos:
# s, t = [Punto(0,0), Punto(2,0)], [Punto(1, -1), Punto(1,1)]
# comprueba_interseccion_segmentos(s, t)

comprueba_tangentes_exteriores()
# Para comprobar polígonos específicos:
# pol = [Punto(0,0), Punto(1,-1), Punto(1,2), Punto(0,1)]
# comprueba_tangentes_exteriores(pol, None)
