
class Pagina:
    """
    Representa una pagina de memoria virtual
    """

    def __init__(self, id_pagina: int, id_proceso: int):
        """
        Inicializa una pagina
        """
        self.id_pagina = id_pagina
        self.id_proceso = id_proceso
        self.cargada = False
        self.marco_asignado = None
        self.tiempo_carga = 0
        self.ultimo_acceso = 0

    def __str__(self) -> str:
        return f"Pag{self.id_pagina}(P{self.id_proceso})"

    def __repr__(self) -> str:
        return self.__str__()
