from time import perf_counter
import os
import platform

import pygame
from pygame.locals import *
import tkinter as tk
from PIL import ImageTk, Image

from sprites import Zuikis, Vilkas, Morka

##
#Path must be a list of game states. Each state describes the game completely i.e. it tells where every entity is on the grid.
#Each state has 5 elements: zuikis, wolves, carrots, energy, zuikis state.
#Zuikis element is tuple of 2 numbers where zuikis is on the board. In terms of square coordinates
#Wolves element is a list of tuples. Each tuple is square coordinates for each wolf
#Carrot element is a list of tuples for each carrot. Again tuples containt coordinates in the grid.
#Energy element is a number that represents energy of zuikis in the state.
#Zuikis state is last element that consists of current field of view for zuikis.
#Diference between each state is one turn. For example game is initialized in state Path[0], then entities make their moves
#and game evolves to state Path[1].
##

class Window:
    def __init__(self, path = None, dim = (30, 30), squaredim = 25, speed = 1, guilen = 360, showQ = False, q = None):
        ##GUI parameters
        self.guilen = guilen
        self.show_q = showQ
        self.gui_height = 30
        self.state_padding = 2
        self.state_line_width = 1
        self.state_icon_dim = (self.guilen) // 9
        self.state_dim = 9 * self.state_icon_dim


        anch = 'w'
        info_anch = 'w'
        part_len = 0.6
        first_width = int(self.guilen * part_len)
        second_width = int(self.guilen * part_len)

        self.gui_bg = 'snow'
        self.gui_fg_text = 'black'
        self.gui_fg_num = '#ff931e'
        self.gui_font = 'Courier 18 bold'
        self.gui_font_secondary = 'Courier 16'
        ## GUI building
        self.path = path
        self.q = q
        ##q must be same length list as path. Each state-action description for each state
        if self.q and len(self.q) != len(self.path):
            print('WARNING: q doesnt match the pat.h')
            exit(1)
        self.root = tk.Tk() #Main window
        self.root.title('Zuikis adventures') #Name of the window
        self.field = FieldState(field=dim, square=squaredim, nwolves=len(path[0][1]), ncarrots=len(path[0][2])) #Field visualization object init.
        self.field_dims = self.field.get_size()
        self.height, self.width = self.field_dims[0], self.field_dims[1] + self.guilen #Window dims based on the field dims.
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen
        xmid = (ws / 2) - (self.width / 2)
        ymid = (hs / 2) - (self.height / 2)
        self.root.geometry('{}x{}+{}+{}'.format(self.width, max([self.height,self.gui_height* 9 + self.state_dim]), int(xmid), int(ymid))) #Fixes whole window size and starting position
        self.root.resizable(False, False) #Make window unresizable

        self.embed = tk.Frame(self.root, width=self.width-self.guilen, height=self.height) #Embeded pygame frame for field visualization
        self.embed.place(x = 0, y = 0, width = self.width-self.guilen, height = self.height)

        ##GUI stuff
        ######

        self.current_state = 0
        self.playing = False
        self.interval = 1 #Wait time while playing in seconds
        self.speed = speed #Speed of playing: speed = 1/interval and viceversa
        self.last_gui_update = perf_counter()


        ##Labels for total number of moves
        self.total_moves = tk.Label(text = 'Total: ', font = self.gui_font, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.total_moves.place(y = 0, x = self.width - self.guilen, width = first_width, height = self.gui_height)
        self.total_num = tk.Label(text = int(len(self.path)-1), font = self.gui_font, anchor = info_anch, width = 10,bg = self.gui_bg, fg = self.gui_fg_text)
        self.total_num.place(y = 0, x = self.width - self.guilen + first_width, width = second_width, height = self.gui_height)
        ##Labels for current move
        self.current_move = tk.Label(text = 'Current:', font = self.gui_font, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.current_move.place(y = self.gui_height * 1, x = self.width - self.guilen, height = self.gui_height, width = first_width)
        self.current_move_num = tk.Label(text = str(1000), font = self.gui_font, anchor = info_anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.current_move_num.place(y = self.gui_height * 1, x = self.width - self.guilen + first_width, height = self.gui_height, width = second_width)
        ##Labels for current energy
        self.current_energy = tk.Label(text = 'Energy:', font = self.gui_font, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text)
        self.current_energy.place(y=self.gui_height * 2, x=self.width - self.guilen, height=self.gui_height,
                                width=first_width)
        self.current_energy_num = tk.Label(text = str(1000.0), font = self.gui_font, anchor = info_anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_num)
        self.current_energy_num.place(y = self.gui_height * 2, x = self.width - self.guilen + first_width, height = self.gui_height, width = second_width)
        ##Slider for current move/state
        self.path_slider = tk.Scale(self.root, from_ = 1, to = len(self.path), orient = tk.HORIZONTAL, length = self.guilen-10,activebackground = self.gui_fg_num, showvalue = False)
        self.path_slider.bind('<B1-Motion>', self.path_slider_onpressmove)
        self.path_slider.place(y = self.gui_height * 3, x = self.width - self.guilen, height = self.gui_height, width = self.guilen)
        #Play button
        def on_play_press():
            if self.playing:
                self.play_button.config(relief = tk.GROOVE, bg = self.gui_bg)
            else: self.play_button.config(relief = tk.SUNKEN, bg= self.gui_fg_num)
            self.playing = not self.playing

        self.play_button = tk.Button(self.root, text='Play', command = on_play_press, width = 25, relief = tk.GROOVE, bg= self.gui_bg)
        self.play_button.place(y = self.gui_height * 4, x = self.width-self.guilen, width = self.guilen, height = self.gui_height)
        #Backwards and forwards buttons
        def on_back_press():
            if self.current_state > 0:
                self.current_state -= 1;
                self.update_currents()

        def on_next_press():
            if self.current_state < self.path.__len__() - 1:
                self.current_state += 1
                self.update_currents()

        self.previous_button = tk.Button(self.root, text='<-', command = on_back_press, relief = tk.GROOVE,bg= self.gui_bg)
        self.previous_button.place(x = self.width - self.guilen, y = self.gui_height * 5, width = self.guilen//4, height = self.gui_height)
        self.next_button = tk.Button(self.root, text='->', command = on_next_press,  relief = tk.GROOVE, bg= self.gui_bg)
        self.next_button.place(x = self.width - self.guilen + self.guilen//4, y = self.gui_height * 5, width = self.guilen//4, height = self.gui_height)

        #Animation speed slider
        self.speed_slider = tk.Scale(self.root, label = 'Speed', from_ = 0.5, to = 15,orient = tk.HORIZONTAL, length = self.guilen-10,activebackground = self.gui_fg_num)
        self.speed_slider.set(self.speed)
        self.speed_slider.bind('<B1-Motion>', self.speed_slider_onpressmove)
        self.speed_slider.place(x = self.width-self.guilen, y = self.gui_height * 6, width = self.guilen, height = self.gui_height * 2)
        #Tkinter images and zuikis state visualization stuff
        zuikis_img = Image.open("pics/—Pngtree—rabbit_2622880.png").resize((self.state_icon_dim, self.state_icon_dim),Image.ANTIALIAS)
        wolf_img = Image.open("pics/wolf.png").resize((self.state_icon_dim, self.state_icon_dim),Image.ANTIALIAS)
        carrot_img = Image.open("pics/carrot.png").resize((self.state_icon_dim, self.state_icon_dim),Image.ANTIALIAS)\
        #icons on the screen
        self.zuikis_icon = ImageTk.PhotoImage(zuikis_img)
        self.wolf_icon = ImageTk.PhotoImage(wolf_img)
        self.carrot_icon = ImageTk.PhotoImage(carrot_img)
        ##Canvas to zuikis state
        self.zuikis_state = tk.Canvas(self.root, width = self.guilen, height = self.guilen)
        self.zuikis_state.place(x = self.width-self.guilen+self.state_padding, y = self.gui_height*8, width = self.state_dim, height = self.state_dim)
        self.draw_zuikis_state()
        ##Zuikis state info label
        self.zuikis_state_info = tk.Label(text = '', font = self.gui_font_secondary, anchor = anch, width = 10, bg = self.gui_bg, fg = self.gui_fg_text, justify=tk.LEFT, wraplength = self.guilen)
        self.zuikis_state_info.place(x = self.width - self.guilen, y = self.gui_height*8 + self.state_dim, width = self.guilen, height = self.gui_height * 2)
        self.update_zuikis_state_info()
        ##Rest
        ######
        #Stuff for embedding
        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
        if platform.system() == 'Windows':
            os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.field.create()#Creates the field visualization
        self.running = True

        #Window closing func
        def on_close():
            self.running = False
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.update_currents()
        self.run()#Init main loop

    def run(self):
        """Runs main loop for updating everything inside the window"""
        while self.running:
            self.field.update() #Updates fieldview subwindow
            self.gui_update() #Updates gui
            self.root.update() #Updates whole window

    def gui_update(self):
        """Updates gui elements"""
        if perf_counter() - self.last_gui_update >= self.interval:
            if self.playing:
                next_val = self.current_state + 1
                if next_val >= len(self.path):
                    next_val = 0
                self.current_state = next_val
                self.update_currents()

                self.path_slider.set(self.current_state)
            self.last_gui_update = perf_counter()

    def path_slider_onpressmove(self, event):
        if self.current_state != (self.path_slider.get() - 1):
            self.current_state = self.path_slider.get() - 1
            self.update_currents()

    def speed_slider_onpressmove(self, event):
        if self.speed != (self.speed_slider.get()):
            self.speed = self.speed_slider.get()
            self.interval = 1/self.speed

    def update_currents(self):
        """Update current field and gui elements"""
        self.field.set_state(self.path[self.current_state])
        self.current_move_num.config(text = str(self.current_state))
        self.current_energy_num.config(text = '{:.1f}'.format(float(self.path[self.current_state][3])))
        self.path_slider.set(self.current_state)
        self.update_zuikis_state_info()
        self.draw_zuikis_state()

    def draw_zuikis_state(self):
        self.zuikis_state.delete('all')
        self.draw_zuikis_grids()
        zuikis_pos = (4,4)
        current_zuikis_state = self.path[self.current_state][4]
        for row in range(9):
            rel_y = row - zuikis_pos[1]
            current_y = row * self.state_icon_dim
            for col in range(9):
                rel_x = col - zuikis_pos[0]
                this_pos = (rel_x, rel_y)
                current_x = col * self.state_icon_dim
                ##Draw indicator of outside vision - black square
                if abs(this_pos[0]) + abs(this_pos[1]) > 4:
                    self.zuikis_state.create_rectangle(current_x, current_y, current_x + self.state_icon_dim, current_y + self.state_icon_dim, fill='black')
                ##Draw wolf
                elif this_pos in current_zuikis_state[0]:
                    self.zuikis_state.create_image(current_x+self.state_icon_dim//2, current_y+self.state_icon_dim//2, image=self.wolf_icon)
                ##Draw carrot
                elif this_pos in current_zuikis_state[1]:
                    self.zuikis_state.create_image(current_x+self.state_icon_dim//2, current_y+self.state_icon_dim//2, image=self.carrot_icon)
                ##Draw zuikis himself
                elif this_pos == (0,0):
                    self.zuikis_state.create_image(current_x+self.state_icon_dim//2, current_y+self.state_icon_dim//2, image=self.zuikis_icon)
                ##Draw walls. In x direction
                elif (rel_x <= current_zuikis_state[2][0] and current_zuikis_state[2][0] < 0) or (rel_x >= current_zuikis_state[2][0] and current_zuikis_state[2][0] > 0):
                    self.zuikis_state.create_rectangle(current_x, current_y, current_x + self.state_icon_dim, current_y + self.state_icon_dim, fill='grey')
                ##In y direction
                elif (rel_y <= current_zuikis_state[2][1] and current_zuikis_state[2][1] < 0) or (rel_y >= current_zuikis_state[2][1] and current_zuikis_state[2][1] > 0):
                    self.zuikis_state.create_rectangle(current_x, current_y, current_x + self.state_icon_dim, current_y + self.state_icon_dim, fill='grey')

    def draw_zuikis_grids(self):
        #Draw bacground
        self.zuikis_state.create_rectangle(0,0,self.state_dim, self.state_dim, fill=self.gui_bg)
        # Draws grid
        for row in range(9):
            hgh = self.state_icon_dim * (row + 1)
            self.zuikis_state.create_line(1, hgh, self.state_dim, hgh, width=self.state_line_width)
        for col in range(9):
            wdt = self.state_icon_dim * (col + 1)
            self.zuikis_state.create_line(wdt, 1, wdt, self.state_dim, width=self.state_line_width)
        ##Draws outer bounds
        self.zuikis_state.create_line(1, 1, 1, self.state_dim, width = 3)
        self.zuikis_state.create_line(1, 1, self.state_dim, 1, width=3)
        self.zuikis_state.create_line(1, self.state_dim-2, self.state_dim, self.state_dim-2, width=3)
        self.zuikis_state.create_line(self.state_dim-2, 0, self.state_dim - 2,self.state_dim, width = 3)

    def update_zuikis_state_info(self):
        current_zuikis_state = self.path[self.current_state][4]
        wolfs = current_zuikis_state[0]
        carrots = current_zuikis_state[1]
        walls = current_zuikis_state[2]
        pattern = 'W: {} C: {} Wl: {}'
        self.zuikis_state_info.config(text = pattern.format(wolfs, carrots, walls))


class FieldState:
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255,255,255)
    GREY1 = pygame.Color(199, 201, 215)

    def __init__(self, field = (30, 30), square = 20, boundthick = 4, innerthick = 2, nwolves = 1, ncarrots = 5):
        self.created = False
        self.n_vilkai, self.n_morkos = nwolves, ncarrots
        self.square = square
        self.field = field
        self.height, self.width = field[0] * square + 2*boundthick, field[1]*square + 2 * boundthick
        self.x0, self.y0 = boundthick, boundthick

        self.grid_thick = boundthick * 2 + 1
        self.grid_inner_thick = innerthick
        self.screen = None
        self.sprites = pygame.sprite.Group()
        self.FramePerSec = None
        self.zuikis = None
        self.vilkai = []
        self.morkos = []
        self.FPS = 60

    def create(self):
        if self.created:
            print('Warning: field visual is already created.')
            return
        self.created = True
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(self.WHITE)
        self.FramePerSec = pygame.time.Clock()


        #Create and deal with entities
        self.zuikis = Zuikis(self)
        for i in range(self.n_vilkai):
            self.vilkai.append(Vilkas(self))
        for i in range(self.n_morkos):
            self.morkos.append(Morka(self))
        # self.move_entity(self.zuikis, 28, 15)
        # self.move_entity(self.morkos[0], 0, 0)
        # self.move_entity(self.vilkai[0], 10, 0)
        self.sprites.add(self.zuikis)
        for v in self.vilkai: self.sprites.add(v)
        for m in self.morkos: self.sprites.add(m)

    def update(self):
        self.FramePerSec.tick(self.FPS)
        self.sprites.draw(self.screen)

        ##Update
        self.sprites.update()
        ##Render
        self.screen.fill((self.WHITE))
        self.draw_grids()
        self.sprites.draw(self.screen)
        ##Flip
        pygame.display.flip()

    def draw_grids(self):
        """Draw grid lines in the field"""
        #Draw horizontal lines
        for i in range(1, self.field[0]):
            pygame.draw.line(self.screen, self.GREY1, (0, self.y0 + self.square * i), (self.width, self.y0 + self.square * i), self.grid_inner_thick)
        for i in range(1, self.field[1]):
            pygame.draw.line(self.screen, self.GREY1, (self.x0 + self.square * i, 0), (self.x0 + self.square * i, self.height), self.grid_inner_thick)

        pygame.draw.line(self.screen, self.BLACK, (0,0), (0,self.height), self.grid_thick)
        pygame.draw.line(self.screen, self.BLACK, (self.width, 0), (self.width, self.height), self.grid_thick)
        pygame.draw.line(self.screen, self.BLACK, (0, 0), (self.width, 0), self.grid_thick)
        pygame.draw.line(self.screen, self.BLACK, (0, self.height), (self.width, self.height), self.grid_thick)

    def move_entity(self, ent,x, y):
        """Moves sprite to different place on the grid"""
        ent.rect.topleft = (self.x0 + x * self.square, self.y0 + y * self.square)

    def set_state(self,state):
        self.move_entity(self.zuikis, state[0][0], state[0][1]) #Move Zuikis
        #Move all Wolfes
        for ind, st in enumerate(state[1]):
            self.move_entity(self.vilkai[ind], st[0],st[1])
        #Move all Carrots
        for ind, st in enumerate(state[2]):
            self.move_entity(self.morkos[ind], st[0],st[1])

    def get_size(self):
        return self.height, self.width
