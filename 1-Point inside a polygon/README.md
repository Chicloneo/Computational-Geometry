# Point inside a polygon
Santiago Lillo Macías
2026-04-16

This second file consists in determining wether or not a point is inside a polygon. We import the `Punto` (point) class used on the previous folder, and the other basic functions.

To determine if a point is inside a polygon we use the following result: a point is inside a polygon when drawing an infinite line, call it r, to any direction on the plane, r intersects odd times with the polygon edges.

Computationally we can't draw an infinite line, of course, but we can draw a line big "enough". We will see this later on the code. 

A usual situation is the following:

![Is Q inside the polygon?](Image1.png)

# Segments intersection

Knowing when two segments intersect is fundamental for the code. But when do segments intersect?

Let A,B,C,D be four points on the plane. Let AB and CD be two segments. If
-A and B are on different sides of the segment CD
-C and D are on different sides of the segment AB
then AB and CD intersect. 

Then we can construct the function.
Input: s, t as a `Punto` list, vertices of s and t.
Output: True/False if s y t intersect (also True if they intersect on a vertex or they are the same segment)

```{python}
def segmentos_se_cortan(s: list[Punto], t: list[Punto]) -> bool:
    a,b = s[0],s[1]
    c,d = t[0],t[1]
    return (izquierda(a,b,c) != izquierda(a,b,d)) and (izquierda(c,d,a) != izquierda(c,d,b))
```

# Point and polygon

We are given a `Punto` list. In that order, the list is sorted as if we iterate through the polygon. `q` is the point to determine. The function returns `True` if `q` is inside `pol`. 

An interesting detail is how to construct the segment from `q` so that it is "big-enough". We take the max of all the x and y points coordinates, and we duplicate it (you can just add one, or whatever you want).

We evaluate the intersection function with the big segment and every other segment. If the number of intersections is odd, then it is inside.

```{python}
def punto_en_poligono(q: Punto, pol: list[Punto]) -> bool:
    coordenadas_x = [p.x for p in pol]
    coordenadas_y = [p.y for p in pol]
    punto_rayo = Punto(2*max(coordenadas_x), 2*max(coordenadas_y))
    segmento = [q,punto_rayo]
    contador_cortes = 0
    
    for i in range(len(pol)):
        # Definimos el lado del polígono
        lado = [pol[i], pol[(i + 1) % len(pol)]]
        
        if segmentos_se_cortan(segmento, lado):
            contador_cortes += 1

    if contador_cortes % 2 == 1:
        return True
    else:
        return False
```

# Examples

![NO example](Figure_2.png)

![YES example](Figure_3.png)
