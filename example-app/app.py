from deribitsimplebot import CBot, CMySQLBotStore
import yaml
import logging.config

def main():

    # Подгружаем конфиг
    with open('./config.yaml','r') as f:
        config = yaml.load(f.read(), Loader = yaml.FullLoader)

    # Загружаем настройки в логер
    logging.config.dictConfig(config['logging'])

    # Создаём бота и выгружаем и хранилище
    bot = CBot(
        **config['bot'], 
        store = CMySQLBotStore(**config['db'])
    )

    # Запускаем бота
    bot.run(
        synch_mod = config['synch']['mod'], 
        synch_actual = config['synch']['actual']
    )

# Запуск
if __name__ == '__main__':
    main()