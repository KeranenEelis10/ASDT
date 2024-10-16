import tkinter as tk
from tkinter import messagebox  
import random  
import numpy as np 
import time  
import threading 
import pygame  

# Apina classi
class ApinaSaariSimulator:
    def __init__(self, master):
        #Alustetaan pääikkuna
        self.master=master
        self.master.title("Apina Saari Simulator")
        
        pygame.mixer.init()
        
        #Canvas
        self.canvas = tk.Canvas(master,width=600,height=400,background='blue')  
        self.canvas.pack()
        
        # Listat
        self.islands = []  
        self.monkeys = []  
        
        #Tulivuorinappi
        self.create_volcano_button = tk.Button(master, text="Tulivuorenpurkaus", command=self.saari)
        self.create_volcano_button.pack()
        
        #Tyhjennä meri nappi
        self.clear_button = tk.Button(master, text="Tyhjennä meri", command=self.tyhjenna)
        self.clear_button.pack()
        
        #Apinat uimaan nappi
        self.swim_button = tk.Button(master, text="Lähetä apinat uimaan", command=self.apinaUimaan)
        self.swim_button.pack()
    
    #Saari funktio
    def saari(self):
        #Infoboksi jos saaria on jo kymmenen
        if len(self.islands) >= 10:
            messagebox.showinfo("Info", "Meri on täynnä saaria!")
            return
        
        #Luodaan saari random paikalle
        attempts = 0
        while attempts < 100:
            x = random.randint(50, 550)  #Random x koord
            y = random.randint(50, 350)  #Random y koord
            
            if not self.paalekkaisyys(x, y):
                break
            attempts += 1
        
        #Luovutetaan jos sata kertaa yritetään ja aina osuu toisen saaren päälle
        if attempts == 100:
            print("Failed to find a place")
            return
        
        #Tehdään saari
        island = self.canvas.create_oval(x-20,y-20,x+20,y+20,fill='green')
        self.islands.append(island)  #Lisää saari listaan
        
        print(f"Created island at ({x}, {y})")
        
        #Tulivuori ääni
        self.tulivuoriAani()
        
        #10 apinaa saarelle
        for i in range(10):
            self.lisaaApina(x, y)
    
    #Funktio joka tarkistaa onko saari toisen päällä
    def paalekkaisyys(self, x, y):
        for island in self.islands:
            coords = self.canvas.coords(island)  # Haetaan koordinaatit
            
            if (coords[0]<=x<=coords[2] and coords[1]<=y<=coords[3]):
                return True
        return False
    
    #Lisätään apina saareen funktio
    def lisaaApina(self, island_x, island_y):
        #Laitetaan apina random kohtaan saaressa
        monkeyx = island_x + random.randint(-15, 15)
        monkeyy = island_y + random.randint(-15, 15)
        #Ruskea pallo kuvastamaan apinaa
        monkey = self.canvas.create_oval(monkeyx-2,monkeyy-2,monkeyx+2,monkeyy+2,fill='brown')
        self.monkeys.append(monkey)  #Laitetaan apina listaan
        print(f"Added monkey at ({monkeyx}, {monkeyy})")
        
        #Säikeytetään apinan elämä
        thread = threading.Thread(target=self.apinaElama, args=(monkey,))
        thread.daemon = True  # Säie lopetetaan, kun ohjelma suljetaan
        thread.start()
    
    #Apinan elinkaari funktio
    def apinaElama(self, monkey):
        monkey_frequency = random.randint(400, 2000)  #Joka apinalle oma ääni
        while True:
            time.sleep(10)  #10 s välein apina pitää ääntä tai kuolee
            if random.random() < 0.01:  #1 pros mahdollisuus kuolla nauruun
                self.nauruAani()  #Nauruääni
                self.canvas.delete(monkey)  #Apina pois canvasilta
                self.monkeys.remove(monkey)  #Apina pois listasta
                print("A monkey died from laughter!")
                break
            else:
                self.play_monkey_sound(monkey_frequency)  #Apinaääni
    
    #Apinat laitetaan uimaan funktio
    def apinaUimaan(self):
        for monkey in self.monkeys[:]:  
            if random.random() < 0.5:  #50 pros todennäköisyydellä apina lähtee uimaan
                self.canvas.itemconfig(monkey, fill='blue')  #Muutetaan apina siniseksi uimisen merkiksi
                thread = threading.Thread(target=self.apinaUimassa, args=(monkey,))
                thread.daemon = True  
                thread.start()
    
    #Apinan uiminen funktio
    def apinaUimassa(self, monkey):
        while True:
            time.sleep(1)  #Tarkistetaan joka sekunti
            if random.random() < 0.01:  #1 pros mahollisuus että hai syö apinan
                self.haiAani()  #Hai ääni
                self.canvas.delete(monkey)  #Apina pois canvasilta
                self.monkeys.remove(monkey)  #Apina pois listasta
                print("A monkey was eaten by a shark!")
                break
    
    #Tulivuori ääni
    def tulivuoriAani(self):
        frequency = 100  
        duration = 1.0  
        self.aanet(frequency, duration)
    
    #Nauru ääni
    def nauruAani(self):
        frequency = 1000  
        duration = 0.5  
        self.aanet(frequency, duration)
    
    #Hain ääni
    def haiAani(self):
        frequency = 200  
        duration = 0.7  
        self.aanet(frequency, duration)
    
    #APinan ääni
    def play_monkey_sound(self, frequency):
        duration = 0.3  
        self.aanet(frequency, duration)
    
    #Äänen luomis funktio
    def aanet(self, frequency, duration):  
        sample_rate = 44100  #Äänentaajuus
        t = np.linspace(0, duration, int(sample_rate * duration), False)  
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Aaltofunktio muodostaa äänen
        audio = np.int16(wave * 32767)  # Muutetaan ääni 16-bittiseksi
        
        try:
            sound = pygame.mixer.Sound(audio)  #Luodaan ääni käyttäen pygame
            sound.play()  #Toistetaan ääni
        except Exception as e:
            print(f"Error playing sound: {e}")  
    
    #Clear funktio
    def tyhjenna(self):
        #Poistetaan kaikki 
        for island in self.islands:
            self.canvas.delete(island)
        self.islands.clear()
        
        #Poistetaan canvasilta kaikki ja poistetaan listat
        for monkey in self.monkeys:
            self.canvas.delete(monkey)
        self.monkeys.clear()
        
        print("Cleared all islands and monkeys")


if __name__ == "__main__":
    root = tk.Tk()  
    app = ApinaSaariSimulator(root)  
    root.mainloop()  
