import joblib
from tensorflow.keras.models import load_model # type: ignore
import pandas as pd

class modello:
    def  __init__(self):
        self.model = joblib.load('source/LLM/xgboost_model.pkl')
        self.label_encoder = joblib.load('source/LLM/label_encoder_mano_dominante.pkl')
        self.target_encoder = joblib.load('source/LLM/target_encoder_fase_tiro.pkl')
        self.categorical_columns = joblib.load('source/LLM/categorical_columns.pkl')

    def calcola_fasa(self, mano_dominante, 
                 angolo_gomito_sx, angolo_gomito_dx,
                 angolo_spalla_sx, angolo_spalla_dx, 
                 angolo_ginocchio_sx, angolo_ginocchio_dx,
                 angolo_anca_sx, angolo_anca_dx):
        new_data = pd.DataFrame([{
                'mano_dominante': mano_dominante,
                'angolo_spalla_sx': angolo_spalla_sx,
                'angolo_spalla_dx': angolo_spalla_dx,
                'angolo_anca_sx': angolo_anca_sx,
                'angolo_anca_dx': angolo_anca_dx,
                'angolo_gomito_dx': angolo_gomito_dx,
                'angolo_gomito_sx': angolo_gomito_sx,
                'angolo_ginocchio_sx': angolo_ginocchio_sx,
                'angolo_ginocchio_dx': angolo_ginocchio_dx
        }])
        #XGBoost usage
        # Codifica della colonna 'mano_dominante' per i nuovi dati
        new_data['mano_dominante'] = self.label_encoder.transform(new_data['mano_dominante'])

        # Previsione della fase_tiro per i nuovi dati
        new_predictions = self.model.predict(new_data)

        # Decodifica delle predizioni per ottenere le etichette originali
        predicted_labels = self.target_encoder.inverse_transform(new_predictions)
        
        return predicted_labels
