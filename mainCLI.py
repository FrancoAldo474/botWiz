from source.controller.controller import Controller
import os
import shutil
import json
from tkinter import Tk, filedialog

def scegli_video():
    # Usa tkinter per scegliere un file video
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Seleziona un video", filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    return file_path

# MAIN
if __name__ == "__main__":
    video = scegli_video()
    if not video:
        print("❌ Nessun video selezionato. Uscita.")
        exit()
    print("\n--- INSERISCI I DATI DELL'ATLETA ---\n")
    nome = input("Nome: ")
    cognome = input("Cognome: ")
    data_nascita = input("Data di nascita (gg/mm/aaaa): ")
    altezza = float(input("Altezza (cm): "))
    peso = float(input("Peso (kg): "))
    
    ruoli = ["playmaker", "guard", "small forward", "big forward", "center"]
    print("\nRuoli disponibili:")
    for i, ruolo in enumerate(ruoli):
        print(f"{i + 1}. {ruolo}")
    
    ruolo_idx = int(input("Scegli il numero corrispondente al ruolo: ")) - 1
    ruolo = ruoli[ruolo_idx]

    mano_tiro = input("Mano dominante (destra/sinistra): ").lower()
    Controller.onAnalize(video, nome,cognome,peso,altezza,data_nascita,ruolo,mano_tiro)
