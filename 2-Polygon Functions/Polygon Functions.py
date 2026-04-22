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


def puntos_tangencia_poligono(q: Punto, pol: list[Punto]) -> list:
    """Encuentra los dos puntos donde cortan las tangentes desde el Punto q al polígono pol.
    En caso de ambigüedad porque la tangente contenga un lado del polígono, elegimos el vértice más cercano a q"""
    # IMPORTANTE: q está en el semiplano {x < 0} y pol está en el semiplano {x >= 0} 
    # Input: q es un punto, pol es una lista de puntos que, en ese orden, son los vértices de un polígono (simple)
    # Output: lista con 2 Puntos (en cualquier orden)
    def angulo2(p: Punto) -> float:       
        return math.atan2(p.y-q.y,p.x-q.x)
    
    lista = sorted(pol, key = angulo2) #ordena la lista según su arcotangente (angulo2) 
    return [lista[0],lista[-1]]

def segmentos_se_cortan_interior(s: list[Punto], t: list[Punto]) -> bool:
    """
    Devuelve True si dos segmentoss e cortan en su interior, es decir, no en sus extremos. False e.c.c.
    """
    #print('len', len([s[0],s[1],t[0],t[1]]))
    #print('set', set([s[0],s[1],t[0],t[1]]))
    if len([s[0],s[1],t[0],t[1]]) != len(set([s[0],s[1],t[0],t[1]])):
        #Entonces hay elementos repetidos --> Algún vértice es el mismo
        return False
    else:
        #t[0] y t[1] están a lados distintos de s /\ s[0] y s[1] están a lados distintos de t
        return ( orient(s[0],s[1],t[0]) != orient(s[0],s[1],t[1]) ) and ( orient(t[0],t[1],s[0]) != orient(t[0],t[1],s[1]) )

def es_poligono(pol: list[Punto]) -> bool:
    #La idea era buena, pero si los segmentos se cortan solo en los puntos extremos, considera que sí se cortan
    #y yo en este modelo no lo estoy considerando así
    segmentos = [0]*len(pol)
    for i in range(len(pol)-1):
        segmentos[i] = [pol[i],pol[i+1]]
    segmentos[len(pol)-1] = [pol[len(pol)-1],pol[0]]
    #print('segmentos: ', segmentos)

    for segmento1 in segmentos:
        for segmento2 in segmentos:
            #print(f'{segmento1} y {segmento2}', segmentos_se_cortan_interior(segmento1, segmento2), 'se cortan')
            if segmentos_se_cortan_interior(segmento1, segmento2):
                return False 
    return True

def generate_random_polygon(n):
    # 1. Create random points
    points = [Punto(random.uniform(0,1), random.uniform(0,1)) for _ in range(n)]
    
    # 2. The "Untangling" loop
    swapped = True
    while swapped:
        swapped = False
        for i in range(n):
            for j in range(i + 2, n):
                # Don't check adjacent edges (they share a vertex)
                if i == 0 and j == n - 1: continue
                
                # Define the four points of the two edges we are checking
                p1, p2 = points[i], points[(i + 1) % n]
                p3, p4 = points[j], points[(j + 1) % n]
                
                if segmentos_se_cortan([p1, p2], [p3, p4]):
                    # 3. Swap the order of points between i+1 and j to uncross
                    points[i+1:j+1] = points[i+1:j+1][::-1]
                    swapped = True
    return points

def comprueba_puntos_tangencia_poligono(q = None, pol = None, n_vertices = 12):
    # --- Plotting ---
    if pol is None:
        pol = generate_random_polygon(n_vertices)
    # Close the polygon for plotting
    plot_data_x = [p.x for p in pol]
    plot_data_x.append(pol[0].x)
    plot_data_y = [p.y for p in pol]
    plot_data_y.append(pol[0].y)
    
    plt.figure(figsize=(6,6))
    plt.fill(plot_data_x, plot_data_y, alpha = 0.2, color = 'blue')

    if q is None: q = Punto(random.uniform(-2,-1), random.uniform(-.5,1.5))
    plt.plot(q.x, q.y, 'bo')
    res_tan = puntos_tangencia_poligono(q, pol)
    plt.plot([res_tan[0].x, q.x, res_tan[1].x], [res_tan[0].y, q.y, res_tan[1].y], 'ro-')
    plt.show()

def comprueba_es_poligono(pol = None):
    n_vertices = 10
    if pol is None:
        pol = generate_random_polygon(n_vertices)
    
    #if random.choice([True, False]):
    pol[0], pol[1] = pol[1], pol[0]
    
    plot_data_x = [p.x for p in pol]
    plot_data_x.append(pol[0].x)
    plot_data_y = [p.y for p in pol]
    plot_data_y.append(pol[0].y)
    
    plt.plot(plot_data_x, plot_data_y, 'bo-')
    respuesta = es_poligono(pol)
    texto = 'Sí' if respuesta else 'No'
    texto = texto + ' es polígono'
    plt.title(texto)
    plt.show()


pol = None
#pol = [Punto(0,0), Punto(1,0), Punto(1,1), Punto(0,1)]
#print(puntos_tangencia_poligono( Punto(-1,-1),pol))
#comprueba_puntos_tangencia_poligono(pol)
#comprueba_es_poligono([Punto(0,0),Punto(1,0),Punto(2,1),Punto(3,2),Punto(2,3)])
#comprueba_es_poligono([Punto(0,0),Punto(1,0),Punto(1,1),Punto(0,1)])

#print('1',segmentos_se_cortan_interior([Punto(0,0),Punto(1,1)],[Punto(0,1),Punto(1,0)]))
#print('2',len([Punto(0,0),Punto(1,1),Punto(0,1),Punto(1,0)]))
#print('3',set([Punto(0,0),Punto(1,1),Punto(0,1),Punto(1,0)]))
#comprueba_es_poligono([Punto(0,0),Punto(1,0),Punto(0,1),Punto(1,1)])
comprueba_es_poligono(pol)

#comprueba_segmentos_se_cortan()
# Segmentos que se cortan:
# comprueba_segmentos_se_cortan([Punto(0,1), Punto(2,1)], [Punto(1,0), Punto(1,2)])
# Segmentos que se cortan:
# comprueba_segmentos_se_cortan([Punto(0,1), Punto(2,1)], [Punto(0,1), Punto(1,2)])

# comprueba_punto_en_poligono()

# Polígono = cuadrado y punto definido
# pol = [Punto(0,0), Punto(1,0), Punto(1,1), Punto(0,1)]
# q = Punto(0.5, 0.5)
# comprueba_punto_en_poligono(q, pol)
