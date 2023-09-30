#Autor: Ivan Olmos Pineda
#Curso: Multiagentes - Graficas Computacionales

import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import pygame
from pygame.locals import *

import random
import math

from objloader import *

class Cubo:
    valid = 0
    subiendo = 0
    bajando = 1
    model = None

    def __init__(self, dim, velocidad):
        
        ###########OP
        #Estados
        self.objetivo = None 
        self.recolectando = False #No se uso
        self.carrying_basura = None
        
        self.angulo = 0
        self.direction = (0, 0, 1)  #Dirección inicial
        self.objetivo_direction = (0, 0, 1)  
        self.valid = 0

        
        #Se inicializan las coordenadas de los vertices del cubo
        self.vertexCoords = [  
                   1,1,1,   1,1,-1,   1,-1,-1,   1,-1,1,
                  -1,1,1,  -1,1,-1,  -1,-1,-1,  -1,-1,1  ]
        #Se inicializan los colores de los vertices del cubo
        self.vertexColors = [ 
                   1,1,1,   1,0,0,   1,1,0,   0,1,0,
                   0,0,1,   1,0,1,   0,0,0,   0,1,1  ]
        #Se inicializa el arreglo para la indexación de los vertices
        self.elementArray = [ 
                  0,1,2,3, 0,3,7,4, 0,4,5,1,
                  6,2,1,5, 6,5,4,7, 6,7,3,2  ]
        
        self.DimBoard = dim
        
        #Se inicializa una posición aleatoria en el tablero
        self.Position = [0,0,0]
        
        self.alturaplataforma = 0.5
        self.contador = 0
        self.condition = self.bajando

        #Inicializar las coordenadas (x, y, z) del cubo en el tablero almacenándolas en el vector Position
        self.Position[0] = 0
        self.Position[1] = 5
        self.Position[2] = 0

        
        #Se inicializa un vector de dirección aleatorio
        self.Direction = [0,0,0]
        
        #El vector aleatorio debe estar sobre el plano XZ (la altura en Y debe ser fija)
        #Se normaliza el vector de dirección
        self.Direction[0] = random.randrange(-200, 200)
        self.Direction[1] = 0
        self.Direction[2] = random.randrange(-200, 200)

        #Se normaliza el vector de dirección
        m = math.sqrt((self.Direction[0] * self.Direction[0]) + (self.Direction[2] * self.Direction[2])) 
        self.Direction[0] = self.Direction[0] / m
        self.Direction[2] = self.Direction[2] / m
        
        #Se cambia la magnitud del vector dirección con la variable vel
        self.velocidad = velocidad
        
    def generate(self, size, facing):
        #global obj
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glScaled(size,size,size)
        glRotate(90,0,0,1)
        glRotate(90,0,1,0)
        glRotate(facing,0,0,1)
        #self.rotar()
        self.obj.render()
        glPopMatrix()

    def loadmodel(self, model):
        self.obj = OBJ(model, swapyz=True)
        self.obj.generate()

    def update(self, new_x, new_z):
        self.Position[0] = new_x
        self.Position[2] = new_z

    def updatevalid(self,value):
        self.valid = value
