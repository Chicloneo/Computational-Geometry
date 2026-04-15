"""PRACTICA 1: 28-01-2026
Instrucciones:
- Modifica el nombre de archivo para que comience por tus apellidos (ej. HernandezCorbato_p1.py)
- Trabaja en las funciones "segmentos_se_cortan" (línea 44), "punto_en_poligono" (línea 49)
- Para comprobar su funcionamiento ve al final del código y ejecuta la comprobación correspondiente
- Sube el código .py a la tarea del CV al final de la clase
Actualizada 03/02/26
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

def izquierda(a:Punto,b:Punto,c:Punto) -> bool:
    #Devuelve True si c está a la izquierda del segmento [a,b]. False e.c.c.
    if det(a,b,c) >= 0:
        return True
    else:
        return False

def segmentos_se_cortan(s: list[Punto], t: list[Punto]) -> bool:
    # Input: s, t son listas con dos puntos, los extremos de los segmentos s y t.
    # Output: True/False decidiendo si s y t se cortan (incluyendo solaparse o cortarse en un extremo)
    a,b = s[0],s[1]
    c,d = t[0],t[1]
    #Devuelve True si c y d están a distintos lados de [a,b] y a y b están a distintos lados de [c,d]
    return (izquierda(a,b,c) != izquierda(a,b,d)) and (izquierda(c,d,a) != izquierda(c,d,b))

def punto_en_poligono(q: Punto, pol: list[Punto]) -> bool:
    # Input: q es un punto, pol es una lista de puntos que, en ese orden, son los vértices de un polígono (simple)
    # Output: True/False decidiendo si q está dentro de pol (incluyendo la frontera)
    coordenadas_x = [p.x for p in pol]
    coordenadas_y = [p.y for p in pol]
    punto_rayo = Punto(2*max(coordenadas_x), 2*max(coordenadas_y))
    segmento = [q,punto_rayo]
    contador_cortes = 0
    
    for i in range(len(pol)):
        # Definimos el lado del polígono
        lado = [pol[i], pol[(i + 1) % len(pol)]]
        #añado % len(pol) para el segmento [An,A0]
        
        if segmentos_se_cortan(segmento, lado):
            contador_cortes += 1
            
    # Si el número de cortes es impar, está dentro
    if contador_cortes % 2 == 1:
        return True
    else:
        return False



def comprueba_segmentos_se_cortan(s = None, t = None, size = 2, entero = False):
    def punto_aleatorio():
        if entero:
            return Punto(random.randint(0, size), random.randint(0, size))
        else:
            return Punto(random.uniform(0, size), random.uniform(0, size))
    if s is None:
        s = [punto_aleatorio(), punto_aleatorio()]
    if t is None:
        t = [punto_aleatorio(), punto_aleatorio()]
    respuesta = segmentos_se_cortan(s, t)
    plt.plot([p.x for p in s], [p.y for p in s], 'blue')
    plt.plot([p.x for p in t], [p.y for p in t], 'red')
    texto = 'Sí se cortan' if respuesta else 'NO se cortan'
    texto = 'Los segmentos ' + texto
    plt.title(texto)
    plt.show()
    return

def comprueba_punto_en_poligono(q = None, pol = None, n_vertices = 12):
    def intersects(p1, p2, p3, p4):
        """Check if line segment (p1,p2) intersects with (p3,p4)."""
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        
        # Standard line intersection formula
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    def generate_random_polygon(n):
        # 1. Create random points
        points = np.random.rand(n, 2)
        
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
                    
                    if intersects(p1, p2, p3, p4):
                        # 3. Swap the order of points between i+1 and j to uncross
                        points[i+1:j+1] = points[i+1:j+1][::-1]
                        swapped = True
        return points

    # --- Plotting ---
    if pol is None:
        poly_points = generate_random_polygon(n_vertices)
    else:
        poly_points = np.array([[p.x, p.y] for p in pol])
    # Close the polygon for plotting
    plot_data = np.vstack([poly_points, poly_points[0]])

    plt.figure(figsize=(6,6))
    plt.plot(plot_data[:,0], plot_data[:,1], 'ro-')
    plt.fill(plot_data[:,0], plot_data[:,1], alpha=0.2, color='blue')
    
    if q is None: q = Punto(random.uniform(0,1), random.uniform(0,1))
    plt.plot(q.x, q.y, 'bo')
    pol = [Punto(*row) for row in poly_points]
    respuesta = punto_en_poligono(q, pol)
    texto = 'dentro' if respuesta else 'fuera'
    texto = 'El punto está ' + texto
    plt.title(texto)
    plt.show()


comprueba_segmentos_se_cortan()
# Segmentos que se cortan:
# comprueba_segmentos_se_cortan([Punto(0,1), Punto(2,1)], [Punto(1,0), Punto(1,2)])
# Segmentos que se cortan:
# comprueba_segmentos_se_cortan([Punto(0,1), Punto(2,1)], [Punto(0,1), Punto(1,2)])

#comprueba_punto_en_poligono()

# Polígono = cuadrado y punto definido
# pol = [Punto(0,0), Punto(1,0), Punto(1,1), Punto(0,1)]
# q = Punto(0.5, 0.5)
# comprueba_punto_en_poligono(q, pol)

#Errores que había cometido: 
#   -Iterar p=Punto(a,b) como p[0] cuando en realidad es p.x
#   -Cuidado con el bucle for, el rango y el último segmento del polígono que conecta el punto An con A1.
