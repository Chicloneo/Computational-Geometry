import random
import math
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
    

def det(P:Punto,Q:Punto) -> bool :
    """
    Calcula el determinante de dos vectores 
    Podemos pensarlos como puntos con coordenadas (x,y)
    """
    return (P.x * Q.y) - (P.y * Q.x)


def alineados(a: Punto, b: Punto, c: Punto) -> bool:
    # Devuelve True/False si los puntos a, b, c están alineados/no lo están
    vector1 = b-a
    vector2 = c-a
    #Podríamos devolver det(vector1, vector2) == 0 ya que comprueba_alineados() solo trabaja con enteros
    return abs(det(vector1, vector2)) < ERROR 

def ordena_angularmente(puntos: list[Punto]) -> list[Punto]:
    # Input: puntos es una lista de Punto
    # Output: lista de puntos ordenada angularmente (según el ángulo desde el origen)
    # Sugerencia: usar una función de comparación auxiliar como la esbozada
    lista_atan = [(puntos[i],math.atan2(puntos[i].y, puntos[i].x)) for i in range(len(puntos))]
    #lista_atan es una lista de tuplas con (punto, atan(punto))
    lista_atan.sort(key=lambda tup: tup[1])
    #Ahora se ha ordenado según la arcotangente (omitiendo el punto)
    return [punto[0] for punto in lista_atan] #Devuelve la lista de puntos ordenados

def punto_en_triangulo(p: Punto, triangulo: list[Punto]) -> bool:
    # Input: p Punto y triangulo lista con 3 Puntos, los vértices del triángulo
    # Output: True/False si el punto p está en el interior del triángulo o no    
    P = triangulo[0]
    Q = triangulo[1]
    R = triangulo[2]
    #return det(Q-P, p-P)>=0 and det(R-Q, p-Q)>=0 and det(P-R, p-R)>=0
    # En la condición de abajo estoy diciendo que los segmentos dejan a p en el mismo lado 
    #ya que el triángulo pueden no dártelo ordenado
    return esta_izquierda([P,Q],p) == esta_izquierda([Q,R],p) == esta_izquierda([R,P],p)

def esta_izquierda(segmento, punto):
    return det(segmento[1]-segmento[0],punto-segmento[0])>=0

P=Punto(0,0)
Q=Punto(3,0)
R=Punto(1,1) #sí está a la izquierda
S=Punto(1,-1) #no está a la izquierda
print('a',esta_izquierda([P,Q],R))
print('b',esta_izquierda([P,Q],S))

def comprueba_alineados(puntos = None):
    if puntos is None:
        puntos = [Punto(random.randint(0,3), random.randint(0,3)) for _ in range(3)]
    color = 'go' if alineados(puntos[0], puntos[1], puntos[2]) else 'ro'
    plt.plot([p.x for p in puntos], [p.y for p in puntos], color)
    plt.show()
    return True

def comprueba_ordena_angularmente(puntos = None):
    if puntos is None:
        puntos = [Punto(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(10)]
    puntos = ordena_angularmente(puntos)
    for i in range(len(puntos)):
        plt.plot([0, puntos[i].x], [0, puntos[i].y], 'blue')
        plt.text(puntos[i].x, puntos[i].y, str(i))
    plt.show()

def comprueba_punto_en_triangulo (p = None, triangulo = None, respuesta_esperada = None):
    if p is None:
        p = Punto(random.uniform(-1,1), random.uniform(-1, 1))
    if triangulo is None:
        triangulo = [Punto(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(3)]  
    if respuesta_esperada is not None:
        while punto_en_triangulo(p, triangulo) != respuesta_esperada:
            p = Punto(random.uniform(-1,1), random.uniform(-1, 1))
    
    respuesta = punto_en_triangulo(p, triangulo)
    
    triangulo = triangulo[:] + triangulo[:1]
    plt.plot([v.x for v in triangulo], [v.y for v in triangulo], 'blue')
    plt.plot(p.x, p.y, 'ro')
    s = 'Dentro' if respuesta else 'Fuera'
    plt.text(p.x, p.y, s)
    plt.show()

#comprueba_alineados([Punto(1,1), Punto(2,2), Punto(3,3)])
#comprueba_alineados() #prueba con 3 puntos de coordenadas enteras pequeñas al azar
#comprueba_ordena_angularmente()
#comprueba_punto_en_triangulo()
