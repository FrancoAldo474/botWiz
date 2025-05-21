import csv
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
import os
from flask import session


class result:
    def __init__(self,tiro):
        self.tiro=tiro

    def createCSV(self):
        csv_header = [
        "mano_dominante", "angolo_spalla_sx", "angolo_spalla_dx",
        "angolo_anca_sx", "angolo_anca_dx", "angolo_gomito_dx",
        "angolo_gomito_sx", "angolo_ginocchio_sx", "angolo_ginocchio_dx", "fase_tiro"
        ]

        n_frames = len(self.tiro.angoli_spalla_sx)

        # Verifica coerenza lunghezza
        assert all(len(getattr(self.tiro, attr)) == n_frames for attr in [
        "angoli_spalla_dx", "angoli_anca_sx", "angoli_anca_dx",
        "angoli_gomito_dx", "angoli_gomito_sx",
        "angoli_ginocchio_sx", "angoli_ginocchio_dx", "phases"
        ]), "Le liste degli angoli devono avere la stessa lunghezza"

        # Creazione righe CSV
        csv_rows = []
        for i in range(n_frames):
            row = {
            "mano_dominante": self.tiro.mano_dominante,
            "angolo_spalla_sx": self.tiro.angoli_spalla_sx[i],
            "angolo_spalla_dx": self.tiro.angoli_spalla_dx[i],
            "angolo_anca_sx": self.tiro.angoli_anca_sx[i],
            "angolo_anca_dx": self.tiro.angoli_anca_dx[i],
            "angolo_gomito_dx": self.tiro.angoli_gomito_dx[i],
            "angolo_gomito_sx": self.tiro.angoli_gomito_sx[i],
            "angolo_ginocchio_sx": self.tiro.angoli_ginocchio_sx[i],
            "angolo_ginocchio_dx": self.tiro.angoli_ginocchio_dx[i],
            "fase_tiro": self.tiro.phases[i]
            }
            csv_rows.append(row)
        csv_output_path="source/static/result/report_finale.csv"
        os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
        # Scrittura del CSV
        with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_header)
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"CSV salvato in: {csv_output_path}")

    def calcola_statistiche(self,df, colonne_angoli):
        return df.groupby("fase_tiro")[colonne_angoli].agg([
            ("Q1", lambda x: np.percentile(x, 25)),
            ("Mediana", "median"),
            ("Q3", lambda x: np.percentile(x, 75)),
            ("Media", "mean")
        ]).rename_axis(columns=["Angolo", "Statistica"]).sort_index(axis=1)
    """
    def calcola_percentuale_confrontabilita(self,diff, valore_massimo_diff=135):
        somma_diff = diff.sum().sum()
        num_valori = diff.count().sum()
        somma_massima = valore_massimo_diff * num_valori
        confrontabilita = 100 - ((somma_diff / somma_massima) * 100)
        return round(confrontabilita, 2)
    """
    def calcola_percentuale_confrontabilita(self, diff, valore_massimo_diff=135):
        # Calcola la media delle differenze assolute (tutti i valori nel DataFrame diff)
        media_diff = diff.values.mean()
        
        # Calcola la percentuale rispetto al valore massimo atteso
        confrontabilita = 100 - (media_diff / valore_massimo_diff) * 100
        
        # Limita il valore tra 0 e 100
        confrontabilita = max(0, min(100, confrontabilita))
        
        return round(confrontabilita, 2)

    def carica_frasi(self,filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            frasi = [line.strip() for line in f.readlines()]
        return frasi

    def valuta_differenza(self,valore_diff, soglie=None):
        """
        Valuta quanto un valore è diverso e ritorna una classificazione testuale.
        
        :param valore_diff: differenza tra i due valori (può essere positiva o negativa)
        :param soglie: dizionario con soglie personalizzabili
                    es: {'leggera': 5, 'forte': 15}
        :return: stringa con la valutazione o None
        """
        if isinstance(valore_diff, dict):  # Se valore_diff è un dizionario, iteriamo su ogni valore
            valutazioni = {key: self.valuta_differenza(val, soglie) for key, val in valore_diff.items()}
            
            # Ordinamento delle classificazioni per gravità
            ordine_gravita = {
                'troppo disteso': 4,
                'leggermente disteso': 3,
                'leggermente flesso': 2,
                'troppo flesso': 1
            }
            
            # Trova la classificazione più grave tra tutte le valutazioni
            valutazioni_gravita = [ordine_gravita[val] for val in valutazioni.values() if val is not None]
            
            if valutazioni_gravita:
                gravita_max = max(valutazioni_gravita)
                
                # Trova la classificazione corrispondente alla gravità massima
                for classificazione, gravita in ordine_gravita.items():
                    if gravita == gravita_max:
                        return classificazione
            return None

        if pd.isna(valore_diff):
            return None

        if soglie is None:
            soglie = {'leggera': 25, 'forte': 50}

        if valore_diff > soglie['forte']:
            return "troppo disteso"
        elif valore_diff > soglie['leggera']:
            return "leggermente disteso"
        elif valore_diff < -soglie['forte']:
            return "troppo flesso"
        elif valore_diff < -soglie['leggera']:
            return "leggermente flesso"
        else:
            return None


    def genera_frasi_diagnostiche(self,stats1, stats2):
        # Calcola le differenze tra le statistiche
        diff_media = stats1.xs('Media', axis=1, level='Statistica') - stats2.xs('Media', axis=1, level='Statistica')
        diff_q1 = stats1.xs('Q1', axis=1, level='Statistica') - stats2.xs('Q1', axis=1, level='Statistica')
        diff_q2 = stats1.xs('Mediana', axis=1, level='Statistica') - stats2.xs('Mediana', axis=1, level='Statistica')
        diff_q3 = stats1.xs('Q3', axis=1, level='Statistica') - stats2.xs('Q3', axis=1, level='Statistica')
        
        output_frasi = []

        for fase in diff_media.index:
            for angolo in diff_media.columns:
                differenze = {
                    'media': diff_media.loc[fase, angolo],
                    'Q1': diff_q1.loc[fase, angolo],
                    'Q2': diff_q2.loc[fase, angolo],
                    'Q3': diff_q3.loc[fase, angolo]
                }
                
                valutazione_globale = self.valuta_differenza(differenze)

                if valutazione_globale:
                    parte_corpo = angolo.replace("angolo_", "").replace("_", " ")
                    frase = f"angolo {parte_corpo} è {valutazione_globale} nella fase di {fase}"
                    output_frasi.append(frase)

        return output_frasi


    '''
    def confronta_tiri(self,path_tiro1, path_tiro2):
        # === LETTURA DATI ===
        df1 = pd.read_csv(path_tiro1)
        df2 = pd.read_csv(path_tiro2)
        df1 = df1[df1["fase_tiro"] != "none"]
        df2 = df2[df2["fase_tiro"] != "none"]

        colonne_angoli = [
            'angolo_spalla_sx', 'angolo_spalla_dx',
            'angolo_anca_sx', 'angolo_anca_dx',
            'angolo_gomito_dx', 'angolo_gomito_sx',
            'angolo_ginocchio_sx', 'angolo_ginocchio_dx'
        ]

        # === STATISTICHE E DIFFERENZE ===
        stats1 = self.calcola_statistiche(df1, colonne_angoli)
        stats2 = self.calcola_statistiche(df2, colonne_angoli)
        diff = (stats1 - stats2).abs()

        # === OUTPUT BASE ===
        for fase in stats1.index:
            print(f"\n--- FASE: {fase.upper()} ---")
            print(">>> Tiro 1")
            print(stats1.loc[fase])
            print("\n>>> Tiro 2")
            print(stats2.loc[fase])
            print("\n>>> Differenze Assolute")
            print(diff.loc[fase])


        # === PERCENTUALE CONFRONTABILITÀ ===
        percentuale = self.calcola_percentuale_confrontabilita(diff)
        # === ANALISI VERBALE ===
        frasi_output = self.genera_frasi_diagnostiche(stats1, stats2)
        frasiEN=self.traduci_frasi_in_inglese_grammaticalmente(frasi_output)

        print("\n🗣️ Frasi Diagnostiche Generate:")
        if frasiEN:
            for frase in frasiEN:
                print("-", frase)
        else:
            print("Nessuna differenza significativa rilevata.")
        return [frasiEN, percentuale]
    
    '''
    def confronta_tiri(self, path_tiro1, path_tiro2):
        # === LETTURA DATI ===
        df1 = pd.read_csv(path_tiro1)
        df2 = pd.read_csv(path_tiro2)
        df1 = df1[df1["fase_tiro"] != "none"]
        df2 = df2[df2["fase_tiro"] != "none"]

        colonne_angoli = [
            'angolo_spalla_sx', 'angolo_spalla_dx',
            'angolo_anca_sx', 'angolo_anca_dx',
            'angolo_gomito_dx', 'angolo_gomito_sx',
            'angolo_ginocchio_sx', 'angolo_ginocchio_dx'
        ]

        # === STATISTICHE E DIFFERENZE ===
        stats1 = self.calcola_statistiche(df1, colonne_angoli)
        stats2 = self.calcola_statistiche(df2, colonne_angoli)
        diff = (stats1 - stats2).abs()

        # === OUTPUT BASE ===
        for fase in stats1.index:
            print(f"\n--- FASE: {fase.upper()} ---")
            print(">>> Tiro 1")
            print(stats1.loc[fase])
            print("\n>>> Tiro 2")
            print(stats2.loc[fase])
            print("\n>>> Differenze Assolute")
            print(diff.loc[fase])

        # === PERCENTUALE CONFRONTABILITÀ ===
        percentuale = self.calcola_percentuale_confrontabilita(diff)

        # === ANALISI VERBALE ===
        frasi_output = self.genera_frasi_diagnostiche(stats1, stats2)
        frasiEN = self.traduci_frasi_in_inglese_grammaticalmente(frasi_output)

        # === MODIFICA PERCENTUALE IN BASE ALLE FRASI ===
        decremento = 0
        for frase in frasiEN:
            frase_lower = frase.lower()
            if "over" in frase_lower:
                decremento += 3.125
            if "slightly" in frase_lower:
                decremento += 1.5625

        percentuale_modificata = round(max(0, 100 - decremento), 2)
        print("\n🗣️ Frasi Diagnostiche Generate:")
        if frasiEN:
            for frase in frasiEN:
                print("-", frase)
        else:
            print("Nessuna differenza significativa rilevata.")

        print(f"\nPercentuale confrontabilità originale: {percentuale}%")
        print(f"Percentuale confrontabilità modificata: {percentuale_modificata}%")

        return [frasiEN, percentuale_modificata]

    
    def traduci_frasi_in_inglese_grammaticalmente(self, frasi_italiano):
        traduzioni_corpo = {
            "ginocchio": "knee",
            "gomito": "elbow",
            "spalla": "shoulder",
            "anca": "hip"
        }
        traduzioni_laterali = {
            "sx": "left",
            "dx": "right"
        }
        traduzioni_valutazioni = {
            "è leggermente flesso": "is slightly flexed",
            "è troppo disteso": "is over extended",
            "è leggermente disteso": "is slightly extended",
            "troppo flesso": "is over flexed",
            "leggermente disteso": "is slightly extended",
            "leggermente flesso": "is slightly flexed",
            "troppo disteso": "is over extended"
        }
        traduzioni_fasi = {
            "Follow-Through": "Follow-Through",
            "Estensione": "Transition",
            "Rilascio": "Release",
            "Preparazione":"Preparation"
        }

        frasi_inglese = []
        for frase in frasi_italiano:
            # Esempio frase: "angolo ginocchio sx è leggermente flesso nella fase di Follow-Through"

            # Split della frase per parti chiave
            # Forma attesa: "angolo <parte_corpo> <lato> è <valutazione> nella fase di <fase>"
            # Scomponiamo con split e replace
            try:
                frase = frase.lower()
                # Estrai parte corpo, lato, valutazione, fase
                # Rimuovo "angolo "
                frase = frase.replace("angolo ", "")
                # Rimuovo " nella fase di "
                parte, fase = frase.split(" nella fase di ")
                fase = fase.strip()
                fase_eng = traduzioni_fasi.get(fase.capitalize(), fase.capitalize())
                
                # parte es: "ginocchio sx è leggermente flesso"
                # divido per ' è '
                parte_corpo_lato, valutazione = parte.split(" è ")
                parte_corpo_lato = parte_corpo_lato.strip()
                valutazione = valutazione.strip()
                
                # parte_corpo_lato es: "ginocchio sx"
                tokens = parte_corpo_lato.split()
                parte_corpo_ita = tokens[0]
                lato_ita = tokens[1] if len(tokens) > 1 else ""

                parte_corpo_eng = traduzioni_corpo.get(parte_corpo_ita, parte_corpo_ita)
                lato_eng = traduzioni_laterali.get(lato_ita, lato_ita)
                valutazione_eng = traduzioni_valutazioni.get(valutazione, valutazione)

                frase_eng = f"The {lato_eng} {parte_corpo_eng} angle {valutazione_eng} during the {fase_eng} phase."
                # Prima lettera maiuscola
                frase_eng = frase_eng[0].upper() + frase_eng[1:]
                frasi_inglese.append(frase_eng)

            except Exception as e:
                # Se la frase non è nel formato previsto, ritorna la frase originale (o la traduzione semplice)
                frasi_inglese.append(frase)

        return frasi_inglese
    
    def genera_frasi(self):
        self.createCSV()
        path1="source/static/result/report_finale.csv"
        mano_dominante = session.get('mano_dominante')
        if mano_dominante=='destro':
            path2="source/static/ideal_form/report_finale_dx.csv"
        elif mano_dominante=='sinistro':
            path2="source/static/ideal_form/report_finale_sx.csv"
        else:
            return 'Errore'
        return self.confronta_tiri(path1,path2)