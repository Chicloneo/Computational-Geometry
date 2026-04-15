# Multiprocessing example
Santiago Lillo Macías
2026-03-28

```{python}
import random
import math
import matplotlib.pyplot as plt
ERROR = 1e-9
```

# `Punto` class

We start by creating a class. A `Punto` object represents a point on the plane. We write the usual operations.

```{python}
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return "({0},{1})".format(self.x, self.y)  
    def __add__(self, other):
        return Punto(self.x + other.x, self.y + other.y)  
    def __sub__(self, other):
        return Punto(self.x - other.x, self.y - other.y)
```

# Three Basic Functions

## `alineados`

This function guesses if three points are aligned. We construct an auxiliary function, `det`, which calculates the determinant of two vectors. You can consider a vector by writing down two coordinates, so the class `Punto` is re-used. Floating-point error within the operations is considered.

```{python}
def det(P:Punto,Q:Punto) -> bool :
    return (P.x * Q.y) - (P.y * Q.x)

def alineados(a: Punto, b: Punto, c: Punto) -> bool:
    # Returns True if a,b,c are alligned
    vector1 = b-a
    vector2 = c-a
    return abs(det(vector1, vector2)) < ERROR 
```

## `ordena_angularmente`

This functions sorts a list of `Punto` objects by the angle they form with `Punto(0,0)`. First, we iterate through the list, and we identify each point with its arctangent. Now we have a list with `(Punto, atan)` elements. Then we sort it by the `atan`.

-Input: a list of `Punto` objects
-Output: the sorted list

```{python}
def ordena_angularmente(puntos: list[Punto]) -> list[Punto]:
    lista_atan = [(puntos[i],math.atan2(puntos[i].y, puntos[i].x)) for i in range(len(puntos))]
    lista_atan.sort(key=lambda tup: tup[1])
    return [punto[0] for punto in lista_atan] #Devuelve la lista de puntos ordenados
```

## `punto_en_triangulo`

This function guesses if a given point is inside of a given triangle. We construct an auxiliary function, `esta_izquierda`, which returns `True` if a given point is at the left side of a given segment (a list of two points).

-Input: a point and a triplet of points.
-Output: Yes/No

The key point is the last line:

```{text}
return esta_izquierda([P,Q],p) == esta_izquierda([Q,R],p) == esta_izquierda([R,P],p)
```

If the point is at the left side of every segment, then it's inside. In this case, every `esta_izquierda` evaluation is `True`. If the point is at the right side of every segment, then it's inside. In this case, every `esta_izquierda` evaluation is `False`. The only thing that changes here is the Triangle orientation (we say a polygon is positive-oriented if we iterate through its points anti-clockwise). Finally, if one of the `esta_izquierda` is `True` and one of them is `False` then the equation does not hold. In this case, the point is outside of the triangle.

`esta_izquierda` is `True` if the point is "inside" the segment, because the determinant will evaluate to zero. 

```{python}
def esta_izquierda(segmento, punto):
    return det(segmento[1]-segmento[0],punto-segmento[0])>=0

def punto_en_triangulo(p: Punto, triangulo: list[Punto]) -> bool: 
    P = triangulo[0]
    Q = triangulo[1]
    R = triangulo[2]
    
    return esta_izquierda([P,Q],p) == esta_izquierda([Q,R],p) == esta_izquierda([R,P],p)
```

# Verifying the code

We now check a few cases to see if our code ws written correctly (note: this is not a formal code verification). Few functions will help us. You can ignore the following code, and skip to the graphics.

```{python}
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
```

We give no input to the functions, hence points are randomly generated. But you can try it for whatever points you want.

```{python}
comprueba_alineados()
```

One `True` example, and one `False` example. Each with a different color.

![True](Figure_1.png)

![False](Figure_2.png)

```{python}
comprueba_ordena_angularmente()
```

![ ](Figure_3.png)

```{python}
comprueba_punto_en_triangulo()
```

![Outside](Figure_4.png)

![Inside](Figure_5.png)