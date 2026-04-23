# Delunay triangulation

Santiago Lillo Macías
2026-04-23

Remember a _point cloud_ is a set of points on the plane. Now, given a point cloud

![Point cloud](Images/Figure_1.png)

determine its triangulation. A point cloud can be triangulated in several ways.

![Point cloud](Images/Figure_2.png)

## Brute force search

There are diferent kinds of triangulation methods: Incremental, Graham, Divide and Conquer,... Here we present a brute-foce search algorithm, easier to understand. The complexity is $O(n^4)$, but we won't care about it for now. 

It is known that a unique circumference passes through 3 points (not alligned). If you hae the point cloud, you could arbitrarily choose 3 points. If you are lucky, no other point falls inside the circle. Then, the triangle defined by those three points is an OK _Delunay Triangle_. But if your are not so lucky, some points could fall inside the circle. This triangle is not a Delunay triangle.

![Delunay](Images/Figure_8.png)

## Algorithm

```{text}
for punto-a in lista_puntos:
    for punto-b in lista_puntos:
        for punto-c in lista_puntos: <-- until here we've selected three points that potentially form a triangle
            for punto-d in lista_puntos:
                check if punto-d is inside the punto-a-b-c circle <-- do this for every point on the plane
                if no point is inside
                    triangle a-b-c is good!
                else:
                    try another three points combination
return all good-triangles
```

## Code

Full code is at the end. First attempt:

-Input: `list[Punto]`

-Output: `list[triangles] = list[list[Punto]]`

__Remarks__

-Every triangle is a `Punto` triplet. We add each triangle to a list named `triangulos`.

-$j = i+1,...,n$ and $k=j+1,...,n$. By this way, every $(i,j,k)$ triplet is different. We can't do $l=k+1,...,n$ because we have to check _every_ point. Nevertheless, we still must check $l$ is different from $i,j$ or $k$ (this is a "concyclic" points issue). 

-`posible_triangulo` is a potential OK Delunay Triangle $(i,j,k)$.

-`triangulo_valido` is a boolean variable. If _some_ point is inside the $(i,j,k)$-circle, then `triangulo_valido = False`, and we don't add it to the final triangle list. Otherwise, is every point is outside the $(i,j,k)$-circle, then it is an OK Delunay Triangle. `triangulo_valido` remains `True`. Note that we only add a triangle only when the boolean variable is `True`.

```{python}
def triangulacion_delaunay_bruta(puntos):

    triangulos = []

    for i in range(len(puntos)):
        for j in range(i+1, len(puntos)):
            for k in range(j+1, len(puntos)):

                posible_triangulo = [puntos[i], puntos[j], puntos[k]]
                triangulo_valido = True #Si nunca se encuentra algún punto dentro, es válido
                for l in range(len(puntos)):
                    if l != i and l!= j and l!=k:
                        if dentro_circunf(puntos[i], puntos[j], puntos[k], puntos[l]) == 1: 
                            triangulo_valido = False
                            break

                if triangulo_valido: #el triángulo es válido si no tiene en el interior o si (no tiene en el interior + tiene conciclicos)
                    triangulo_correcto = posible_triangulo
                    triangulos.append(triangulo_correcto)
                        
    return triangulos
```

We've asked AI a function that determines if $d$ is inside the $a-b-c$ circle. Returns 1/0/-1 if it's inside/concyclic/outside the circle. You can use this as a black box. 

```{python}
def dentro_circunf(a, b, c, d):

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
```

## Test 1

Test functions are the following:

```{python}
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
```

```{text}
puntos = genera_nube_puntos(10, False)
comprueba_triangulacion_nube(puntos)
```
![Delunay](Images/Figure_6.png)

## Concyclic points

But what aout concyclic points? That is, four or more points that lay on the same circumference -as we said before, three points are always concyclic.

![Concyclic](Images/Figure_4.png)

If we don't modify our function, weird things appear.

![Concyclic](Images/Figure_5.png)

__Remarks__

-If a circle doesn't contain any points inside, and has concyclic points, we still consider it to be valid.

-We store the concyclic points apart. We will triangulate them independently.

-Points can be stored once. We store them as sets because ${a,b,c} = {a,c,b}$ but $[a,b,c] \neq [a,c,b]$.

- We use `triangulos.extend(triangulos_correctos)` and not `append` because `triangulos_correctos` is a list of lists, and we want to add each of the little lists.

-`else` covers the basic (previous) case.

Final function:

```{python}
def triangulacion_delaunay_bruta(puntos):

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
                            conciclicos.append(puntos[l]) # <---- store concyclic points

                if triangulo_valido:
                    if len(conciclicos) > 3: # <---- 3 points are always concyclic
                        if set(conciclicos) not in conciclicos_totales: # <---- only store them once
                            conciclicos_totales.append(set(conciclicos))
                            triangulos_correctos = triangula_conciclicos(conciclicos)
                            triangulos.extend(triangulos_correctos)
                    else:
                        triangulo_correcto = posible_triangulo
                        triangulos.append(triangulo_correcto)
    return triangulos
```

The following function triangulates the concyclic points. It fixes a point, and draws lines to each other point. 

```{python}
def ordena_angularmente_foco(puntos: list[Punto], foco:Punto) -> list[Punto]:
    def angulo(p: Punto) -> float:
        ang = math.atan2(p.y - foco.y, p.x - foco.x)
        return ang if ang >= 0 else ang + 2 * math.pi
    return sorted(puntos, key=angulo)

def triangula_conciclicos(puntos:list[Punto])->list[list[Punto]]:
    foco = puntos[0]
    lista_puntos = puntos[1:]
    ordenados = ordena_angularmente_foco(lista_puntos, foco)

    triangulos = []

    for i in range(len(ordenados) - 1):
        triangulos.append([foco, ordenados[i], ordenados[i+1]])

    return triangulos
```

## Test 2

We an now test our function with concyclic points.

```{text}
puntos = [Punto(11.924500897298753, 10.0), Punto(10.962250448649376, 11.666666666666666), Punto(9.037749551350624, 11.666666666666666),\
Punto(8.075499102701247, 10.0), Punto(9.037749551350624, 8.333333333333334), Punto(10.962250448649376, 8.333333333333334), Punto(14, 18), \
Punto(4, 6), Punto(18, 2), Punto(4, 12), Punto(14, 0), Punto(8, 4), Punto(5, 10), Punto(4, 8), Punto(20, 12), Punto(2, 11), Punto(4, 0), Punto(18, 0)]

comprueba_triangulacion_nube(puntos)
```

![Delunay](Images/Figure_7.png)
