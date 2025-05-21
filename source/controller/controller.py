# source/controller/controller.py
from source.model.videoTiro import VideoTiro
from source.model.athlete import athlete  # la tua classe atleta
from source.model.result import result
class Controller:
    @staticmethod
    def onAnalize(path, name, surname, weight, height, birth, position,hand):
        plyr = athlete(name, surname, weight, height, birth, position,hand)
        vid = VideoTiro(path,plyr)
        print("Analisi avviata per", plyr.name, plyr.surname)

        shot=vid.esamina_video()
        risultati=result(shot)
        [output, percentuale]= risultati.genera_frasi()

        return [output, percentuale]
