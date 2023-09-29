from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import Slider
from mesa.space import MultiGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Checkbox
from random import randrange

from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule

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


    def __init__(self, model, pos, level, behaviour, tamano, incinerador):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.trash = None
        self.destino = None
        self.condition = self.free
        self.behaviour = behaviour
        self.initialpos = None
        self.search = self.searching
        self.level = level
        self.tamano = tamano
        self.center = (tamano//2, tamano//2)
        self.incinerador = incinerador
        self.loop = (1,0,0,0)
        self.loopcounter = 0
        self.centercells = self.model.grid.get_neighborhood(self.incinerador.pos, moore=True, radius=1)
            
    def movetopos(self, x, y):
        current_pos = self.pos
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
                    nextpos = (current_pos[0], current_pos[1] -1 )
        #if self.checkavailability(nextpos):
        self.model.grid.move_agent(self, nextpos)

    def pickup(self):
        bots = list(filter(lambda a:type (a) == Bot, self.model.grid.get_cell_list_contents(self.pos)))
        if len(bots) > 1:
            next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
            next_move = self.random.choice(next_moves)
            self.model.grid.move_agent(self, next_move)
            return False
        trash = list(filter(lambda a:type (a) == Trash, self.model.grid.get_cell_list_contents(self.pos)))
        if len(trash) == 1:
            if trash[0].condition == Trash.STATIC:
                self.trash = trash[0]
                self.condition = self.loaded
                self.destino = self.pos
                return True
        return False
    
    def sweep(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, radius=2)
        for i in range(len(neighbors)):
            trash = list(filter(lambda a:type (a) == Trash, self.model.grid.get_cell_list_contents(neighbors[i])))
            if len(trash) > 0:
                self.search = self.found
                i = randrange(0, len(trash))
                #print("Trash found at:" + str(trash[i].pos))
                return trash[i].pos

    def step(self):
        #print("bot number: " + str(self.level) +", x:" + str(self.pos[0]) +  ", y:" + str(self.pos[1]))
        #print("Destino" + str(self.destino))
        if self.trash == None:
            if self.behaviour == self.sweeping:
                if self.destino != None:
                    if self.pos != (self.destino[0], self.destino[1]):
                        self.movetopos(self.destino[0],self.destino[1])
                    elif self.pos == (self.destino[0], self.destino[1]):
                         self.destino = self.initialpos
                         self.search = self.busy
                         if not self.pickup():
                            #print("searching")
                            self.search = self.searching
                elif self.search == self.searching:
                    if self.sweep():
                        self.destino = self.sweep()
                    else:
                        if self.pos[0] == self.tamano -1 or self.pos[1] == self.tamano-1:
                            self.behaviour = self.patrolling
                        if self.pos[0] < self.tamano - 1:
                            if self.pos[1] < self.tamano -1:
                                self.movetopos(self.pos[0]+1, self.pos[1]+1)
                            else: 
                                self.movetopos(self.pos[0]+1, self.pos[1])
                        elif self.pos[1] < self.tamano - 1:
                            if self.pos[0] < self.tamano -1:
                                self.movetopos(self.pos[0]+1, self.pos[1]+1)
                            else: self.movetopos(self.pos[0], self.pos[1]+1)
                        
            elif self.behaviour == self.patrolling:
                if self.destino != None:
                    if self.pos != (self.destino[0], self.destino[1]):
                        self.movetopos(self.destino[0],self.destino[1])
                    elif self.pos == (self.destino[0], self.destino[1]):
                         self.destino = self.initialpos
                         self.search = self.busy
                         if not self.pickup():
                            #print("searching")
                            self.search = self.searching
                elif self.search == self.searching:
                    if self.sweep():
                        self.destino = self.sweep()
                if self.destino == None:
                    if self.loop == (1,0,0,0):
                        if self.pos[0] == (self.tamano - self.tamano + self.loopcounter):
                            self.loopcounter += 1
                            print(self.loopcounter)
                            self.loop = (0,0,1,0)
                            return
                        self.movetopos((self.tamano - self.tamano + self.loopcounter), self.pos[1])
                    elif self.loop == (1,1,0,0):
                        if self.pos[0] == (self.tamano - 1 - self.loopcounter):
                            self.loop = (0,0,1,1)
                            return
                        self.movetopos((self.tamano - 1 - self.loopcounter), self.pos[1])
                    elif self.loop == (0,0,1,0):
                        if self.pos[1] == (self.tamano - self.tamano + self.loopcounter):
                            self.loop = (1,1,0,0)
                            return
                        self.movetopos(self.pos[0], (self.tamano - self.tamano + self.loopcounter))
                    elif self.loop == (0,0,1,1):
                        if self.pos[1] == (self.tamano - 1 - self.loopcounter):
                            self.loop = (1,0,0,0)
                            return
                        self.movetopos(self.pos[0], (self.tamano - 1 - self.loopcounter))

                    if self.loopcounter > 13: self.behaviour = self.idle
                print("patrolling")

        else:
            if self.pos == self.center:
                self.trash = None
                self.condition = self.free
            elif self.pos in self.centercells:
                print("incinerador:" + str(self.incinerador.condition))
                if self.incinerador.condition == self.incinerador.free:
                    if self.incinerador.choosebot():
                        self.movetopos(self.center[0],self.center[1])
                        self.trash.move(self.pos[0], self.pos[1])

                        #self.trash = None
                        #self.condition = self.free
                    return
                return
                #deposit trash
            else:
                self.movetopos(self.center[0],self.center[1])
                self.trash.move(self.pos[0], self.pos[1])
            
class incinerador(Agent):
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
        trash = list(filter(lambda a:type (a) == Trash, self.model.grid.get_cell_list_contents(self.pos)))
        if len(trash) == 1:
            self.trash = trash[0]
            print("adgfdghfgfdsfdfsdgfffffffffffffffffffffffffffffffffffffssssssssssss")
            return True
        return False
    
    def choosebot(self):
        if self.condition == self.free:
            self.condition = self.visit
            return True

    def step(self):
        if self.checktrash():
            self.world.deleteagent(self.trash)
            self.condition = self.visit
            print("burned trash")
        else:
            if self.condition == self.visit: #blue
                self.condition = self.burning #morado
            elif self.condition == self.burning:
                self.condition = self.free #yelow
        
class Trash(Agent):
    STATIC = 0
    MOVING = 1

    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.condition = self.STATIC
        self.pos = pos 
        self.bot = None    
    def move(self, x,y):
        self.condition = self.MOVING
        self.model.grid.move_agent(self, (x,y))
    
basura_total = 0

class Floor(Model):
    def __init__(self, density=0.45, num_robots=1, size=False, tamaño=51, time = 1000):
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
        
        self.datacollector = DataCollector(
            {"Get_burned": "trash_burned"}
        )

        center = incinerador(self, (tamaño//2, tamaño//2), self)
        self.grid.place_agent(center, center.pos)
        self.schedule.add(center)
        print(center.pos)

        arreglo_bot = ((tamaño-1,tamaño-1), (0,tamaño-1),(0,0), (tamaño-1,0), (tamaño//2, tamaño-1), (tamaño//2, 0))  # Convert set to list
        for i in range(6):
            pos = arreglo_bot[i]
            print(pos)
            ghost = Bot(self, pos, i, Bot.sweeping, tamaño, center)
            self.grid.place_agent(ghost, pos)
            self.schedule.add(ghost)
            print("Pos Robot:", ghost.pos)

        for _, (x, y) in self.grid.coord_iter():
            if (x, y) != ghost.pos and (x, y) != center.pos:
                if self.random.random() < density:
                    trash = Trash(self, (x, y))
                    self.grid.place_agent(trash, (x, y))
                    self.schedule.add(trash)
                    self.total_trash_placed += 1
        self.datacollector = DataCollector({"Percent burned": lambda m:(self.trash_burned/ self.total_trash_placed)})


    def deleteagent(self, agent):
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)
        self.trash_burned += 1
    

    def step(self):
        if self.schedule.steps < self.time:
            self.schedule.step()
            self.datacollector.collect(self)


def agent_portrayal(agent):
    if isinstance(agent,Trash):
        if agent.condition == Trash.MOVING: 
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "Green", "r": 0.25, "Layer": 2}
        elif agent.condition == Trash.STATIC:
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "Grey", "r": 0.75, "Layer": 1}
    elif isinstance(agent, Bot):
        if agent.condition == Bot.loaded:
            portrayal = {"Shape": "robot.png", "Layer": 1}
        elif agent.condition == Bot.free:
            portrayal = {"Shape": "ghost.png", "Layer": 1}
    elif isinstance(agent, incinerador):
        if agent.condition == incinerador.free: #GREEN
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "yellow", "r": 0.75, "Layer": 0}
        elif agent.condition == incinerador.burning: #RED -- MORADO
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "purple", "r": 0.75, "Layer": 0}
        if agent.condition == incinerador.visit: #BLUE
            portrayal = {"Shape": "circle", "Filled": "true", "Color": "blue", "r": 0.75, "Layer": 0}
    else:
        portrayal = {}
    return portrayal

grid = CanvasGrid(agent_portrayal, 51, 51, 600, 600)

chart = ChartModule([{"Label": "Percent burned", "Color": "Black"}], data_collector_name='datacollector')

server = ModularServer(Floor, [grid, chart], "PacMan", {
    "density": Slider("Trash density", 0.15, 0.01, 1.0, 0.01),
    "size": Checkbox("Tamaño del Mapa", True),
    "time": Slider("Time", 1000, 1, 10000, 10),
})
server.port = 8523
#server.launch()