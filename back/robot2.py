from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import Slider
from mesa.space import MultiGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Checkbox
from random import randrange
from random import random
from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule

import pathfinding
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class Bot(Agent):
    sweeping = 0
    idle = 1
    patrolling = 2

    tocenter = 3
    returning = 5
    depositing = 6

    found = 0
    searching = 1
    busy = 2

    free = 0
    loaded = 1

    totrash = 0
    topos = 1
    def __init__(self, model, pos, level, behaviour, tamano, incinerador, matrix):
        super().__init__(model.next_id(), model)
        #
        self.schedule = RandomActivation(model)  #######
        self.matrix = model.grid_to_matrix() ###Aqui

        #self.grid = MultiGrid(21, 21, torus=False)  ######

        # self.grid = grid
        # self.grid = None
        self.grid = model.grid
        ...
        self.path = None
        self.setup_grid(tamano)

        #
        self.pos = pos
        self.path = []
        #
        self.todestination = None
        self.trash = None
        self.destino = None
        self.condition = self.free
        self.behaviour = behaviour
        self.initialpos = None
        self.search = self.searching
        self.level = level
        self.tamano = tamano
        self.center = (tamano // 2, tamano // 2)
        self.incinerador = incinerador
        self.loop = (1, 0, 0, 0)
        self.loopcounter = 0
        self.centercells = self.model.grid.get_neighborhood(self.incinerador.pos, moore=True, radius=1)
        
        #self.matrix = None

    def set_matrix(self, matrix):
        self.matrix = matrix

        #######
        ########

    def pathfinding_check(self):
        #Si pathfnding esta vacio
        if not self.path:
            return False





    def setup_grid(self, tamano):
        self.grid = Grid(matrix=[[0] * tamano for _ in range(tamano)])

    # def update_grid(self):
    ###




    #############
    #########
    def set_matrix(self, matrix):
        self.matrix = matrix


    ########
    #####

    def movetopos(self, x, y):
        current_pos = self.pos
        if current_pos == (x, y):
            return
        if self.pos[0] > x:
            if self.pos[1] > y:
                nextpos = (current_pos[0] - 1, current_pos[1] - 1)
            elif self.pos[1] == y:
                nextpos = (current_pos[0] - 1, current_pos[1])
            elif self.pos[1] < y:
                nextpos = (current_pos[0] - 1, current_pos[1] + 1)
        elif self.pos[0] < x:
            if self.pos[1] < y:
                nextpos = (current_pos[0] + 1, current_pos[1] + 1)
            elif self.pos[1] == y:
                nextpos = (current_pos[0] + 1, current_pos[1])
            elif self.pos[1] > y:
                nextpos = (current_pos[0] + 1, current_pos[1] - 1)
        elif self.pos[0] == x:
            if self.pos[1] < y:
                nextpos = (current_pos[0], current_pos[1] + 1)
            elif self.pos[1] > y:
                nextpos = (current_pos[0], current_pos[1] - 1)
        # if self.checkavailability(nextpos):
        self.model.grid.move_agent(self, nextpos)

    def pickup(self):
        trash = list(filter(lambda a: isinstance(a, Trash), self.model.grid.get_cell_list_contents(self.pos)))
        if trash:
            for t in trash:
                if t.condition == Trash.STATIC:
                    if t.assigned == False:
                        self.trash = t
                        self.trash.assigned = True
                        self.condition = self.loaded
                        self.destino = self.pos
                    return True
        return False

    def sweep(self):
        
        for i in range(2):
            #print("iteration" + str(i))
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, radius=i+1)
            for j in range(len(neighbors)):
                trash = list(filter(lambda a: type(a) == Trash, self.model.grid.get_cell_list_contents(neighbors[j])))
                if len(trash) > 0:
                    self.search = self.found
                    k = randrange(0, len(trash))
                    #print("Trash found at:" + str(trash[i].pos))
                    #print("found at: " + str(i))
                    return trash[k].pos

    def posicion_basura(self, x, y):
        contenido = self.grid.get_cell_list_contents((x, y))
        return any(isinstance(agent, Trash) for agent in contenido)


    def print_grid(self):
        ancho, alto = self.grid.width, self.grid.height

        for y in reversed(range(alto)):
            row = ""
            for x in range(ancho):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                if any(isinstance(agent, Trash) for agent in cell_contents):
                    row += "[1]"
                elif any(isinstance(agent, Bot) for agent in cell_contents):
                    row += "[B]"
                else:
                    row += "[0]"
            #print(row)

    def set_path(self, path):
        self.path = path


    def moves(self):
        if self.path:
            next_step = self.path[0]
            #Si hay basura
            cell_contents = self.model.grid.get_cell_list_contents([next_step])
            if not any(isinstance(agent, Trash) for agent in cell_contents):
                self.path.pop(0)  #Remove
                self.model.grid.move_agent(self, next_step)

    def move_using_pathfinding(self, destination,matrix):
        #print(destination)
        grid = Grid(matrix=matrix)
        (x, y) = self.pos
        start = grid.node(x, y)
        (end_x, end_y) = destination
        end = grid.node(end_x, end_y)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, _ = finder.find_path(start, end, grid)
        #print(path)
        if len(path) > 1:
            next_pos = path[1]
            self.model.grid.move_agent(self, next_pos)

    def step(self):

        #self.matrix = self.mesa_A_matrix(self.model.grid, self.model.grid.width, self.model.grid.height)
        self.matrix = self.model.grid_to_matrix()
        #matrix = self.model.matrix  #Access the matrix from the model (Floor)
        #print(self.matrix)
        if isinstance(self.trash, Trash):
            self.trash = self.trash
        else:
            self.trash = None


        if self.trash == None:
            if self.behaviour == self.sweeping:
                if self.destino != None:
                    if self.pos != (self.destino[0], self.destino[1]):
                        #print(self.destino)
                        #self.matrix[self.destino[0]][self.destino[1]] = 0
                        #print(self.matrix[self.destino[0]][self.destino[1]])
                        #self.move_using_pathfinding(self.destino, self.matrix)
                        if self.search == self.busy:
                            self.move_using_pathfinding(self.destino, self.matrix)
                        else:
                            self.movetopos(self.destino[0], self.destino[1])

                    elif self.pos == (self.destino[0], self.destino[1]):
                        self.destino = self.initialpos
                        self.search = self.busy
                        if not self.pickup():
                            # print("searching")
                            self.search = self.searching
                elif self.search == self.searching:
                    if self.sweep():
                        self.destino = self.sweep()
                        self.todestination = self.totrash
                    else:
                        if self.pos[0] == self.tamano - 1 or self.pos[1] == self.tamano - 1:
                            self.behaviour = self.patrolling
                        if self.pos[0] < self.tamano - 1:
                            if self.pos[1] < self.tamano - 1:
                                #self.move_using_pathfinding((self.pos[0] + 1, self.pos[1] + 1), self.matrix)
                                self.movetopos(self.pos[0] + 1, self.pos[1] + 1)
                            else:
                                #self.move_using_pathfinding((self.pos[0] + 1, self.pos[1]), self.matrix)
                                self.movetopos(self.pos[0] + 1, self.pos[1])
                        elif self.pos[1] < self.tamano - 1:
                            if self.pos[0] < self.tamano - 1:
                                #self.move_using_pathfinding((self.pos[0] + 1, self.pos[1] + 1), self.matrix)
                                self.movetopos(self.pos[0] + 1, self.pos[1] + 1)
                            else:
                                #self.move_using_pathfinding((self.pos[0], self.pos[1] + 1), self.matrix)
                                self.movetopos(self.pos[0], self.pos[1] + 1)

            elif self.behaviour == self.patrolling:
                if self.destino != None:
                    if self.pos != (self.destino[0], self.destino[1]):
                        #self.move_using_pathfinding((self.destino[0], self.destino[1]), self.matrix)
                        #self.movetopos(self.destino[0], self.destino[1])
                        if self.search == self.busy:
                            self.move_using_pathfinding(self.destino, self.matrix)
                        else:
                            self.movetopos(self.destino[0], self.destino[1])
                    elif self.pos == (self.destino[0], self.destino[1]):
                        self.destino = self.initialpos
                        self.search = self.busy
                        if not self.pickup():
                            # print("searching")
                            self.search = self.searching
                elif self.search == self.searching:
                    if self.sweep():
                        self.destino = self.sweep()
                        self.todestination = self.totrash
                if self.destino == None:
                    if randrange(0,100) < 5:
                        self.loopcounter+=1
                    if self.loop == (1, 0, 0, 0):
                        if self.pos[0] == (self.tamano - self.tamano + self.loopcounter):
                            self.loopcounter += 1
                            #print(self.loopcounter)
                            self.loop = (0, 0, 1, 0)
                            return
                        #self.move_using_pathfinding(((self.tamano - self.tamano + self.loopcounter), self.pos[1]), self.matrix)
                        self.movetopos((self.tamano - self.tamano + self.loopcounter), self.pos[1])
                    elif self.loop == (1, 1, 0, 0):
                        if self.pos[0] == (self.tamano - 1 - self.loopcounter):
                            self.loop = (0, 0, 1, 1)
                            return
                        #self.move_using_pathfinding(((self.tamano - 1 - self.loopcounter), self.pos[1]), self.matrix)
                        self.movetopos((self.tamano - 1 - self.loopcounter), self.pos[1])
                    elif self.loop == (0, 0, 1, 0):
                        if self.pos[1] == (self.tamano - self.tamano + self.loopcounter):
                            self.loop = (1, 1, 0, 0)
                            return
                        #self.move_using_pathfinding((self.pos[0], (self.tamano - self.tamano + self.loopcounter)), self.matrix)
                        self.movetopos(self.pos[0], (self.tamano - self.tamano + self.loopcounter))
                    elif self.loop == (0, 0, 1, 1):
                        if self.pos[1] == (self.tamano - 1 - self.loopcounter):
                            self.loop = (1, 0, 0, 0)
                            return
                        #self.move_using_pathfinding((self.pos[0], (self.tamano - 1 - self.loopcounter)), self.matrix)
                        self.movetopos(self.pos[0], (self.tamano - 1 - self.loopcounter))

                    if self.loopcounter > 60: self.behaviour = self.idle
                #print("patrolling")
        else:
            if self.pos == self.center:
                self.trash.state = 1
                self.trash = None
                self.condition = self.free
                #self.destino = self.sweep()
            elif self.pos in self.centercells:
                #print("incinerador:" + str(self.incinerador.condition))
                if self.incinerador.condition == self.incinerador.free:
                    if self.incinerador.choosebot():
                        #Elimina basura pero se bugea
                        self.trash.state = 1
                        print(str(self.trash.state))
                        self.move_using_pathfinding(self.center,self.matrix)
                        #self.movetopos(self.center[0], self.center[1])
                        if self.trash != None:
                            self.trash.move(self.pos[0], self.pos[1])
                            self.trash.state = 1 
                        return
                return
            else:
                #print(self.center)
                if self.trash.pos in self.centercells:
                    self.trash.state = 1 
                self.move_using_pathfinding(self.center,self.matrix)
                if self.trash != None:
                    self.trash.move(self.pos[0], self.pos[1])






class Incinerador(Agent):
    free = 0
    visit = 1
    burning = 2

    def __init__(self, model, pos, world):
        super().__init__(model.next_id(), model)
        self.world = world
        self.pos = pos
        self.condition = self.free
        self.trash = None

    def burn(self):
        self.condition = self.visit

    def checktrash(self):
        trash = list(filter(lambda a: type(a) == Trash, self.model.grid.get_cell_list_contents(self.pos)))
        if len(trash) == 1:
            self.trash = trash[0]
            self.trash.state = 1
            #print("adgfdghfgfdsfdfsdgfffffffffffffffffffffffffffffffffffffssssssssssss")
            return True
        return False

    def choosebot(self):
        if self.condition == self.free:
            self.condition = self.visit
            return True

    def step(self):
        if self.checktrash():
            if isinstance(self.trash, Trash):
                self.trash.state = 1
                self.world.deleteagent(self.trash)
                self.condition = self.visit
            #print("burned trash")
        else:
            if self.condition == self.visit:  # blue
                self.condition = self.burning  # morado
            elif self.condition == self.burning:
                self.condition = self.free  # yelow


class Trash(Agent):
    STATIC = 0
    MOVING = 1
    
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.assigned = False
        self.condition = self.STATIC
        self.pos = pos
        self.bot = None
        self.state = 0
    def move(self, x, y):
        self.condition = self.MOVING
        self.model.grid.move_agent(self, (x, y))


basura_total = 0


class Floor(Model):
    def __init__(self, density=0.25, num_robots=1, size=False, tamaño=51, time=1000):
        if size == True:
            tamaño = 51
        else:
            tamaño = 21
        super().__init__()
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(tamaño, tamaño, torus=False)
        self.time = time
        self.total_trash_placed = 0
        self.trash_burned = 0

        self.matrix = self.grid_to_matrix()

        self.datacollector = DataCollector(
            {"Get_burned": "trash_burned"}
        )

        center = Incinerador(self, (tamaño // 2, tamaño // 2), self)
        self.grid.place_agent(center, center.pos)
        self.schedule.add(center)
        #print(center.pos)

        arreglo_bot = ((tamaño - 1, tamaño - 1), (0, tamaño - 1), (0, 0), (tamaño - 1, 0), (tamaño // 2, tamaño - 1),
                       (tamaño // 2, 0))  # Convert set to list
        for i in range(6):
            pos = arreglo_bot[i]
            #print(pos)
            ghost = Bot(self, pos, i, Bot.sweeping, tamaño, center, self.matrix)
            self.grid.place_agent(ghost, pos)
            self.schedule.add(ghost)
            #print("Pos Robot:", ghost.pos)

        for _, (x, y) in self.grid.coord_iter():
            if (x, y) != ghost.pos and (x, y) != center.pos:
                if self.random.random() < density:
                    trash = Trash(self, (x, y))
                    self.grid.place_agent(trash, (x, y))
                    self.schedule.add(trash)
                    self.total_trash_placed += 1
        self.datacollector = DataCollector({"Percent burned": lambda m: (self.trash_burned / self.total_trash_placed)})

    def deleteagent(self, agent):
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)
        self.trash_burned += 1


    def grid_to_matrix(self):
        ancho, alto = self.grid.width, self.grid.height
        matrix = []

        for y in (range(alto)):
            row = []
            for x in range(ancho):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                if any(isinstance(agent, Trash) for agent in cell_contents):
                    row.append(0)
                #elif any(isinstance(agent, Bot) for agent in cell_contents):
                #    row.append('B')
                else:
                    row.append(1)
            matrix.append(row)
            #print(row)
        return matrix



    def print_grid(self):
        ancho, alto = self.grid.width, self.grid.height

        for y in reversed(range(alto)):
            row = ""
            for x in range(ancho):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                if any(isinstance(agent, Trash) for agent in cell_contents):
                    row += "[1]"
                elif any(isinstance(agent, Bot) for agent in cell_contents):
                    row += "[B]"
                else:
                    row += "[0]"
            #print(row)

    def step(self):
        # elf.update_grid()
        #self.print_grid()
        #self.grid_to_matrix()
        #print("Espacio-Acaba")
        if self.schedule.steps < self.time:
            self.schedule.step()
            self.datacollector.collect(self)


def agent_portrayal(agent):
    if isinstance(agent, Trash):
        if agent.condition == Trash.MOVING:
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "Green", "r": 0.25, "Layer": 2}
        elif agent.condition == Trash.STATIC:
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "Grey", "r": 0.75, "Layer": 1}
    elif isinstance(agent, Bot):
        if agent.condition == Bot.loaded:
            portrayal = {"Shape": "robot.png", "Layer": 1}
        elif agent.condition == Bot.free:
            portrayal = {"Shape": "ghost.png", "Layer": 1}
    elif isinstance(agent, Incinerador):
        if agent.condition == Incinerador.free:  # GREEN
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "yellow", "r": 0.75, "Layer": 0}
        elif agent.condition == Incinerador.burning:  # RED -- MORADO
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "purple", "r": 0.75, "Layer": 0}
        if agent.condition == Incinerador.visit:  # BLUE
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "blue", "r": 0.75, "Layer": 0}
    else:
        portrayal = {}
    return portrayal


grid = CanvasGrid(agent_portrayal, 51, 51, 600, 600)

chart = ChartModule([{"Label": "Percent burned", "Color": "Black"}], data_collector_name='datacollector')

server = ModularServer(Floor, [grid, chart], "PacMan", {
    "density": Slider("Trash density", 0.25, 0.01, 1.0, 0.01),
    # "num_robots":Slider("Numero de Robots", 1, 1, 4, 1),
    "size": Checkbox("Tamaño del Mapa", True),
    "time": Slider("Time", 1000, 1, 10000, 10),
})
#server.port = 8523
#server.launch()