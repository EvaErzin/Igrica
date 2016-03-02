import tkinter

# Privzeta minimax globina, če je nismo podali ob zagonu v ukazni vrstici
MINIMAX_PRIVZETA_GLOBINA = 3 

######################################################################
## Igra


IGRALEC_1 = 1
IGRALEC_2 = 2

def nasprotnik(igralec):
    if igralec == IGRALEC_1:
        return IGRALEC_1
    else:
        return IGRALEC_2

class Igra():
    def __init__(self):
        self.polje = [[0, None, None, None, None, None],
                      [None, 0, None, None, None, None],
                      [None, None, 0, None, None, None],
                      [None, None, None, 0, None, None],
                      [None, None, None, None, 0, None],
                      [None, None, None, None, None, 0]]
        self.na_potezi = IGRALEC_1
        self.zgodovina = []

    def shrani_pozicijo(self):
        p = [self.polje[i][:] for i in range(6)]
        self.zgodovina.append((p, self.na_potezi))

    def razveljavi(self):
        (self.polje, self.na_potezi) = self.zgodovina.pop()

    def je_veljavna(self, i, j):
        print(self.polje)
        return (self.polje[i][j], self.polje[j][i]) == (None, None)

    def je_konec(self):
        '''Vrne trojico (True, porazenec, povezane pike), če je igra končana in (False, None, None), če igre še ni konec.'''
        for i in range(6):
            for j in range(i, 6):  ## range(i, 6)??
                for k in range(j, 6):
                    if self.polje[i][j]in [0, None]:
                        pass
                    elif self.polje[i][j] == self.polje[j][k] == self.polje[k][i]:
                        return (True, self.polje[i][j], [i, j, k])
        return (False, None, None)


    def veljavne_poteze(self):
        poteze = []
        for i in range(6):
            for j in range(i, 6):
                if self.je_veljavna(i, j):
                    poteze.append((i,j))
        return poteze

    def povleci(self, i, j):
        if self.polje[i][j] is not None:
            return None  #neveljavna poteza
        else:
            self.shrani_pozicijo()
            self.polje[i][j], self.polje[j][i] = self.na_potezi, self.na_potezi
            self.na_potezi = nasprotnik(self.na_potezi)
            return (i, j)


######################################################################
## Igralec clovek

class Clovek():
    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        pass



######################################################################
## Igralec minimax

class Minimax():
    def __init__(self, globina):
        self.globina = globina

    def poteza(self, igra, igralec):
        return igra.veljavne_poteze[0]
        
######################################################################
## Uporabniški vmesnik

class Gui():

    def __init__(self, master):
        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu)

        # Podmenu za izbiro igre
        menu_igra = tkinter.Menu(menu)
        menu.add_cascade(label="Igra", menu=menu_igra)
        menu_igra.add_command(label="X=Človek, O=Človek",         command=lambda: self.zacni_igro(Clovek, Clovek))
        menu_igra.add_command(label="X=Človek, O=Računalnik",     command=lambda: self.zacni_igro(Clovek, Minimax))
        menu_igra.add_command(label="X=Računalnik, O=Človek",     command=lambda: self.zacni_igro(Minimax, Clovek))
        menu_igra.add_command(label="X=Računalnik, O=Računalnik", command=lambda: self.zacni_igro(Minimax, Minimax))

        # Katera pika
        self.pozicija_prve = None
        
        # Napis, ki prikazuje stanje igre
        self.napis = tkinter.StringVar(master, value="Isti SimCity")
        tkinter.Label(master, textvariable=self.napis).grid(row=0, column=0)

        # Igralno območje
        self.plosca = tkinter.Canvas(master, width=600, height=600)
        self.plosca.grid(row=1, column=0, columnspan=2)

        # Pike na igralnem polju
        self.plosca.create_oval(295,100,305,90,tags='pika0', fill='black')
        self.plosca.create_oval(445,205,455,195,tags='pika1', fill='black')
        self.plosca.create_oval(445,405,455,395,tags='pika2', fill='black')
        self.plosca.create_oval(295,510,305,500,tags='pika3', fill='black')
        self.plosca.create_oval(145,405,155,395,tags='pika4', fill='black')
        self.plosca.create_oval(145,205,155,195,tags='pika5', fill='black')

        self.plosca.tag_bind('pika0','<Button-1>',func=self.povleci_potezo(0))
        self.plosca.tag_bind('pika1','<Button-1>',func=self.povleci_potezo(1))
        self.plosca.tag_bind('pika2','<Button-1>',func=self.povleci_potezo(2))
        self.plosca.tag_bind('pika3','<Button-1>',func=self.povleci_potezo(3))
        self.plosca.tag_bind('pika4','<Button-1>',func=self.povleci_potezo(4))
        self.plosca.tag_bind('pika5','<Button-1>',func=self.povleci_potezo(5))

        # Prični z izbiro igralcev
        self.zacni_igro(Clovek, Clovek)

    def izbira_igralcev(self):
        """Nastavi stanje igre na izbiranje igralcev."""
        # Zaenkrat kar preskocimo izbiro igralcev in
        # predpostavimo, da sta oba igralca človeka
        self.igralec_1 = Clovek(self)
        self.igralec_2 = Clovek(self)
        self.zacni_igro()

    def zacni_igro(self, igralec_1, igralec_2):
        """Nastavi stanje igre na zacetek igre."""
        self.igra = Igra()
        self.igralec_1 = igralec_1(self)
        self.igralec_2 = igralec_2(self)
        self.igralec_1.igraj()

    def koncaj_igro(self):
        """Nastavi stanje igre na konec igre."""
        print ("KONEC!")

    def narisi_crto(self, prva_pika, druga_pika, barva):
        pike = [[300, 95],
                [450, 200],
                [450, 400],
                [300, 505],
                [150, 400],
                [150, 200]]
        x0, y0 = pike[prva_pika][0], pike[prva_pika][1]
        x1, y1 = pike[druga_pika][0], pike[druga_pika][1]
        self.plosca.create_line(x0, y0, x1, y1, fill=barva, width=5)

    def povleci_potezo(self, pozicija):
        """Povleci potezo (i,j)."""
        def pomozna(event):
            ## dodaj se pogoj, da mora biti igra veljavna!!
            igralec = self.igra.na_potezi
            if self.pozicija_prve == None:
                self.pozicija_prve = pozicija
            elif self.igra.je_veljavna(self.pozicija_prve, pozicija):
                r = self.igra.povleci(self.pozicija_prve, pozicija)
                if r == None:
                    pass
                else:
                    barva = ['blue', 'yellow'][igralec - 1]
                    self.narisi_crto(self.pozicija_prve, pozicija, barva)
                    self.igra.povleci(self.pozicija_prve, pozicija)
                if self.igra.je_konec()[0]:
                    self.koncaj_igro()
                else:
                    if self.igra.na_potezi == IGRALEC_1:
                        self.igralec_1.igraj()
                    else:
                        self.igralec_2.igraj()
                self.pozicija_prve = None
        return pomozna
            
            



######################################################################
## Glavni program

if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Sim")
    aplikacija = Gui(root)
    root.mainloop()
