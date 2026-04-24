"""LIBRERÍA DE GCOM

Este archivo contiene:
- las clases Punto, Arista, Cara y DCEL (línea 69)
- algunas de las funciones implementadas durante el curso (a partir de la línea 400 aprox.)
"""

import numpy as np
import random
import math
import matplotlib.pyplot as plt
ERROR = 1e-9

##################################### INICIO DCEL ######################################################
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    #La coordenada x del Punto p es p.x y la coordenada y del Punto p es p.y
    def __repr__(self):
        return "({0},{1})".format(self.x, self.y)  
    def __add__(self, other):
        return Punto(self.x + other.x, self.y + other.y)  
    def __sub__(self, other):
        return Punto(self.x - other.x, self.y - other.y)
    def __eq__(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) < ERROR
    def __hash__(self):
        return hash((round(self.x, 9), round(self.y, 9)))

class Arista:
    def __init__(self, origen, final, anterior = None, siguiente = None, gemela = None, cara = None):
        self.origen, self.final = origen, final
        self.anterior = anterior
        self.siguiente = siguiente
        self.gemela = gemela
        self.cara = cara           
    def __repr__(self):
        return "Arista de {0} a {1}".format(self.origen, self.final)
    def __eq__(self, other):
        return self.origen == other.origen and self.final == other.final
    def __hash__(self):
        return hash((self.origen, self.final))

class Cara:
    def __init__(self, arista_incidente = None):
        self.arista_incidente = arista_incidente

    def __repr__(self):
        return "Cara cuya arista es {0}".format(self.arista_incidente)                

    def lista_vertices(self):        
        e0 = self.arista_incidente
        vertices = [e0.origen]
        e = e0.siguiente
        while e != e0:
            vertices.append(e.origen)
            e = e.siguiente        
        return vertices

    def lista_lados(self):
        e0 = self.arista_incidente
        lados = [e0]
        e = e0.siguiente
        while e0 != e:
            lados.append(e)
            e = e.siguiente
        return lados

class DCEL:
    def __init__(self, vertices = None):
        # 1. Inicializamos las estructuras vacías
        self.lista_aristas = {}
        self.lista_caras = []   
        self.lista_vertices = {} # diccionario con los vértices como llaves y una arista incidente como valor 
        self.cara_exterior = None # puntero a la cara exterior, si la hubiera

        if vertices and len(vertices) >= 3:
            n = len(vertices)
            
            # 2. Creamos las dos caras iniciales
            cara_interior = Cara()
            cara_exterior = Cara()
            
            self.lista_caras.extend([cara_interior, cara_exterior])
            self.cara_exterior = cara_exterior
            
            # Listas temporales para ayudarnos a enlazar luego
            aristas_interiores = []
            aristas_exteriores = []
            
            # --- PRIMERA PASADA: Crear aristas, gemelas, y asignar orígenes/caras ---
            for i in range(n):
                origen, final = vertices[i], vertices[(i + 1) % n]
                
                # Creamos la arista interior (antihorario) y la exterior (horario)
                e_int = Arista(origen, final, cara=cara_interior)
                e_ext = Arista(final, origen, cara=cara_exterior)
                
                # Enlazamos las gemelas entre sí
                e_int.gemela = e_ext
                e_ext.gemela = e_int
                
                # Guardamos en nuestras listas temporales
                aristas_interiores.append(e_int)
                aristas_exteriores.append(e_ext)
                
                # Añadimos las aristas al diccionario global de la DCEL                
                self.lista_aristas[e_int], self.lista_aristas[e_ext] = e_int, e_ext
                
                # Registramos en el diccionario de vértices (usamos la arista interior)
                self.lista_vertices[origen] = e_int
                
            # Asignamos una arista incidente cualquiera a nuestras caras
            cara_interior.arista_incidente = aristas_interiores[0]
            cara_exterior.arista_incidente = aristas_exteriores[0]
            
            for i in range(n):
                # Para la cara interior: el recorrido es ANTIHORARIO (avanza hacia adelante en la lista)
                aristas_interiores[i].siguiente = aristas_interiores[(i + 1) % n]
                aristas_interiores[i].anterior = aristas_interiores[(i - 1) % n]
                
                # Para la cara exterior: el recorrido es HORARIO (avanza hacia atrás en la lista)
                # OJO aquí: la arista exterior 'i' va de V_{i+1} a V_{i}. 
                # Su 'siguiente' debe ser la que sale de V_{i}, que es la arista exterior 'i-1'.
                aristas_exteriores[i].siguiente = aristas_exteriores[(i - 1) % n]
                aristas_exteriores[i].anterior = aristas_exteriores[(i + 1) % n]
        
    def __repr__(self):               
        lineas = ["--- Información de la DCEL ---"]
        todas_las_aristas = list(self.lista_aristas.values())
        lineas.append(f"Total de aristas ({len(todas_las_aristas)}): {todas_las_aristas}")
        lineas.append(f"Lista de caras: {self.lista_caras}")
        lineas.append("Detalle por caras:")
        for c in self.lista_caras:
            lineas.append(f"  {c}")
            if c.arista_incidente:
                e0 = c.arista_incidente
                lineas.append(f"    - {e0}")
                e = e0.siguiente
                while e is not None and e != e0: 
                    lineas.append(f"    - {e}")
                    e = e.siguiente
        return "\n".join(lineas)
    
    
    def plot(self, grado = None):
        fig, ax = plt.subplots()
        for c in self.lista_caras:
            aristas = c.lista_lados()
            valores_x = [e.origen.x for e in aristas] + [aristas[0].origen.x]
            valores_y = [e.origen.y for e in aristas] + [aristas[0].origen.y]
            ax.fill(valores_x, valores_y, alpha=0.3)
            ax.plot(valores_x, valores_y)
        
        if grado is not None:
            for p in self.lista_vertices.keys():
                ax.text(p.x, p.y, f'{grado[p]}')

        ax.set_aspect('equal')
        plt.show()
        
    def busca_vertice(self, v_buscado):
        if v_buscado in self.lista_vertices: 
            return self.lista_vertices[v_buscado].origen
        else: return None
        
    def busca_arista(self, e_buscada):
        return self.lista_aristas.get(e_buscada) # devuelve None si e_buscada no está aún en la DCEL


    def añadir_triangulo_exterior(self, e_base, punto_nuevo):
        """
        Añade un nuevo triángulo a la frontera de la DCEL.
        e_base: La semi-arista actual que pertenece a la cara exterior (Origen A, Final B).
        punto_nuevo: La instancia del objeto Punto (P) que queremos añadir.
        """
        if e_base.cara is not self.cara_exterior:
            print("Error: e_base no pertenece a la cara exterior.")
            return
            
        # 1. Identificamos los vértices
        A = e_base.origen
        B = e_base.final # Asumiendo que definiste el método final() o usas e_base.gemela.origen
        P = punto_nuevo
        
        # 2. Registramos el nuevo vértice
        self.lista_vertices[P] = None # Se actualizará en un momento
        
        # 3. Creamos la nueva cara interior
        nueva_cara = Cara()
        self.lista_caras.append(nueva_cara)
        
        # 4. Creamos las 4 nuevas semi-aristas
        # Interiores del nuevo triángulo (B->P y P->A)
        e_BP = Arista(B, final=P, cara=nueva_cara)
        e_PA = Arista(P, final=A, cara=nueva_cara)
        
        # Exteriores (P->B y A->P)
        e_PB = Arista(P, final=B, cara=self.cara_exterior)
        e_AP = Arista(A, final=P, cara=self.cara_exterior)
        
        # Asignamos gemelas
        e_BP.gemela, e_PB.gemela = e_PB, e_BP
        e_PA.gemela, e_AP.gemela = e_AP, e_PA
        
        # Registramos las aristas en nuestro diccionario (asumiendo que hiciste el cambio)
        self.lista_aristas[e_BP] = e_BP
        self.lista_aristas[e_PB] = e_PB
        self.lista_aristas[e_PA] = e_PA
        self.lista_aristas[e_AP] = e_AP
        
        # 5. Modificamos la arista base antigua
        # Deja de ser exterior y pasa a ser la base del nuevo triángulo interior
        e_base.cara = nueva_cara 
        
        # 6. Conectamos el ciclo INTERIOR (El nuevo triángulo: e_base -> e_BP -> e_PA -> e_base)
        e_base.siguiente, e_BP.anterior = e_BP, e_base
        e_BP.siguiente, e_PA.anterior = e_PA, e_BP
        e_PA.siguiente, e_base.anterior = e_base, e_PA
        
        # Asignamos una arista cualquiera a la nueva cara y al nuevo vértice
        nueva_cara.arista_incidente = e_base
        self.lista_vertices[P] = e_PA
        
        # 7. Conectamos el ciclo EXTERIOR
        # Guardamos quiénes eran los vecinos de e_base en el bucle exterior original
        ext_anterior = e_base.anterior
        ext_siguiente = e_base.siguiente
        
        # Insertamos el nuevo camino exterior: ext_anterior -> e_AP -> e_PB -> ext_siguiente
        ext_anterior.siguiente, e_AP.anterior = e_AP, ext_anterior
        e_AP.siguiente, e_PB.anterior = e_PB, e_AP
        e_PB.siguiente, ext_siguiente.anterior = ext_siguiente, e_PB
        
        # Si la cara exterior apuntaba a e_base, actualizamos para que apunte a una válida
        if self.cara_exterior.arista_incidente == e_base:
            self.cara_exterior.arista_incidente = e_AP
            
        return nueva_cara

    
    def divide_triangulo(self, t, p):
        # Input: Punto p perteneciente a una Cara t de la DCEL
        # Objetivo: La función actualiza la DCEL eliminando t y creando los triángulos que forman p y los lados de t 
        # (y conectando todo bien). Funciona también si p está sobre un lado salvo si es un lado de la cara exterior

        # 1. Borramos la cara original
        if t in self.lista_caras:
            self.lista_caras.remove(t)
            
        lados = t.lista_lados()
        
        # 2. Búsqueda Pythonic del punto en un segmento
        k = -1
        for i, lado in enumerate(lados):
            # Asumo que punto_en_segmento está definida globalmente
            if punto_en_segmento(p, [lado.origen, lado.final]):
                k = i
                # Si p es exactamente un vértice, no hacemos nada
                if p == lado.origen or p == lado.final: 
                    return
                break # Encontramos el lado, salimos del bucle
                
        # 3. Caso en el que el punto cae sobre un lado (Edge Split)
        if k != -1:
            lado_k = lados[k]
            eg = lado_k.gemela
            
            # PROTECCIÓN: Si la gemela da al exterior, abortamos o derivamos a otra función
            if eg.cara is self.cara_exterior:
                print("El punto está en el límite exterior. Usar otra función.")
                return
                
            if eg is not None:
                # Actualizamos la lista de lados para formar el polígono envolvente
                lados = lados[k+1:] + lados[:k]
                e = eg.siguiente
                while e != eg:
                    lados.append(e)
                    e = e.siguiente
                    
                # Borramos la cara adyacente
                if eg.cara in self.lista_caras:
                    self.lista_caras.remove(eg.cara)
                    
                # Limpiamos el diccionario de aristas 
                self.lista_aristas.pop(lado_k, None)
                self.lista_aristas.pop(eg, None)
                
                # HIGIENE: Aseguramos que los vértices no apunten a aristas borradas
                self.lista_vertices[lado_k.origen] = eg.siguiente # Una arista segura del nuevo ciclo
                self.lista_vertices[eg.origen] = lado_k.siguiente # Otra arista segura

        # 4. Construcción de la geometría radial
        radiosin, radiosout = [], []
        for e in lados:
            e_in = Arista(e.final, p)
            e_out = Arista(p, e.origen)
            
            # Registramos en el diccionario de aristas
            self.lista_aristas[e_in] = e_in
            self.lista_aristas[e_out] = e_out
            
            cara_e = Cara(e)
            self.lista_caras.append(cara_e)
            
            e.cara = e_in.cara = e_out.cara = cara_e
            e.anterior, e.siguiente = e_out, e_in
            e_in.anterior, e_in.siguiente = e, e_out
            e_out.anterior, e_out.siguiente = e_in, e
            
            radiosin.append(e_in)
            radiosout.append(e_out)
            
        # 5. Asignación de gemelas
        for i in range(len(lados)):        
            radiosin[i].gemela = radiosout[(i + 1) % len(lados)]
            radiosout[(i + 1) % len(lados)].gemela = radiosin[i]
            
        # 6. Registramos el nuevo vértice central
        self.lista_vertices[p] = radiosout[0]                
        return
    
    def inspector_integridad(self) -> bool:
        """
        Verifica que todos los invariantes topológicos de la DCEL se cumplan.
        Imprime un informe detallado de los errores encontrados.
        """
        print("--- Iniciando Inspección de Integridad de la DCEL ---")
        errores = 0

        # 1. Comprobación de Vértices
        for v, e in self.lista_vertices.items():
            if e is None:
                print(f"Error Vértice: El vértice {v} no tiene arista incidente asignada.")
                errores += 1
            elif e.origen != v:
                print(f"Error Vértice: La arista incidente del vértice {v} nace en otro vértice ({e.origen}).")
                errores += 1

        # 2. Comprobación de Semi-Aristas
        for e in self.lista_aristas.values():
            # A. Punteros básicos del ciclo
            if e.siguiente is None or e.anterior is None:
                print(f"Error Arista {e}: Falta el puntero .siguiente o .anterior.")
                errores += 1
                continue # Saltamos para evitar errores en cascada

            if e.siguiente.anterior != e:
                print(f"Error Arista {e}: e.siguiente.anterior no vuelve a e.")
                errores += 1
            if e.anterior.siguiente != e:
                print(f"Error Arista {e}: e.anterior.siguiente no vuelve a e.")
                errores += 1
            
            # B. Coherencia de Caras
            if e.cara != e.siguiente.cara:
                print(f"Error Arista {e}: e y e.siguiente apuntan a caras diferentes.")
                errores += 1

            # C. Coherencia de Gemelas
            if e.gemela is None:
                print(f"Error Arista {e}: No tiene gemela. Toda arista debe tenerla (incluidas las de la frontera exterior).")
                errores += 1
            else:
                if e.gemela.gemela != e:
                    print(f"Error Arista {e}: e.gemela.gemela no vuelve a e.")
                    errores += 1
                if e.origen == e.gemela.origen:
                    print(f"Error Arista {e}: e y su gemela nacen del mismo vértice. ¡Deben ser opuestas!")
                    errores += 1

        # 3. Comprobación de Caras
        for c in self.lista_caras:
            if c.arista_incidente is None:
                print(f"Error Cara {c}: No tiene arista incidente asignada.")
                errores += 1
            elif c.arista_incidente.cara != c:
                print(f"Error Cara {c}: Su arista incidente apunta a una cara distinta.")
                errores += 1

        # 4. Fórmula de Euler para grafos planares conexos
        # Si la topología es correcta, debe cumplirse invariablemente
        V = len(self.lista_vertices)
        E = len(self.lista_aristas) // 2  # Aristas reales (pares de semi-aristas)
        F = len(self.lista_caras)
        
        if V - E + F != 2:
            print(f"Error Topológico Global: No se cumple la Fórmula de Euler ($V - E + F = 2$).")
            print(f"Valores actuales: V={V}, E={E}, F={F} -> Resultado: {V - E + F}")
            errores += 1

        # Resumen final
        if errores == 0:
            print("Resultado: Correcto. La DCEL es válida y consistente.\n")
            return True
        else:
            print(f"Resultado: Inspección FALLIDA. Se encontraron {errores} errores.\n")
            return False
    
    
##################################### FIN DCEL ######################################################

##################################### INICIO "LIBRERIA" GCOM ###########################################
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


def envolvente_convexa(puntos: list[Punto]) -> list[Punto]:
    """Cálculo de la envolvente convexa usando el algoritmo de Graham, generado por IA y retocado para casos extremos"""
    n = len(puntos)
    if n < 3: return puntos

    # 1. Encontrar el punto con la 'y' más baja (y la 'x' más baja en caso de empate)
    # Este será nuestro punto de pivote.
    pivote = min(puntos, key=lambda p: (p.y, p.x))

    # 2. Ordenar los puntos según el ángulo polar respecto al pivote
    # Usamos atan2 para calcular el ángulo de forma sencilla.
    def calcular_angulo(p):
        return math.atan2(p.y - pivote.y, p.x - pivote.x), (p.x-pivote.x)**2 + (p.y - pivote.y)**2
    
    # Quitamos el pivote de la lista para ordenar el resto
    puntos_restantes = [p for p in puntos if p != pivote]
    puntos_ordenados = sorted(puntos_restantes, key=calcular_angulo)

    lastangle = calcular_angulo(puntos_ordenados[-1])
    i = len(puntos_restantes) - 1
    while i >= 0 and abs(calcular_angulo(puntos_ordenados[i])[0] - lastangle[0]) < ERROR: i = i-1
    puntos_ordenados = puntos_ordenados[:i+1] + puntos_ordenados[i+1:][::-1]
    
    # 3. Construir la envolvente usando una pila (stack)
    envolvente = [pivote, puntos_ordenados[0]]

    for i in range(1, len(puntos_ordenados)):
        punto_actual = puntos_ordenados[i]
        
        # Mientras el giro no sea hacia la izquierda (CCW), eliminamos el último punto
        # orient(a, b, c) == 1 significa giro a la izquierda.
        while len(envolvente) > 1 and orient(envolvente[-2], envolvente[-1], punto_actual) == -1:
            envolvente.pop()
            
        envolvente.append(punto_actual)

    return envolvente

def dentro_circunf(a, b, c, d):
    """Input: cuatro puntos a, b, c, d (objetos con atributos .x e .y)
    Output: 1/0/-1 dependiendo de si d está dentro/sobre/fuera de la circunferencia circunscrita de a, b, c"""
    
    # 1. Trasladar d al origen para simplificar el cálculo y estabilizar los decimales
    ax, ay = a.x - d.x, a.y - d.y
    bx, by = b.x - d.x, b.y - d.y
    cx, cy = c.x - d.x, c.y - d.y
    
    # 2. Calcular la componente Z proyectando los puntos en un paraboloide 3D
    az = ax**2 + ay**2
    bz = bx**2 + by**2
    cz = cx**2 + cy**2
    
    # 3. Calcular el determinante de la matriz 3x3
    det = (ax * (by * cz - bz * cy) -
           ay * (bx * cz - bz * cx) +
           az * (bx * cy - by * cx))
           
    # 4. Calcular la orientación de los puntos a, b, c (producto cruzado 2D)
    # Esto es vital por si los puntos te llegan en orden horario en lugar de antihorario
    orientacion = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    
    # Si están en orden horario, invertimos el signo del determinante
    if orientacion < 0:
        det = -det
                    
    # 5. Evaluar el resultado
    if det > ERROR:
        return 1  # Dentro
    elif det < -ERROR:
        return -1 # Fuera
    else:
        return 0  # Sobre la circunferencia


##################################### FIN "LIBRERIA" GCOM ###########################################

