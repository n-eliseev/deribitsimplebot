"""
Хранит реализацию двух классов для работы с MySQL:
 - CMySQLBotStore(IBotStore) - для хранения данных о заказах в БД
 - CLogMySQLHandler(logging.Handler) - для логирования в БД
"""

import json
import time
import logging
from .interface import IBotStore
from mysql.connector import MySQLConnection
from typing import Union, NoReturn


class CMySQLBotStore(IBotStore):
    """Реализация интерфейса IBotStore обеспечивающее хранение заявок в БД MySQL.
    Описание и требования см. IBotStore
    """

    def __init__(self,connection : MySQLConnection = None, **connection_option):
        """На входе надо передать, либо собранный коннектор, либо параметры для подключения
        через MySQLConnection (см. https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html)
        """
        super().__init__()
        self.__connection = (MySQLConnection(**connection_option) if connection is None else connection) 
        self.__cursor = self.__connection.cursor(dictionary = True)

    def __del__(self):
        try:
            self.__cursor.close()
            self.__connection.close()
        except:
            pass

    def get(self, id:Union[int,str,None] = None, param:dict = {}, order_by:dict[str,str] = {}) -> Union[None, dict, list[dict]]:
        
        sql = 'select * from `order` where '
        _real_param = {}

        if not (id is None):
            
            sql+='`id`=%(id)s limit 1'
            _real_param = { 'id': id }

        elif len(param.keys()):

            _p = []
            
            for i in param:

                _cd = {
                    'operation' : '=',
                    'value' : param[i]
                }
 
                if isinstance(param[i],list):
                    _cd['operation'] = 'in'
                elif isinstance(param[i],dict):
                    _cd = param[i]

                if 'raw' in _cd:
                    _p.append(_cd['raw'])
                else:

                    if isinstance(_cd['value'],list):
                        
                        __p = []
                        
                        for j,v in enumerate(_cd['value']):
                            __p.append(f'%({i}_{j})s')
                            _real_param[f'{i}_{j}'] = v
                        
                        _pp = f'({",".join(__p)})'
                    
                    else:
                        _pp = f'%({i})s'
                        _real_param[i] = _cd['value']
                
                    _p.append(f'(`{i}` {_cd["operation"]} {_pp})')
    
            sql+=' and '.join(_p)

        if len(order_by):
            _ob=order_by.popitem()
            sql+=f' order by `{_ob[0]}` {_ob[1]}'

        self.__cursor.execute(sql,_real_param)
        order = self.__cursor.fetchone() if not (id is None) else self.__cursor.fetchall() 
        self.__connection.commit()

        return order


    def insert(self,order:dict, other_param:dict = {}, return_is_active:bool = True, modify_active:bool = True):
        return self.__write(
                is_insert = True, 
                order = order, 
                other_param=other_param,
                return_is_active = return_is_active,
                modify_active = modify_active,
                field_map = {
                    'id' : 'order_id',
                    'group_id' : 'label',
                    'instrument' : 'instrument_name',
                    'state' : 'order_state',
                    'type' : 'order_type',
                    'direction': 'direction',
                    'price' : 'price',
                    'amount' : 'amount',
                    'real_create' : 'creation_timestamp',
                    'raw_data' : 'raw_data'
                }
            )


    def update(self, id:Union[int,str,None], order:dict, other_param:dict = {}, return_is_active:bool = True, modify_active:bool = True) :
        return self.__write(
                is_insert = False, 
                id = id,
                order = order, 
                other_param=other_param,
                return_is_active = return_is_active,
                modify_active = modify_active,
                field_map = {
                    'state' : 'order_state',
                    'type' : 'order_type',
                    'price' : 'price',
                    'amount' : 'amount',
                    'update' : 'update',
                    'real_update' : 'last_update_timestamp',
                    'last_raw_data' : 'last_raw_data'
                }
            )


    def __write(self, is_insert:bool, field_map:dict, order:dict = None, id:Union[int,str,None] = None, other_param:dict = {}, return_is_active:bool = True, modify_active:bool = True):

        _order = { **other_param }

        if order is None:
            order = {}

        if 'active' in _order:
            modify_active = False

        for i in field_map :

            if (i == 'real_create' or i == 'real_update') and (field_map[i] in order):
                _order[i] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(order[field_map[i]]/1000)))
            elif (i == 'raw_data') or (i == 'last_raw_data'):
                _order[i] = json.dumps(order)
            elif (i == 'update'):
                _order[i] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
            elif (field_map[i] in order):
                _order[i] = order[field_map[i]]
        
        if modify_active and (_order['state'] != 'open') and (_order['state'] != 'filled'):
            _order['active'] = 0
            _order['active_comment'] = 'Order is not open or filled'

        if is_insert:
            sql = f'insert into `order` (`{"`,`".join(_order.keys())}`) values (%({")s,%(".join(_order.keys())})s)'
        else :
            _p = [f'`{i}`=%({i})s' for i in _order.keys()]
            sql = f'update `order` set {", ".join(_p)} where `id` = %(id)s limit 1'
            _order['id'] = id

        self.__cursor.execute(sql,_order)
        self.__connection.commit()

        return self.get(param = {'id' : _order['id'],'active' : 1}) if return_is_active else self.get(_order['id'])



class CLogMySQLHandler(logging.Handler):
    """Реализация обработчика для записи логов в БД"""

    def __init__(self, connection : MySQLConnection = None, **connection_option):
        super().__init__()
        self.__connection = (MySQLConnection(**connection_option) if connection is None else connection)
        self.__cursor = self.__connection.cursor(dictionary = True)

    def emit(self, record):

        sql = 'insert into `log` (`sender_id`,`level`,`level_order`,`data`) values (%(sender_id)s,%(level)s,%(level_order)s,%(data)s)'

        param = {
            'sender_id' : record.name,
            'level' : record.levelname,
            'level_order' : record.levelno,
            'data' : record.msg
        }

        self.__cursor.execute(sql,param)
        self.__connection.commit()