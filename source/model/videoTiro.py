import cv2
import numpy as np
import mediapipe as mp
import os
from flask import session

from source.LLM.modello import modello
from source.model.tiro import tiro


class VideoTiro:
    def __init__(self, path, atleta):
        self.path = path
        self.player = atleta
        self.numero_frame = self._calcola_numero_frame()

    def standardizzazione(self, phases):
        fase_ordinale = ['none', 'preparazione', 'estensione', 'rilascio', 'Follow-Through']
        fasi_raw = [x[0] for x in phases]
        fasi_corrette = []
        fase_corrente_idx = 0

        for fase in fasi_raw:
            try:
                idx_fase = fase_ordinale.index(fase)
            except ValueError:
                idx_fase = fase_corrente_idx

            if idx_fase == fase_corrente_idx or idx_fase == fase_corrente_idx + 1:
                fase_corrente_idx = idx_fase

            fasi_corrette.append(fase_ordinale[fase_corrente_idx])
        return fasi_corrette

    def _calcola_numero_frame(self):
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            raise ValueError(f"Impossibile aprire il video: {self.path}")
        numero_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return numero_frame

    def calcola_angolo(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angolo = np.abs(radians * 180.0 / np.pi)
        if angolo > 180.0:
            angolo = 360 - angolo
        return angolo

    def esamina_video(self):
        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(self.path)
        models = modello()

        if not cap.isOpened():
            print("Errore nell'aprire il video. Controlla il percorso.")
            exit()

        angoli_gomito_sx = []
        angoli_spalla_sx = []
        angoli_anca_sx = []
        angoli_ginocchio_sx = []

        angoli_gomito_dx = []
        angoli_spalla_dx = []
        angoli_anca_dx = []
        angoli_ginocchio_dx = []

        phases = []
        frame_count = 0
        fasi_frames = {}
        fasi_counter = {}

        mano_dominante = self.player.hand

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Fine del video.")
                    break

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks:
                    # Landmark bianchi
                    for landmark in results.pose_landmarks.landmark:
                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])
                        cv2.circle(image, (x, y), radius=3, color=(0, 0, 0), thickness=-1)

                    # Linee gialle
                    for connection in mp_pose.POSE_CONNECTIONS:
                        start_idx, end_idx = connection
                        start = results.pose_landmarks.landmark[start_idx]
                        end = results.pose_landmarks.landmark[end_idx]
                        start_point = (int(start.x * frame.shape[1]), int(start.y * frame.shape[0]))
                        end_point = (int(end.x * frame.shape[1]), int(end.y * frame.shape[0]))
                        cv2.line(image, start_point, end_point, color=(0, 255, 255), thickness=2)

                    landmarks = results.pose_landmarks.landmark

                    spalla_sx = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    gomito_sx = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    polso_sx = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    anca_sx = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    ginocchio_sx = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    caviglia_sx = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                   landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                    spalla_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    gomito_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    polso_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    anca_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    ginocchio_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    caviglia_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                    angolo_gomito_sx = self.calcola_angolo(spalla_sx, gomito_sx, polso_sx)
                    angolo_spalla_sx = self.calcola_angolo(anca_sx, spalla_sx, gomito_sx)
                    angolo_anca_sx = self.calcola_angolo(spalla_sx, anca_sx, ginocchio_sx)
                    angolo_ginocchio_sx = self.calcola_angolo(anca_sx, ginocchio_sx, caviglia_sx)

                    angolo_gomito_dx = self.calcola_angolo(spalla_dx, gomito_dx, polso_dx)
                    angolo_spalla_dx = self.calcola_angolo(anca_dx, spalla_dx, gomito_dx)
                    angolo_anca_dx = self.calcola_angolo(spalla_dx, anca_dx, ginocchio_dx)
                    angolo_ginocchio_dx = self.calcola_angolo(anca_dx, ginocchio_dx, caviglia_dx)

                    frame_count += 1

                    angoli_gomito_sx.append(angolo_gomito_sx)
                    angoli_spalla_sx.append(angolo_spalla_sx)
                    angoli_anca_sx.append(angolo_anca_sx)
                    angoli_ginocchio_sx.append(angolo_ginocchio_sx)

                    angoli_gomito_dx.append(angolo_gomito_dx)
                    angoli_spalla_dx.append(angolo_spalla_dx)
                    angoli_anca_dx.append(angolo_anca_dx)
                    angoli_ginocchio_dx.append(angolo_ginocchio_dx)

                    phase = models.calcola_fasa(
                        mano_dominante,
                        angolo_gomito_sx, angolo_gomito_dx,
                        angolo_spalla_sx, angolo_spalla_dx,
                        angolo_ginocchio_sx, angolo_ginocchio_dx,
                        angolo_anca_sx, angolo_anca_dx
                    )
                    phases.append(phase)
                    fase_corrente = phase[0]

                    if fase_corrente not in fasi_counter:
                        fasi_counter[fase_corrente] = 0
                    fasi_counter[fase_corrente] += 1

                    if fase_corrente == 'Follow-Through' and fasi_counter[fase_corrente] == 3:
                        fasi_frames[fase_corrente] = image.copy()
                    elif fase_corrente != 'Follow-Through' and fase_corrente not in fasi_frames:
                        fasi_frames[fase_corrente] = image.copy()

            cap.release()
            cv2.destroyAllWindows()

            temp_folder = "static/temp_frames"
            os.makedirs(temp_folder, exist_ok=True)

            for fase, frame in fasi_frames.items():
                filename = f"{fase}.jpg"
                path = os.path.join(temp_folder, filename)
                cv2.imwrite(path, frame)
                session[fase] = filename

        cleaned_phases = [elem[0] for elem in phases]
        print(cleaned_phases)

        shot = tiro(
            mano_dominante,
            angoli_gomito_sx, angoli_gomito_dx,
            angoli_spalla_sx, angoli_spalla_dx,
            angoli_ginocchio_sx, angoli_ginocchio_dx,
            angoli_anca_sx, angoli_anca_dx,
            cleaned_phases
        )
        print("Video analizzato")
        return shot




            