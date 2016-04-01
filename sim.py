import tkinter
import threading
import argparse
import logging


# Privzeta minimax globina, če je nismo podali ob zagonu v ukazni vrstici
PRIVZETA_GLOBINA = 3

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
        # XXX tu je zapečeno število 6
        self.polje = [[0, PRAZNO, PRAZNO, PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, 0, PRAZNO, PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, 0, PRAZNO, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO, 0, PRAZNO, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO, PRAZNO, 0, PRAZNO],
                      [PRAZNO, PRAZNO, PRAZNO, PRAZNO, PRAZNO, 0]]
        self.na_potezi = IGRALEC_1
        self.zgodovina = []
        self.zgodovina_pik = []

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
        return self.polje[i][j] == PRAZNO

    def je_konec(self):
        """Vrne trojico (True, porazenec, povezane pike), če je igra končana in (False, None, PRAZNO), če igre še ni konec."""
        for i in range(6):
            for j in range(i+1, 6):  ## range(i, 6)??
                for k in range(j+1, 6):
                    if self.polje[i][j]in [0, PRAZNO]:
                        pass
                    elif self.polje[i][j] == self.polje[j][k] == self.polje[k][i]:
                        return (True, self.polje[i][j], [i, j, k])
        return (False, None, PRAZNO)


    def veljavne_poteze(self):
        """Vrne seznam veljavnih potez."""
        poteze = []
        for i in range(6):
            for j in range(i+1, 6):
                if self.je_veljavna(i, j) and (i, j) not in poteze:
                    poteze.append((i,j))
        return poteze


    def povleci(self, i, j):
        """Povleče potezo in vrne dvojico pik, če je ta veljavna in vrne None če ni."""
        if (self.polje[i][j] is not PRAZNO) or (self.na_potezi == None):
            return None  #neveljavna poteza
        else:
            self.shrani_pozicijo()
            self.polje[i][j], self.polje[j][i] = self.na_potezi, self.na_potezi
            self.zgodovina_pik.append((i, j))
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
## Igralec računalnik

class Racunalnik():
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem #Algoritem, ki izračuna potezo
        self.mislec = None #Vlakno, ki razmišlja

    def igraj(self):
        """Igra potezo, ki jo vrne algoritem"""
        self.mislec = threading.Thread(target=lambda : self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))
        self.mislec.start()
        self.gui.plosca.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        if self.algoritem.poteza is not None:
            self.gui.povleci_potezo(self.algoritem.poteza[0])
            self.gui.povleci_potezo(self.algoritem.poteza[1])
            self.mislec = None
        else:
            self.gui.plosca.after(100, self.preveri_potezo)

    def prekini(self):
        if self.mislec:
            logging.debug("Prekinjamo{0}".format(self.mislec))
            self.algoritem.prekini()
            self.mislec.join()
            self.mislec = None

    def klik(self, p):
        pass


######################################################################
## Igralec minimax

class Minimax():
    def __init__(self, globina):
        self.globina = globina
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteza = None

    def prekini(self):
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izračuna potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.minimax(self.globina, True)
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
        self.poteza = poteza

    # Vrednosti igre
    ZMAGA = 100000
    NESKONCNO = ZMAGA + 1

    def vrednost_pozicije(self):
        """Ocena vrednosti pozicije: sešteje vrednosti vseh trikotnikov na plošči."""
        vrednost_trikotnika = {
            (0, 3): Minimax.ZMAGA,
            (3, 0): -Minimax.ZMAGA//10,
            (0, 2): Minimax.ZMAGA//100,
            (2, 0): -Minimax.ZMAGA//1000,
            (0, 1): Minimax.ZMAGA//10000,
            (1, 0): -Minimax.ZMAGA//100000
        }
        vrednost = 0
        for i in range(6):
            for j in range(i+1, 6):
                for k in range (j+1, 6):
                    x = 0
                    y = 0
                    if self.igra.polje[i][j] == self.jaz:
                        x += 1
                    elif self.igra.polje[i][j] == nasprotnik(self.jaz):
                        y += 1
                    if self.igra.polje[j][k] == self.jaz:
                        x += 1
                    elif self.igra.polje[j][k] == nasprotnik(self.jaz):
                        y += 1
                    if self.igra.polje[i][k] == self.jaz:
                        x += 1
                    elif self.igra.polje[i][k] == nasprotnik(self.jaz):
                        y += 1
                    vrednost += vrednost_trikotnika.get((x, y), 0)
        return vrednost

    def minimax(self, globina, maksimiziramo):
        """Glavna metoda minimax."""
        if self.prekinitev:
            logging.debug("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)
        (konec, porazenec, pike) = self.igra.je_konec()
        if konec:
            if porazenec == self.jaz:
                return (None, -Minimax.ZMAGA)
            elif porazenec == nasprotnik(self.jaz):
                return (None, Minimax.ZMAGA)
            else:
                assert False, "Konec igre brez zmagovalca."
        elif not konec:
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                if maksimiziramo:
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    for (i, j) in self.igra.veljavne_poteze():
                        self.igra.povleci(i, j)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = (i, j)
                else:
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    for (i, j) in self.igra.veljavne_poteze():
                        self.igra.povleci(i, j)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = (i, j)

                assert (najboljsa_poteza is not None), "minimax: izračunana poteza je None"
                return (najboljsa_poteza, vrednost_najboljse)
        else: assert False, "minimax: nedefinirano stanje igre"

######################################################################
## Igralec alfa-beta

class Alpha_Beta():

    def __init__(self, globina):
        self.globina = globina
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteza = None

    def prekini(self):
        self.prekinitev = True

    # Vrednosti igre
    ZMAGA = 100000
    NESKONCNO = ZMAGA + 1

    def vrednost_pozicije(self):
        """Ocena vrednosti pozicije: sešteje vrednosti vseh trikotnikov na plošči."""
        vrednost_trikotnika = {
            (0, 3): Alpha_Beta.ZMAGA,
            (3, 0): -Alpha_Beta.ZMAGA//10,
            (0, 2): Alpha_Beta.ZMAGA//100,
            (2, 0): -Alpha_Beta.ZMAGA//1000,
            (0, 1): Alpha_Beta.ZMAGA//10000,
            (1, 0): -Alpha_Beta.ZMAGA//100000
        }
        vrednost = 0
        for i in range(6):
            for j in range(i+1, 6):
                for k in range (j+1, 6):
                    x = 0
                    y = 0
                    if self.igra.polje[i][j] == self.jaz:
                        x += 1
                    elif self.igra.polje[i][j] == nasprotnik(self.jaz):
                        y += 1
                    if self.igra.polje[j][k] == self.jaz:
                        x += 1
                    elif self.igra.polje[j][k] == nasprotnik(self.jaz):
                        y += 1
                    if self.igra.polje[i][k] == self.jaz:
                        x += 1
                    elif self.igra.polje[i][k] == nasprotnik(self.jaz):
                        y += 1
                    vrednost += vrednost_trikotnika.get((x, y), 0)
        return vrednost

    def izracunaj_potezo(self, igra):
        """Izračuna potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.alphabeta(self.globina, True, -Alpha_Beta.NESKONCNO, Alpha_Beta.NESKONCNO)
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
        self.poteza = poteza

    def alphabeta(self, globina, maksimiziramo, alpha, beta):
        """Glavna metoda minimax."""
        if self.prekinitev:
            logging.debug("Minimax prekinja, globina = {0}".format(globina))
            return (None, 0)
        (konec, porazenec, pike) = self.igra.je_konec()
        if konec:
            if porazenec == self.jaz:
                return (None, -Alpha_Beta.ZMAGA)
            elif porazenec == nasprotnik(self.jaz):
                return (None, Alpha_Beta.ZMAGA)
            else:
                assert False, "Konec igre brez zmagovalca."
        elif not konec:
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                if maksimiziramo:
                    a = alpha
                    b = beta
                    najboljsa_poteza = None
                    vrednost_najboljse = -Alpha_Beta.NESKONCNO
                    for (i, j) in self.igra.veljavne_poteze():
                        self.igra.povleci(i, j)
                        vrednost = self.alphabeta(globina-1, not maksimiziramo, alpha, beta)[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = (i, j)
                        if vrednost > a:
                            a = vrednost
                        if b <= a:
                            break
                    return (najboljsa_poteza, vrednost_najboljse)

                else:
                    a = alpha
                    b = beta
                    najboljsa_poteza = None
                    vrednost_najboljse = Alpha_Beta.NESKONCNO
                    for (i, j) in self.igra.veljavne_poteze():
                        self.igra.povleci(i, j)
                        vrednost = self.alphabeta(globina-1, not maksimiziramo, alpha, beta)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = (i, j)
                        if vrednost < b:
                            b = vrednost
                        if b < a:
                            break
                    return (najboljsa_poteza, vrednost_najboljse)

                assert (najboljsa_poteza is not None), "alfa-beta: izračunana poteza je None"
        else: assert False, "alfa-beta: nedefinirano stanje igre"



######################################################################
## Uporabniški vmesnik

class Gui():

    def __init__(self, master, globina):
        self.igralec_1 = None
        self.igralec_2 = None
        self.igra = None
        self.zadnja = None

        master.protocol("WM_DELETE_WINDOW", lambda: self.zapri_okno(master))

        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu)

        # Podmenu za izbiro igralcev
        menu_igra = tkinter.Menu(menu)
        menu_igralci = tkinter.Menu(menu)
        menu_clo_rac = tkinter.Menu(menu_igralci)
        menu_rac_clo = tkinter.Menu(menu_igralci)
        menu_rac = tkinter.Menu(menu_igralci)

        menu.add_cascade(label="Igra", menu=menu_igra)
        menu_igra.add_command(label="Nova igra", command=lambda: self.zacni_igro(self.igralec_1, self.igralec_2))
        menu_igra.add_command(label="Razveljavi", command=self.razveljavi_potezo)
        menu_igra.add_separator()
        menu_igra.add_command(label="Izhod", command=master.quit)

        menu.add_cascade(label="Igralci", menu=menu_igralci)
        menu_igralci.add_command(label="1=Človek, 2=Človek", command=lambda: self.zacni_igro(Clovek(self), Clovek(self)))
        menu_igralci.add_cascade(label="1=Človek, 2=Računalnik", menu=menu_clo_rac) ##
        menu_igralci.add_cascade(label="1=Računalnik, 2=Človek", menu=menu_rac_clo) ##     command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)), Clovek(self)))
        menu_igralci.add_cascade(label="1=Računalnik, 2=Računalnik", menu=menu_rac) ## command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)), Racunalnik(self, Minimax(globina))))

        menu_clo_rac.add_command(label="Algoritem Minimax", command=lambda: self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina))))
        menu_clo_rac.add_command(label="Algoritem Alfa-Beta", command=lambda: self.zacni_igro(Clovek(self), Racunalnik(self, Alpha_Beta(globina))))
        menu_rac_clo.add_command(label="Algoritem Minimax", command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)), Clovek(self)))
        menu_rac_clo.add_command(label="Algoritem Alfa-Beta", command=lambda: self.zacni_igro(Racunalnik(self, Alpha_Beta(globina)), Clovek(self)))
        menu_rac.add_command(label="1=Algoritem Minimax, 2=Algoritem Minimax", command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)), Racunalnik(self, Minimax(globina))))
        menu_rac.add_command(label="1=Algoritem Minimax, 2=Algoritem Alfa-Beta", command=lambda: self.zacni_igro(Racunalnik(self, Minimax(globina)), Racunalnik(self, Alpha_Beta(globina))))
        menu_rac.add_command(label="1=Algoritem Alfa-Beta, 2=Algoritem Minimax", command=lambda: self.zacni_igro(Racunalnik(self, Alpha_Beta(globina)), Racunalnik(self, Minimax(globina))))
        menu_rac.add_command(label="1=Algoritem Alfa-Beta, 2=Algoritem Alfa-Beta", command=lambda: self.zacni_igro(Racunalnik(self, Alpha_Beta(globina)), Racunalnik(self, Alpha_Beta(globina))))

        


        # Katera pika
        self.pozicija_prve = None

        # Napis, ki prikazuje stanje igre
        self.napis = tkinter.StringVar(master, value="IGRALEC 1")
        self.napis1 = tkinter.StringVar(master, value="Na potezi je ")
        tkinter.Label(master, textvariable=self.napis1, font=("Times", 13)).grid(row=0, column=0, sticky="e")
        self.label_igralec = tkinter.Label(master, font=("Times", 13), textvariable=self.napis, fg="blue")
        self.label_igralec.grid(row=0, column=1, sticky="w")
        
        # Igralno območje
        self.plosca = tkinter.Canvas(master, width=600, height=600)
        self.plosca.grid(row=2, column=0, columnspan=2)

        # Navodila za igro
        self.navodila = tkinter.Message(master, width=500, font=("Times", 12), text="Cilj igre je nasprotnika prisiliti, da s svojo barvo nariše trikotnik, katerega oglišča predstavljajo pike, ki so prikazane na zaslonu. Igralec črto povleče s klikom na piki, ki ju želi povezati. Če dvakrat označi isto piko, se izbira razveljavi.")
        self.navodila.grid(row=3, column=0, columnspan=2)
        
        # Pike na igralnem polju
        # XXX tukaj je zapečeno število 6, to se spremeni v eno zanko
        self.plosca.create_oval(290,105,310,85,tags="pika0", fill="black")
        self.plosca.create_oval(440,210,460,190,tags="pika1", fill="black")
        self.plosca.create_oval(440,410,460,390,tags="pika2", fill="black")
        self.plosca.create_oval(290,515,310,495,tags="pika3", fill="black")
        self.plosca.create_oval(140,410,160,390,tags="pika4", fill="black")
        self.plosca.create_oval(140,210,160,190,tags="pika5", fill="black")

        self.plosca.tag_bind("pika0","<Button-1>",func=self.pika_klik(0))
        self.plosca.tag_bind("pika1","<Button-1>",func=self.pika_klik(1))
        self.plosca.tag_bind("pika2","<Button-1>",func=self.pika_klik(2))
        self.plosca.tag_bind("pika3","<Button-1>",func=self.pika_klik(3))
        self.plosca.tag_bind("pika4","<Button-1>",func=self.pika_klik(4))
        self.plosca.tag_bind("pika5","<Button-1>",func=self.pika_klik(5))

        # Prični z izbiro igralcev
        self.zacni_igro(Clovek(self), Clovek(self))


    def zacni_igro(self, igralec_1, igralec_2):
        """Nastavi stanje igre na zacetek igre."""
        self.napis1.set("Na potezi je ")
        self.napis.set("IGRALEC 1")
        self.barva = "blue"
        self.prekini_igralce()
        self.plosca.delete("crta", "slika")
        self.igra = Igra()
        if (igralec_1, igralec_2) == (None, None):
            self.igralec_1 = Clovek(self)
            self.igralec_2 = Clovek(self)
        else:
            self.igralec_1 = igralec_1
            self.igralec_2 = igralec_2
        self.igralec_1.igraj()

    def koncaj_igro(self, trojica):
        """Nastavi stanje igre na konec igre."""
        barva = ["blue", "red"][trojica[1] - 1]
        self.narisi_crto(trojica[2][0], trojica[2][1], barva, 10)
        self.narisi_crto(trojica[2][1], trojica[2][2], barva, 10)
        self.narisi_crto(trojica[2][0], trojica[2][2], barva, 10)
        self.napis1.set("Izgubil je ")
        self.napis.set("IGRALEC {}".format(trojica[1]))
        barva = ["blue", "red"][trojica[1] - 1]
        self.label_igralec.configure(fg=barva)
        self.image = tkinter.PhotoImage(file="gamedog.gif")
        self.plosca.after(3000, self.narisi_koncno)
        ##self.plosca.create_image(300, 300, image=self.image, tags="slika")

    def narisi_koncno(self):
        self.plosca.create_image(300, 300, image=self.image, tags="slika")
        

    def prekini_igralce(self):
        """Sporoči igralcem, da morajo nehati razmišljati."""
        logging.debug ("prekinjam igralce")
        if self.igralec_1: self.igralec_1.prekini()
        if self.igralec_2: self.igralec_2.prekini()

    def zapri_okno(self, master):
        """Ta metoda se pokliče, ko uporabnik zapre aplikacijo."""
        # Vlaknom, ki tečejo vzporedno, je treba sporočiti, da morajo
        # končati, sicer se bo okno zaprlo, aplikacija pa bo še vedno
        # delovala.
        self.prekini_igralce()
        # Dejansko zapremo okno.
        master.destroy()

    def narisi_crto(self, prva_pika, druga_pika, barva, debelina=5):
        pike = [[300, 95],
                [450, 200],
                [450, 400],
                [300, 505],
                [150, 400],
                [150, 200]]
        x0, y0 = pike[prva_pika][0], pike[prva_pika][1]
        x1, y1 = pike[druga_pika][0], pike[druga_pika][1]
        a = min(prva_pika, druga_pika)
        b = max(prva_pika, druga_pika)
        self.plosca.create_line(x0, y0, x1, y1, fill=barva, width=debelina, state="disabled", tags=("crta", "crta{0}{1}".format(a, b)))
        self.plosca.tag_lower("crta")

    def pika_klik(self, pozicija):
        def pomozna(event):
            if self.igra.na_potezi == IGRALEC_1:
                self.igralec_1.klik(pozicija)
            elif self.igra.na_potezi == IGRALEC_2:
                self.igralec_2.klik(pozicija)
        return pomozna

    def povleci_potezo(self, pozicija):
        """Shrani pozicijo prve pike in povlece potezo, ce je ta ze shranjena."""
        igralec = self.igra.na_potezi
        if self.pozicija_prve == None:
            oznaka = "pika{}".format(pozicija)
            self.pozicija_prve = pozicija
            self.plosca.itemconfig(oznaka, fill="grey")
        elif self.igra.je_veljavna(self.pozicija_prve, pozicija):
            oznaka = "pika{}".format(self.pozicija_prve)
            self.plosca.itemconfig(oznaka, fill="black")
            r = self.igra.povleci(self.pozicija_prve, pozicija)
            if r:
                barva = ["blue", "red"][igralec - 1]
                self.narisi_crto(self.pozicija_prve, pozicija, barva)
            if r[0]:
                self.koncaj_igro(r)
            else:
                self.napis.set("IGRALEC {}".format(self.igra.na_potezi))
                barva = ["blue", "red"][self.igra.na_potezi - 1]
                self.label_igralec.configure(fg=barva) 
                if self.igra.na_potezi == IGRALEC_1:
                    self.igralec_1.igraj()
                elif self.igra.na_potezi == IGRALEC_2:
                    self.igralec_2.igraj()
                else:
                    assert False, "Na potezi ni noben igralec"
            self.pozicija_prve = None
        else:
            oznaka = "pika{}".format(self.pozicija_prve)
            self.plosca.itemconfig(oznaka, fill="black")
            self.pozicija_prve = None

    def razveljavi_potezo(self):
        (i, j) = self.igra.zgodovina_pik.pop()
        i, j = min(i, j), max(i, j)
        self.igra.razveljavi()
        self.igra.polje[i][j], self.igra.polje[j][i] = PRAZNO, PRAZNO
        self.plosca.delete("crta{0}{1}".format(i, j))
        self.napis.set("IGRALEC {}".format(self.igra.na_potezi))
        barva = ["blue", "red"][self.igra.na_potezi - 1]
        self.label_igralec.configure(fg=barva)







######################################################################
## Glavni program

if __name__ == "__main__":

    # Opišemo argumente, ki jih sprejmemo iz ukazne vrstice
    parser = argparse.ArgumentParser(description="Igrica Sim")
    # Argument --globina n, s privzeto vrednostjo PRIVZETA_GLOBINA
    parser.add_argument("--globina",
                        default=PRIVZETA_GLOBINA,
                        type=int,
                        help="globina iskanja za minimax algoritem")
    # Argument --debug, ki vklopi sporočila o tem, kaj se dogaja
    parser.add_argument("--debug",
                        action="store_true",
                        help="vklopi sporočila o dogajanju")

    # Obdelamo argumente iz ukazne vrstice
    args = parser.parse_args()

    # Vklopimo sporočila, če je uporabnik podal --debug
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)


    root = tkinter.Tk()
    root.title("Sim")
    aplikacija = Gui(root, args.globina)
    root.mainloop()
