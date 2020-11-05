import logging


def get_logger(log_level='DEBUG'):
    log_level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

    bot_logger = logging.getLogger()
    bot_logger.setLevel(log_level_dict[log_level])
    format_file = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%d-%m-%Y %H:%M")
    format_console = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    bot_streamhendler = logging.StreamHandler()
    bot_streamhendler.setLevel(log_level_dict[log_level])
    bot_streamhendler.setFormatter(format_console)

    bot_filehendler = logging.FileHandler('bot_vk.log', 'w', 'utf-8')
    bot_filehendler.setLevel(log_level_dict[log_level])
    bot_filehendler.setFormatter(format_file)

    bot_logger.addHandler(bot_filehendler)
    bot_logger.addHandler(bot_streamhendler)
