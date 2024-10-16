#Käytin koodin ongelmanratkaisussa tekoälyä apuna
#Lisäksi kirjoitin koodin puhtaaksi tekoälyn avulla
import tkinter as tk
import threading
import numpy as np
import time
import random
from math import pi, cos, sin


# Saari classi
class SaariSimu:
    def __init__(self):
        #Pääikkuna
        self.juuri = tk.Tk()
        self.juuri.title("Saari ja uima-allas")
        
        #Alustetaan matriisit uima-altaalle ja ojille
        self.allas_matriisi = np.zeros((20, 60))  # Uima-allas matriisi
        self.oja_ernesti = np.ones(100)      # Ernestin oja
        self.oja_kernesti = np.ones(100)     # Kernestin oja
        
        #Tehdään canvas
        self.piirtoalue = tk.Canvas(self.juuri, width=1000, height=800, bg='#1e90ff')
        self.piirtoalue.pack(pady=10)
        
        #Näytetään kaivuu edistyminen
        self.labelikehys = tk.Frame(self.juuri)
        self.labelikehys.pack(fill=tk.X, padx=20)
        
        self.ernesti_edistyminen = tk.Label(self.labelikehys, text="Ernestin oja: 0% kaivettu", 
                                       font=('Arial', 12), fg='#2c3e50')
        self.ernesti_edistyminen.pack(side=tk.LEFT, padx=20)
        
        self.kernesti_edistyminen = tk.Label(self.labelikehys, text="Kernestin oja: 0% kaivettu",
                                        font=('Arial', 12), fg='#2c3e50')
        self.kernesti_edistyminen.pack(side=tk.RIGHT, padx=20)
        
        #Apinoiden hallinta
        self.apinat = []  #Lista apinoista
        self.apina_lukko = threading.Lock()  #Lukko säikeille
        self.aktiiviset_kaivajat = {"Ernesti": [], "Kernesti": []}  #Aktiiviset kaivajat
        self.kaivaus_asemat = {"Ernesti": {}, "Kernesti": {}}  #Kaivajien sijainnit
        
        #Tehdään napit
        self.luo_napit()
        
        #Piirretään saari
        self.piirra_saarimaisema()
        self.luo_metsa_apinat(15)  #Luodaan apinat metsään
        
        # Käynnistä animaatio
        self.animaatio()

    #Tehdään käyttöliittymän napit
    def luo_napit(self):
        nappi_kehys = tk.Frame(self.juuri)
        nappi_kehys.pack(pady=10)
        
        # Ernestin napit
        ernesti_kehys = tk.Frame(nappi_kehys)
        ernesti_kehys.pack(side=tk.LEFT, padx=20)
        
        tk.Button(ernesti_kehys, text="Hae Apina\n(Ernesti)", 
                  command=lambda: self.hae_apina("Ernesti"),
                  foreground='black',background='white', height=2, width=20, font=('TimesNewRoman', 12),).pack(side = tk.LEFT)
        
        tk.Button(ernesti_kehys, text="Aloita Kaivuu\n(Ernesti)", 
                  command=lambda: self.aloita_kaivuu("Ernesti"),
                  background='white', foreground='black',  height=2, width=20,font=('TimesNewRoman', 12)).pack(side = tk.LEFT)
        
        # Kernestin napit
        kernesti_kehys = tk.Frame(nappi_kehys)
        kernesti_kehys.pack(side=tk.LEFT, padx=20)
        
        tk.Button(kernesti_kehys, text="Hae Apina\n(Kernesti)", 
                  command=lambda: self.hae_apina("Kernesti"),
                  background='white',foreground='black',  height=2, width=20,font=('TimesNewRoman', 12)).pack( side=tk.LEFT)
        
        tk.Button(kernesti_kehys, text="Aloita Kaivuu\n(Kernesti)", 
                  command=lambda: self.aloita_kaivuu("Kernesti"),
                  background='white', foreground='black', height=2, width=20,font=('TimesNewRoman', 12)).pack(side=tk.LEFT)

    #Piirretään saaren sisälle tarvittavat asiat
    def piirra_saarimaisema(self):
        #Piirretään saari
        self.piirtoalue.create_oval(150, 150, 850, 650, fill='yellow', outline='yellow', width=3  )
        
        #Piirretään uima-allas
        self.allasx1, self.allasy1 = 400, 350
        self.allasx2, self.allasy2 = 600, 450
        self.piirtoalue.create_rectangle(self.allasx1, self.allasy1, self.allasx2, self.allasy2,
                                   fill='blue', outline='blue')
        
        #Piirretään ojat
        self.piirra_oja("Ernesti", self.allasx1 + 50, self.allasy1)
        self.piirra_oja("Kernesti", self.allasx2 - 50, self.allasy1)
        
        #Piirretään metsän pohja
        self.piirra_metsa()

    # Metsän piirto omana funktiona että saatiin se hyvään kohtaan ja ympyrän muotoisena
    def piirra_metsa(self):
        metsax, metsay = 250, 400
        
        self.piirtoalue.create_oval(metsax-80, metsay-80, metsax+80, metsay+80,
                              fill='green', outline='darkgreen', width=2, tags='metsa')

    # Ojien piirto
    def piirra_oja(self, omistaja, x, y):
        ojan_pituus = 200  #Ojan pituus
        ojan_leveys = 20   #Ojan leveys
        
        # allennetaan ojan sijaintitiedot
        oja_data = {
            "x": x,
            "y": y,
            "pituus": ojan_pituus,
            "leveys": ojan_leveys,
            "alku_y": y,
            "loppu_y": y - ojan_pituus
        }
        
        setattr(self, f'oja_{omistaja.lower()}_data', oja_data)
        
        #Tehdään ojan visuaalinen ilme
        self.piirtoalue.create_rectangle(x - ojan_leveys/2, y - ojan_pituus,
                                   x + ojan_leveys/2, y,
                                   fill='#e3d9c6', outline='#7f8c8d', tags=f'oja_{omistaja.lower()}')

    #Apinoiden luonti metsään random paikkoihin funktio
    #Tämä idea tullu tekoälyltä ja pidin sen koska se oli hauska yksityiskohta
    def luo_metsa_apinat(self, maara):
        metsax, metsay = 250, 400
        
        #Luodaan satunnaisuus apinoiden sijainnille
        for i in range(maara):
            kulma = random.uniform(0, 2*pi)  # Satunnainen kulma
            s = random.uniform(20, 60)  # Satunnainen etäisyys keskipisteestä
            x = metsax + s * cos(kulma)
            y = metsay + s * sin(kulma)
            
            #Luodaan apina ja lisätään listaan
            apina = {
                'id': i,
                'sijainti': (x, y),
                'haettu': False,
                'omistaja': None,
                'canvas_id': self.piirra_apina(x, y, f'apina_{i}')
            }
            self.apinat.append(apina)

    #Piirretään apina
    def piirra_apina(self, x, y, tagi):
        apina_vari = '#8b4513'
        return self.piirtoalue.create_oval(x-10, y-10, x+10, y+10, fill=apina_vari, outline='black', tags=tagi)

    #Apinan hakeminen ojaan
    def hae_apina(self, omistaja):
        with self.apina_lukko:
            # Tarkistetaan, onko vapaita apinoita
            vapaat_apinat = [apina for apina in self.apinat if not apina['haettu']]
            if not vapaat_apinat:
                self.soita_aani('error')
                return
            
            apina = vapaat_apinat[0]  #Otetaan ensimmäinen vapaa apina
            apina['haettu'] = True
            apina['omistaja'] = omistaja
            
            #Haetaan ojan tiedot
            oja_data = getattr(self, f'oja_{omistaja.lower()}_data')
            nykyiset_kaivajat = len(self.aktiiviset_kaivajat[omistaja])
            alku_y = oja_data['alku_y']
            loppu_y = oja_data['loppu_y']
            
            #Määritetään apinan sijainti ojassa
            asema = nykyiset_kaivajat * (alku_y - loppu_y) // 10
            kohde_y = alku_y - asema
            
            #Siirretään apina metsän alueelta ojaan
            self.animoitu_apinan_liike(apina, oja_data['x'], kohde_y)
            self.soita_aani('fetch')
            
            #Tallennetaan kaivausasema
            self.kaivaus_asemat[omistaja][apina['id']] = asema // 2
            self.aktiiviset_kaivajat[omistaja].append(apina)

    #Apinan liikkuminen ojalle
    def animoitu_apinan_liike(self, apina, kohde_x, kohde_y):
        nykyinen_x, nykyinen_y = apina['sijainti']
        askeleet = 50  
        x_askel = (kohde_x - nykyinen_x) / askeleet
        y_askel = (kohde_y - nykyinen_y) / askeleet
        
        for i in range(askeleet):
            nykyinen_x += x_askel
            nykyinen_y += y_askel
            self.piirtoalue.move(apina['canvas_id'], x_askel, y_askel)
            self.piirtoalue.update()
            time.sleep(0.02)
        
        apina['sijainti'] = (kohde_x, kohde_y)

    # Aloita kaivaminen
    def aloita_kaivuu(self, omistaja):
        with self.apina_lukko:
            if self.aktiiviset_kaivajat[omistaja]:
                for apina in self.aktiiviset_kaivajat[omistaja]:
                    threading.Thread(target=self.kaiva_ojaa, args=(apina, self.kaivaus_asemat[omistaja][apina['id']])).start()

    # Kaivaa ojaa
    def kaiva_ojaa(self, apina, alkuasema):
        omistaja = apina['omistaja']
        oja = self.oja_ernesti if omistaja == "Ernesti" else self.oja_kernesti
        edistys_labeli = self.ernesti_edistyminen if omistaja == "Ernesti" else self.kernesti_edistyminen
        
        asema = alkuasema
        viive = 1  # Kaivuun alkuviive
        
        while asema < 100:
            if oja[asema] > 0:  # Kaivetaan vain jos ojaa vielä jäljellä
                time.sleep(viive)  # Kaivuu viive
                with self.apina_lukko:
                    oja[asema] -= 1  # Poistetaan hiekkaa
                    self.paivita_oja_visuaali(omistaja)
                    
                    # Päivitä edistymisprosentti
                    edistys = (sum(oja <= 0) / 100) * 100
                    edistys_labeli.config(text=f"{omistaja}'n oja: {edistys:.1f}% kaivettu")
                    self.soita_aani('dig')
                
                asema += 1
                viive *= 2  # Tuplataan seuraavan metrin kaivuun aika
            else:
                break

    # Päivitä ojan visuaalinen näkymä
    def paivita_oja_visuaali(self, omistaja):
        oja = self.oja_ernesti if omistaja == "Ernesti" else self.oja_kernesti
        oja_data = getattr(self, f'oja_{omistaja.lower()}_data')
        x, y, leveys = oja_data["x"], oja_data["alku_y"], oja_data["leveys"]
        
        # Poistetaan edellinen oja
        self.piirtoalue.delete(f'oja_{omistaja.lower()}')
        
        # Piirretään oja uudestaan
        self.piirra_oja(omistaja, x, y)
        
        for i in range(100):
            if oja[i] <= 0:
                self.piirtoalue.create_rectangle(x - leveys / 2, y - (i + 1),
                                         x + leveys / 2, y - i,
                                         fill='grey', outline='black', tags=f'oja_{omistaja.lower()}')

    # Ääniefektien toisto
    def soita_aani(self, toiminto):
        print(f"Toistetaan ääni: {toiminto}")

    # Animaatio
    def animaatio(self):
        self.juuri.after(100, self.animaatio)

# Käynnistä simulaatio
if __name__ == "__main__":
    simulaatio = SaariSimu()
    simulaatio.juuri.mainloop()
