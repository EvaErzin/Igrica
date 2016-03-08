import tkinter
import threading
import argparse
import logging

# Privzeta minimax globina, če je nismo podali ob zagonu v ukazni vrstici
MINIMAX_PRIVZETA_GLOBINA = 3 

######################################################################
# ## Igra


IGRALEC_1 = 1
IGRALEC_2 = 2
PRAZNO = "."

def nasprotnik(igralec):
    if igralec == IGRALEC_1:
        return IGRALEC_2
    elif igralec == IGRALEC_2:
        return IGRALEC_1
    else:
        assert False, "neveljaven nasprotnik"


class Igra():
    def __init__(self):
        self.polje = [[0, PRAZNO, PRAZNO, PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, 0, PRAZNO, PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, 0, PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO, 0, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO, PRAZNO, 0, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO, PRAZNO, PRAZNO, 0]]
        self.na_potezi = IGRALEC_1
        self.zgodovina = []

    def shrani_pozicijo(self):
        """Shrani trenutno pozicijo."""
        p = [self.polje[i][:] for i in range(6)]
        self.zgodovina.append((p, self.na_potezi))

    def kopija(self):
        """Vrne kopijo igre."""
        kopija = Igra()
        kopija.polje = [self.polje[i][:] for i in range(6)]
        kopija.na_potezi = self.na_potezi
        return kopija

    def razveljavi(self):
        """Razveljavi potezo in se vrne v prejšnje stanje."""
        (self.polje, self.na_potezi) = self.zgodovina.pop()

    def je_veljavna(self, i, j):
        """Vrne True, če je poteza veljavna in False, če je neveljavna."""
        return ((self.polje[i][j], self.polje[j][i]) == (PRAZNO, PRAZNO))

    def je_konec(self):
        '''Vrne trojico (True, porazenec, povezane pike), če je igra končana in (False, None, PRAZNO), če igre še ni konec.'''
        for i in range(6):
            for j in range(i, 6):  ## range(i, 6)??
                for k in range(6):
                    if self.polje[i][j]in [0, PRAZNO]:
                        pass
                    elif self.polje[i][j] == self.polje[j][k] == self.polje[k][i]:
                        return (True, self.polje[i][j], [i, j, k])
        return (False, None, PRAZNO)


    def veljavne_poteze(self):
        """Vrne seznam veljavnih potez."""
        poteze = []
        for i in range(6):
            for j in range(i, 6):
                if self.je_veljavna(i, j):
                    poteze.append((i,j))
        print(poteze)
        return poteze

    def povleci(self, i, j):
        """Povleče potezo in vrne dvojico pik, če je ta veljavna in vrne None če ni."""
        if (self.polje[i][j] is not PRAZNO) or (self.na_potezi == None):
            return None  #neveljavna poteza
        else:
            self.shrani_pozicijo()
            self.polje[i][j], self.polje[j][i] = self.na_potezi, self.na_potezi
            (konec, porazenec, povezane_pike) = self.je_konec()
            if konec:
                self.na_potezi = None
            else:
                self.na_potezi = nasprotnik(self.na_potezi)
            return (konec, porazenec, povezane_pike)


######################################################################
## Igralec clovek

class Clovek():
    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        pass

    def prekini(self):
        pass

    def klik(self, pozicija):
        self.gui.povleci_potezo(pozicija)
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
        self.plosca.create_oval(290,105,310,85,tags='pika0', fill='black')
        self.plosca.create_oval(440,210,460,190,tags='pika1', fill='black')
        self.plosca.create_oval(440,410,460,390,tags='pika2', fill='black')
        self.plosca.create_oval(290,515,310,495,tags='pika3', fill='black')
        self.plosca.create_oval(140,410,160,390,tags='pika4', fill='black')
        self.plosca.create_oval(140,210,160,190,tags='pika5', fill='black')

        self.plosca.tag_bind('pika0','<Button-1>',func=self.pika_klik(0))
        self.plosca.tag_bind('pika1','<Button-1>',func=self.pika_klik(1))
        self.plosca.tag_bind('pika2','<Button-1>',func=self.pika_klik(2))
        self.plosca.tag_bind('pika3','<Button-1>',func=self.pika_klik(3))
        self.plosca.tag_bind('pika4','<Button-1>',func=self.pika_klik(4))
        self.plosca.tag_bind('pika5','<Button-1>',func=self.pika_klik(5))

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

    def pika_klik(self, pozicija):
        def pomozna(event):
            if self.igra.na_potezi == IGRALEC_1:
                self.igralec_1.klik(pozicija)
            elif self.igra.na_potezi == IGRALEC_2:
                self.igralec_2.klik(pozicija)
        return pomozna

    def povleci_potezo(self, pozicija):
        """Povleci potezo (i,j)."""
        igralec = self.igra.na_potezi
        if self.pozicija_prve == None:
            self.pozicija_prve = pozicija
        elif self.igra.je_veljavna(self.pozicija_prve, pozicija):
            print('je kul')
            r = self.igra.povleci(self.pozicija_prve, pozicija)
            if r == None:
                print('bla bla')
            else:
                barva = ['blue', 'yellow'][igralec - 1]
                self.narisi_crto(self.pozicija_prve, pozicija, barva)
                # self.igra.povleci(self.pozicija_prve, pozicija)
            if r[0]:
                self.koncaj_igro()
            else:
                if self.igra.na_potezi == IGRALEC_1:
                    self.igralec_1.igraj()
                else:
                    self.igralec_2.igraj()
            self.pozicija_prve = None
        else:
            print('bla')
            self.pozicija_prve = None


            
            



######################################################################
## Glavni program

if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Sim")
    aplikacija = Gui(root)
    root.mainloop()
