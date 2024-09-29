# Tehtäväm ongelmanratkaisussa käytetty tekoälyä
# Kirjoitin myös lopuksi koodin puhtaaksi tekoälyllä

import tkinter as tk  # Käyttöliittymä
import threading  # Säikeet
import time  # Aika
import winsound  # Äänet
import random  # Hain syönti

# Pääikkuna
ikkuna = tk.Tk()  #Ikkunan alustus
ikkuna.title("Ernestin ja Kernestin pako")  # Ikkunan otsikko
ikkuna.geometry("600x400")  # Ikkunan koko

# Visualisoidaan saari ja mantere
Canvas = tk.Canvas(ikkuna, width=600, height=400)  # Piirtoalusta
Canvas.pack()  # Pakataan piirtoalusta

# Piirretään saari 
saari =Canvas.create_oval(50, 150, 150, 250, fill="yellow", outline="black", width=2)  # Ympyrän muotoinen saari
Canvas.create_text(100, 270, text="Saari", font=("TimesNewRoman", 12, "bold"))  # Teksti saaren alle

# Piirretään manner
Canvas.create_rectangle(480, 10, 600, 400, fill="grey", outline="black", width=2)  # Suorakulmion muotinen manner
Canvas.create_text(540, 320, text="Mainland", font=("TimesNewRoman", 12, "bold"))  # Teksti mantereen alle

# Määritellään molempien oma viesti
ernestiViesti = ["Ernesti", "Kernesti", "täällä", "olemme", "autiolla", "saarella", "haakisirikkoutuneina", "lähettäkää", "apua", "kiitos"]  # Ernesti
kernestiViesti = ["Kernesti", "Ernesti", "tarvitsemme", "pelastusta", "lähettäkää", "apua", "autiolle", "saarelle", "mahdollisimman", "pian"]  # Kernesti

# Luodaan Pohteri ja Eteteri seuraamaan sanoja
pohteriSanat = set()  # Seurataan Ernestiä
eteteriSanat = set()  # Seurataan Kernestiä

# Pelastusalus
pelastusAlus = None  

# Tehdään rajat joiden mukaan pelastusalus pysähtyy
saari_x_stop = 150  # X-koordinaatti kertoo paljon alus liikkuu x-akselilla
saari_pohteri_y = 170  # Y-koordinaatti alukselle jos ernesti sai sanat perille ensin
saari_eteteri_y = 230  # Y-koordinaatti alukselle jos kernesti sai sanat perille ensin

# Apinaluokka jossa annetaan apinalle yksi sana
class apina:
    def __init__(self, nimi, sana, color, aloitusYkoordinaatti):
        self.nimi = nimi  # Apinan nimi eli Ernesti tai Kernesti
        self.sana = sana  # Apinan mukana oleva sana
        # Alustetaan apinan aloituspaikan x-koordinaatti ja luodaan ympyrän muotoinen apina
        self.muoto = Canvas.create_oval(85, aloitusYkoordinaatti, 115, aloitusYkoordinaatti + 30, fill=color)  
        self.aloitusYkoordinaatti = aloitusYkoordinaatti  # Apinan aloituspaikan y-koordinaatti

# Luodaan äänet
def uintiÄäni():
    winsound.Beep(800, 100)  # Ääni jokaiselle askeleelle kun apina etenee

def hukkumisÄäni():
    winsound.Beep(400, 300)  # Ääni kun apina syödään

def saapumisÄäni():
    winsound.Beep(1500, 300)  # Ääni kun apina tulee perille

# Ernestin ja Kernestin iloiset äänet kun pelastusalus saapuu
def ernestiHuuto():
    winsound.Beep(1200, 500)  
    winsound.Beep(1400, 500)  

def kernestiHuuto():
    winsound.Beep(1000, 500)  
    winsound.Beep(800, 500)  

# Luodaan apinan uiminen käyttäen säikeitä
def liikutaApinaa(apina_obj, success_callback):
    def ui():
        for step in range(100):  # Liikutaan sata askelta
            Canvas.move(apina_obj.muoto, 4, 0)  # Liikutaan itään päin
            uintiÄäni()  # Soitetaan ääni jokaisella askelella

            # Luodaan random mahdollisuus joutua hain syömäksi
            if random.random() < 0.01:  # 1% mahdollisuus
                hukkumisÄäni()  # Soitetaan ääni jos apina syödään
                print(f"{apina_obj.nimi} on syöty hain toimesta!")  # Tulostetaan terminaaliin jos apina syödään
                return  # Apinan uinti loppuu jos se syödään

            ikkuna.update()  # Päivitetään Tkinter-ikkuna
            time.sleep(0.1)  # Pysäytetään apina 100 ms välein simuloimaan uintia

        saapumisÄäni()  # Soitetaan saapumisääni kun apina saapuu mantereelle
        print(f"{apina_obj.nimi} on saapunut sanalla: {apina_obj.sana}")  # Tulostetaan terminaaliin
        success_callback(apina_obj.sana)  # Kutsutaan onnistumiskutsua 

    # Suoritetaan uinti erillisessä säikeessä, jotta käyttöliittymä ei jumiudu
    threading.Thread(target=ui).start()

# Tarkistetaan onko Pohteri tai Eteteri saanut 10 ainutlaatuista sanaa
def tarkistaPelastus():
    if len(pohteriSanat) >= 10:  # Tarkistetaan Pohterin sanoja
        print("Pohteri on saanut 10 ainutlaatuista sanaa! Lähetetään pelastusalus!")  # Ilmoitetaan pelastusalus terminaaliin
        lahetaPelastusAlus("pohteri")  # Lähetetään pelastusalus Pohterille
    elif len(eteteriSanat) >= 10:  # Tarkistetaan Eteterin sanat
        print("Eteteri on saanut 10 ainutlaatuista sanaa! Lähetetään pelastusalus!")  # Ilmoitetaan pelastusalus terminaaliin
        lahetaPelastusAlus("eteteri")  # Lähetetään pelastusalus Eteterille

# Pelastuslaivan lähetys
def lahetaPelastusAlus(winner):
    global pelastusAlus  

    # Luodaan pelastusaluksen lähtöpaikka
    if pelastusAlus is None:  # Pelastusalus luodaan vain kerran
        pelastusAlus = Canvas.create_rectangle(500, 180, 530, 210, fill="blue", outline="black", width=2)  

    def liikutaAlusta():
        while True:  # Toistetaan niin kauan kuin laiva liikkuu
            ship_coords = Canvas.coords(pelastusAlus)  # Haetaan pelastuslaivan nykyiset koordinaatit
            x, y = ship_coords[0], ship_coords[1]  # Poimitaan laivan x- ja y-koordinaatit (vasen yläkulma)

            if x <= saari_x_stop:  # Tarkistetaan, onko alus saaren kohdalla (x-asento)
                print(f"Pelastusalus on pysähtynyt saarelle {winner.capitalize()}'s tiimille!")  # Ilmoitetaan aluksen pysähtymisestä

                # Soitetaan iloinen ääni voittajalle
                if winner == "pohteri":
                    ernestiHuuto()  # Soitetaan iloinen ääni Ernesti
                else:
                    kernestiHuuto()  # Soitetaan iloinen ääni Kernesti

                return  # Lopetetaan alus

            # Liikuttaminen voittajan mukaan
            if winner == "pohteri":
                Canvas.move(pelastusAlus, -4, -0.5)  # Liikuta alusta vinosti ylös saareen (Pohterin puolelle)
            else:
                Canvas.move(pelastusAlus, -4, 0.5)  # Liikuta alusta vinosti alas saareen (Eteterin puolelle)

            ikkuna.update()  # Päivitetään Tkinter-ikkuna
            time.sleep(0.1)  # Viivästys aluksen liikuttamiseksi

    # Suoritetaan aluksen liikuttaminen omassa säikeessä
    threading.Thread(target=liikutaAlusta).start()

# Luodaan funktio napeille joka lähettää apinat
def lahetaApina(person):
    # Valitaan sanat apinoille henkilön mukaan
    message_list = ernestiViesti.copy() if person == 'ernesti' else kernestiViesti.copy()  # Kopioidaan sanat
    apina_color = "#D2B48C" if person == 'ernesti' else "#8B4513"  # Määritetään apinan väri
    aloitusYkoordinaatti = 170 if person == 'ernesti' else 200  # Määritetään apinan aloituspaikan y-koordinaatti
    successful_sanas = pohteriSanat if person == 'ernesti' else eteteriSanat  # Jos apina pääsee perille annetaan sana Pohterille/eterille

    # Funktio joka lähettää yhden apinan ja tarkistaa mitä sanoja pitää vielä lähettää
    def send_single_apina():
        if message_list:  # Tarkistetaan mikä on seuraava sana joka täytyy lähettää
            sana = message_list.pop(0)  # Haetaan seuraava sana ja poistetaan sana että seuraava ei saa samaa
            apina_obj = apina(f"{person.capitalize()}'s apina", sana, apina_color, aloitusYkoordinaatti)  # Luodaan apina
            print(f"{apina_obj.nimi} kantaa sanaa: {apina_obj.sana}")  # Tulostetaan terminaaliin mitä sanaa apina vie
            liikutaApinaa(apina_obj, lambda sana: successful_sanas.add(sana))  

    # Lähetetään apinoita kymmenen kerralla
    for _ in range(10):
        send_single_apina()  # Eli lähetään yksittäisiä kymmenen yhtäaikaa

    # Tarkistetaan, voivatko joko Pohteri tai Eteteri lähettää pelastuksen kymmenen apinan jälkeen
    ikkuna.after(5000, tarkistaPelastus)  # Annetaan aikaa apinoiden saapua, tarkistetaan pelastusolot

# Nappi apinoiden lähettäömiseen
ernesti_button = tk.Button(ikkuna, text="Ernesti lähettää apinoita", command=lambda: lahetaApina('ernesti'))  # Napin luominen Ernesti
ernesti_button.pack(side=tk.LEFT, padx=20, pady=20)  # Laitetaan nappi vasemmalle

kernesti_button = tk.Button(ikkuna, text="Kernesti lähettää apinoita", command=lambda: lahetaApina('kernesti'))  # Napin luominen Kernesti
kernesti_button.pack(side=tk.RIGHT, padx=20, pady=20)  # Laitetaan nappi oikealle


ikkuna.mainloop()  
