class InvalidEquipmentException(Exception):
    def __init__(self, status: str, message: str, equipment_id: int) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
        self.equipment_id = equipment_id


class InvalidEquipmentsException(Exception):
    ...
