APP_PATH = '/home/pi/godenerg/'


logger_conf = {
    'filename': 'godenerg.log',
    'format': '[%(asctime)s] %(message)s'
}

http_conf = {
    'port': 8889
}


datalogger_conf = {
    'db_filename': APP_PATH + 'godenerg.db',
    'interval': 15,
    'last_interval': 2,
    'samples': 7200,
    'port': 8890
}

charger_conf = {
    'float_voltage': 26.4,
    'absorbtion_voltage': 29.2,
    'absorbtion_amps_threshold': 6.4,
    'charge_check_start': 11,
    'charge_check_end': 23
}

weather_api_conf = {
    'enable': True,
    'url': 'http://api.weatherstack.com/current?'\
           'access_key={APIXU_API_KEY}&query={LAT},{LNG}&forecast_days=4',
    'lat': '53.916151',
    'lng': '-115.239140',
    'api_key_file': APP_PATH + 'apixu_api_key.txt'
}
