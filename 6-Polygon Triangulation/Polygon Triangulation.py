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

################################ FIN LIBRERÍA GCOM ##########################################3

def es_vertice_convexo(v:Punto, pol: list[Punto]) -> bool:
    """
    Input: vértice del polígono. Lista de vértices del polígono positivamente orientada.
    Output: Sí / No es un vértice convexo
    """
    i = pol.index(v) # posición del vértice en la lista
    n = len(pol)
    # Vértice convexo <--> v_i Gira a la izquierda <--> v_{i+1} a la izquierda de [v_{i-1},v_i] <--> orient(v_{i-1},v_i,v_{i+1}) = 1 ó 0
    if orient(pol[(i-1)%n], pol[i], pol[(i+1)%n]) == 1 or orient(pol[(i-1)%n], pol[i], pol[(i+1)%n]) == 0:
        return True
    else:
        return False
    
def es_diagonal_interna(i: int, pol: list[Punto]) -> bool:
    """
    Input: índice del vértice potencialmente convexo. Lista de vértices del polígono positivamente orientada.
    Se presupone que esta diagonal es [v_{i-1},v_{i+1}] para algún i. Por teoría sabemos que existe.
    Output: Sí / No es diagonal interna
    """
    """
    [v_{i-1},v_{i+1}] es diagonal interna cuando se cumplen ambas a) y b):
    a) v_i es un vértice convexo
    b) ningún otro v_k (k =/= i-1,i,i+1) está dentro del triángulo [v_{i-1}, v_i, v_{i+1}]
    ¡¡¡Mejor pasar i y no v_i!!!
    """
    n = len(pol)
    p = pol[(i-1)%n]
    v = pol[i]
    q = pol[(i+1)%n]
    triangulo = [p, v, q]

    if es_vertice_convexo(pol[i], pol):
        for j in range(n):
            if j!=(i-1)%n and j!=i and j!=(i+1)%n and punto_en_triangulo(pol[j], triangulo):
                return False # Viola la condición 
        return True # Cumple a) porque ha entrado en el if
                    # Cumple b) porque ha entrado y salido del bucle for sin que haya ningún vértice extra dentro del triángulo (no ha devuelto False)
    else:
        return False # Viola la condición a)
    
def encuentra_oreja(pol:list[Punto])->Punto:
    """
    Input: poligono
    Output: v_i tal que [v_{i-1},v_{i+1}] es diagonal interna
    """
    n = len(pol)
    for i in range(n):
        if es_diagonal_interna(i,pol):
            return pol[i] # Devuelve el primero que encuenta

def triangula_poligono(pol:list[Punto]):
    """Input: polígono simple (lista de puntos, el último punto de la lista conecta con el primero)
    Output: lista de diagonales (cada diagonal es un segmento, esto es, una lista de dos puntos)"""
    diagonales = []
    n = len(pol)
    if len(pol) == 3:
        return diagonales
    while n > 3:
        v_i = encuentra_oreja(pol)
        i   = pol.index(v_i)
        diagonales.append([pol[(i-1)%n],pol[(i+1)%n]])
        pol.remove(v_i)
        n = n-1
    return diagonales


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
    
    area = 0
    for i in range(n):
        area += prod_vect(points[i], points[(i + 1) % n])
    if area < 0: return points[::-1]
    else: return points
    
def comprueba_triangulacion(pol = None):
    if pol is None: pol = generate_random_polygon(10)
    
    diagonales = triangula_poligono(pol.copy())  
    
    #dibuja el polígono (vértices en verde, lados en azul) y las diagonales (en rojo)
    pol.append(pol[0])
    plt.plot([p.x for p in pol], [p.y for p in pol], 'bo-')
    for s in diagonales:
        plt.plot([p.x for p in s], [p.y for p in s], color = 'red')
    plt.show() 

pol = None
comprueba_triangulacion(pol)
