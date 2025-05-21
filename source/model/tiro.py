class tiro:
    def __init__(self, mano_dominante, 
                 angoli_gomito_sx, angoli_gomito_dx,
                 angoli_spalla_sx, angoli_spalla_dx, 
                 angoli_ginocchio_sx, angoli_ginocchio_dx,
                 angoli_anca_sx, angoli_anca_dx,phases):
        
        self.mano_dominante = mano_dominante # "destra" o "sinistra"
        self.angoli_gomito_sx = angoli_gomito_sx
        self.angoli_gomito_dx = angoli_gomito_dx
        self.angoli_ginocchio_sx = angoli_ginocchio_sx
        self.angoli_ginocchio_dx = angoli_ginocchio_dx
        self.angoli_spalla_sx = angoli_spalla_sx
        self.angoli_spalla_dx = angoli_spalla_dx
        self.angoli_anca_sx = angoli_anca_sx
        self.angoli_anca_dx = angoli_anca_dx
        self.phases=phases
    
