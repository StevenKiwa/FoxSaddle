"""Registro de secciones: el orden de este diccionario es el del menú de la barra lateral."""
from secciones.curvas_nivel import curvas_nivel
from secciones.demostracion_formal import demostracion_formal
from secciones.derivadas import derivadas
from secciones.grafica_2d_3d import grafica_2d_3d
from secciones.inicio import inicio
from secciones.polares import polares
from secciones.superficies_nivel import superficies_nivel
from secciones.trayectorias import trayectorias
from secciones.tutor_ia import tutor_ia

SECCIONES = {
    "Inicio": inicio,
    "Gráfica 2D y 3D": grafica_2d_3d,
    "Curvas de nivel": curvas_nivel,
    "Superficies de nivel": superficies_nivel,
    "Límite por trayectorias": trayectorias,
    "Límite en coordenadas polares": polares,
    "Demostración ε-δ": demostracion_formal,
    "Derivadas parciales": derivadas,
    "Tutor IA": tutor_ia,
}
