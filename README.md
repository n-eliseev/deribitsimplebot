# DeribitSimpleBot

Реализация простого бота для криптобиржи Deribit.\
Работает на Websockets JSON-RPC v.2 ([Документация](https://docs.deribit.com/))

## Возможности
 1. Возможность работы с несколькими инструментами одновременно
 2. Возобновление работы после остановки
 3. Возможность использвоать разные системы хранения ордеров


## Алгоримт работы

 1. Робот выставляет ордер #1 на покупку по цене **buy price = current price - gap / 2**.
 2. **(a)** Если цена уменьшается до **buy price**, то ордер #1, скорее всего, будет исполнен. В этом случае перейти к пункту 3.\
**(b)** Если цена увеличивается до такого значения, что становится истинным условие **current price > buy price + gap + gap ignore**, то робот должен отменить ордер #1. Далее, вернуться к пункту 1.
 3. Робот выставляет ордер #2 на продажу по цене **sell price = current price + gap**.
 4. **(a)** Если цена увеличивается до sell price, то ордер #2, скорее всего, будет исполнен. В этом случае вернуться к пункту 1.\
**(b)** Если цена уменьшается до такого значения, что становится истинным условие **current price < sell price - gap - gap ignore**, то робот должен отменить ордер #2. После этого следует вернуться к пункту 3.

## Требования
Python >=3.7, <4.0

## Установка
```
pip install deribitsimplebot
```

## Рабочий пример
 - [Полный рабочий пример](https://github.com/n-eliseev/deribitsimplebot/tree/master/example-app)
 - [Docker-compose приложение](https://github.com/n-eliseev/deribitsimplebotapp) (*для развёртывания в одну команду*) 

**Описание и примеры, ниже:**

## Настройка

Перед запуском необходимо определиться с настройками работы бота.\
В качестве шаблона предлагается файл вида (можно создать config.yaml со следующим содержимым).\
Такого конфига достаточно для начала работы бота.

```yaml
bot:

  url: wss://test.deribit.com/ws/api/v2

  # Будет добавлено к идентификатору групп ордеров
  order_label: 'dsb'
  
  auth:
    grant_type: 'client_credentials'
    client_id: ''			# Client ID из личного кабинета биржи
    client_secret: ''		# Client secret из личного кабинета биржи
  
  # Инструменты с которыми будет работать бот
  instrument:
    
    # Настройки по умолчанию
    default:
      gap: 100.0				# См. описание алгоритм
      gap_ignore: 50.0			# См. описание алгоритм
      price_id: 'mark_price'	# Тип цены, от которого брать вычисления
      amount: 10				# Объем стартового входа

    # Далее перечислены инструменты с которыми работает бот
    # Для каждого из них указан 
    #  - btc-perpetual - по умолчанию
    #  - eth-perpetual - объем входа 5, остальное по умолчанию 
    btc-perpetual:
    eth-perpetual:
      amount: 5

# Настройки синхронизации
synch:
  mod: 1
  actual: True
```

## Простой пример запуска
Пример простого работающего бота.\
Без хранилища (не умеет восстанавливать состояние) и без логирования.
```python
import yaml
from deribitsimplebot import CBot

with open('./config.yaml','r') as f:
	config = yaml.load(f.read(), Loader = yaml.FullLoader)

bot = CBot(**config['bot'])

bot.run()
```

## Синхронизация и хранение данных
Для хранения данных необходимо организоваться хранилище данных. Хранилище должно отвечать реализации интерфейса IBotStore. По умолчанию, в состав пакета входит реализация класса для организации хранилища в MySQL (CMySQLBotStore).

### База данных 
Для работы с базой данных необходима СУБД MySQL с созданной базой данных и таблицей следующего вида:

```sql
CREATE TABLE IF NOT EXISTS `order` (
	`id` VARCHAR(25) NOT NULL COMMENT 'ID, используется id с биржи' COLLATE 'utf8mb4_0900_ai_ci',
	`active` TINYINT(3) UNSIGNED NOT NULL DEFAULT '1' COMMENT '1 - управляется ботом, 0 - не управляется, 2 - управление потеряно (т.е. например: при загрузке ордер не нашелся)',
	`group_id` VARCHAR(64) NOT NULL COMMENT 'ID объединяет группу ордеров buy и sell (такое-же значение попадает в label у ордера)' COLLATE 'utf8mb4_0900_ai_ci',
	`instrument` VARCHAR(25) NOT NULL COMMENT 'Инструмент' COLLATE 'utf8mb4_0900_ai_ci',
	`state` VARCHAR(15) NOT NULL COMMENT 'Статус на бирже' COLLATE 'utf8mb4_0900_ai_ci',
	`type` VARCHAR(15) NOT NULL COMMENT 'Тип (limit, market и т.п.)' COLLATE 'utf8mb4_0900_ai_ci',
	`direction` VARCHAR(5) NOT NULL COMMENT 'Направление buy или sell' COLLATE 'utf8mb4_0900_ai_ci',
	`price` DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT '0.00' COMMENT 'Цена входа',
	`amount` DECIMAL(10,2) UNSIGNED NOT NULL DEFAULT '0.00' COMMENT 'Объем по ордеру',
	`real_create` DATETIME NOT NULL COMMENT 'Дата и время создания на бирже',
	`real_update` DATETIME NULL DEFAULT NULL COMMENT 'Дата и время последнего обновления на бирже',
	`create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата и время создания, ботом',
	`update` DATETIME NULL DEFAULT NULL COMMENT 'Дата и время последнего обновления, ботом',
	`raw_data` TEXT NULL DEFAULT NULL COMMENT 'Текст исходного JSON объекта ордера' COLLATE 'utf8mb4_0900_ai_ci',
	`last_raw_data` TEXT NULL DEFAULT NULL COMMENT 'Текст исходного JSON последнего объекта ордера' COLLATE 'utf8mb4_0900_ai_ci',
	`active_comment` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Комментарий по присвоенному статусу active (Например: order not find)' COLLATE 'utf8mb4_0900_ai_ci',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `active` (`active`) USING BTREE,
	INDEX `create` (`create`) USING BTREE,
	INDEX `real_create` (`real_create`) USING BTREE,
	INDEX `real_update` (`real_update`) USING BTREE,
	INDEX `update` (`update`) USING BTREE,
	INDEX `instrument` (`instrument`) USING BTREE,
	INDEX `group_id` (`group_id`) USING BTREE
)
COMMENT='Таблица ордеров, созданные и ведомые ботом (базовые понятия о типах, были взяты с типов данных биржи Deribit)'
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;
```
### Настройки
**Добавить в файл** настройки данные для подключения к БД.\
Поля для подключения указываемые в настройках соотвествуют параметрам конструктора: [MySQLConnection](https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html)

```yaml
db:
  user: 'root'
  password: ''
  host: ''
  database: ''
  charset: 'utf8mb4'
```

### Синхронизация
В настройках указаны параметры для синхронизации.
 - **actual** - продолжать управление ранее созданными ордерами по инструментам указанным в настройках бота
 - **mod** - режим синхронизации - указывает как надо проводить синхронизацию тех ордеров у которых active = 1 (т.е. управляемые ботом).\
 *mod = 0* - ничего не делать\
 *mod = 1* - все ордера управляемые ботом (кроме тех, которые актуальны для тех инструментов, которые указаны) имеющие статус Open на бирже - будут принудительно закрыты.\
 *mod не 0 и не 1* - все ордера управляемые ботом (кроме тех, которые актуальны для тех инструментов) будут сняты с управления ботом, без доп.запросов на биржу 

### Пример робота работающего с харнилищем
В отличии от первого примера, данный бот можно остановить, после повтороного запуска, он "подберёт" орера с которыми он работал до этого и продолжит работу.

```python
from deribitsimplebot import CBot, CMySQLBotStore
import yaml

with open('./config.yaml','r') as f:
	config = yaml.load(f.read(), Loader = yaml.FullLoader)
    
bot = CBot(
	**config['bot'], 
	store = CMySQLBotStore(**config['db'])
)

bot.run(
	synch_mod = config['synch']['mod'], 
    synch_actual = config['synch']['actual']
)
```

## Логирование
Модуль поддерживает стандартную библиотеку логирования logging. В состав пакета входит обработчик (CLogMySQLHandler) для хранения логов в БД MySQL со структурой:
```sql
CREATE TABLE IF NOT EXISTS `log` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`sender_id` VARCHAR(100) NULL DEFAULT NULL COMMENT 'Имя модуля или программы создавшей лог' COLLATE 'utf8mb4_0900_ai_ci',
	`level` VARCHAR(25) NOT NULL COMMENT 'Тип записи' COLLATE 'utf8mb4_0900_ai_ci',
	`level_order` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0' COMMENT 'Значимый вес',
	`data` TEXT NOT NULL COMMENT 'Текст лога' COLLATE 'utf8mb4_0900_ai_ci',
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `create` (`create`) USING BTREE,
	INDEX `sender_id` (`sender_id`) USING BTREE,
	INDEX `level` (`level`) USING BTREE,
	INDEX `level_order` (`level_order`) USING BTREE
)
COMMENT='Содержит логи работы бота'
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;
```

В файл конфигурации **нужно добавить** настройки. Секция настроек поддерживает [настройки модуля logging](https://docs.python.org/3/library/logging.config.html)

```yaml
logging:
  version: 1
  
  formatters:
    simple:
      format: '%(asctime)s %(name)s [%(levelname)s]: %(message)s'

  handlers:
    console:
      class: 'logging.StreamHandler'
      level: 'INFO'
      formatter: 'simple'
      stream: 'ext://sys.stdout'
    file:
      class: 'logging.FileHandler'
      level: 'WARNING'
      filename: 'bot_log.log'
    mysqldb:
      class: 'deribitsimplebot.db.CLogMySQLHandler'
      level: 'INFO'
      <<: *db-cred

  loggers:
    deribit_bot:
      handlers: [mysqldb, file]

  root:
    level: 'INFO'
    handlers: [console,file]
```

### Полный пример робота

```python
from deribitsimplebot import CBot, CMySQLBotStore
import yaml
import logging.config

with open('./config.yaml','r') as f:
	config = yaml.load(f.read(), Loader = yaml.FullLoader)

logging.config.dictConfig(config['logging'])

bot = CBot(
	**config['bot'], 
	store = CMySQLBotStore(**config['db'])
)

bot.run(
	synch_mod = config['synch']['mod'], 
    synch_actual = config['synch']['actual']
)
```