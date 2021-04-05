from typing import Optional

class COrder:

    def __init__(self, order:Optional[dict] = None):
        """Класс описывает объект который храниться в хранилище (описанный интерфейсом IBotStore). 
        Обеспечивает доступ к свойствам id, state, label и direction. В качестве аргумента принимает 
        объект (JSON) описывающий заказа на бирже - хранимый в свойстве source."""

        self.source = order

    def set_source(self, order:dict):
        self.source = order
        return self

    def reset(self):
        self.source = None
        return self

    def __getattr__(self,name):

        field_map = {
            'id' : 'order_id',
            'state' : 'order_state',
            'label' : 'label',
            'direction' : 'direction'
        }

        if name == 'source':
            return self.source
        elif name == 'isset':
            return (not (self.source is None))
        elif (name in field_map) and (self.source is None):
            return None
        elif (name in field_map):
            return self.source[field_map[name]]
        elif not (self.source is None) and (name in self.source):
            return self.source[name]
        else:
            raise AttributeError(f'{name} attribute not found in DerebitOrder')
