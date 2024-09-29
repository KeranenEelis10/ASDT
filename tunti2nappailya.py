import tkinter as tk
import winsound

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ikkuna=tk.Tk()

ikkuna.geometry("300x900+500+300")

markkerin_x_koordinaatti=10


#Toimintoja

def toiminto():
    print("Heihei")

def tuota_aani():
    global markkerin_x_koordinaatti
    markkerin_x_koordinaatti=markkerin_x_koordinaatti+1
    markkeri.place(x=markkerin_x_koordinaatti, y=500)
    winsound.Beep(440,220)

def tuota_aani_2():
    winsound.Beep(500,500)
    for i in range(10):
        tuota_aani()

def toiminto2():
    print("Lopeta heti")


#Osioita

tekstijuttu=tk.Label(ikkuna,text="Ensimmäinen tkinterUI")
tekstijuttu.place(x=10, y=30)

markkeri=tk.Label(ikkuna, text="B")
markkeri.place(x=markkerin_x_koordinaatti, y=500)

painike=tk.Button(ikkuna, text="Aja toiminto", command=toiminto)
painike.place(x=10, y=60)

painike_aani=tk.Button(ikkuna, text="Kuulen ääniä", command=tuota_aani)
painike_aani.place(x=100,y=60)

painike_3=tk.Button(ikkuna, text="Lopeta", command=toiminto2)
painike_3.place(x=100,y=90)

painike_4=tk.Button(ikkuna, text="Hätä Seis", command=tuota_aani_2)
painike_4.place(x=100,y=120)

#Kuvien plottaus

#Luodaan kuvaaja:

fig=Figure(figsize=(5,4), dpi=100)
ax=fig.add_subplot(111)
ax.plot(1,1,'b+')

#Upotetaan kuvaaja TkInteriin

kuvaaja_canvas=FigureCanvasTkAgg()

ikkuna.mainloop(fig, master=ikkuna)
kuvaaja_canvas.draw()
kuvaaja_canvas.get_tk_widget().place(x=20, y=160)