import ipinfo       # https://ipinfo.io/developers
import httpx
import asyncio
import logging
import logging.handlers
import json
from urllib.parse import urlparse
from pathlib import Path

default_log_path = '/var/log/ip2w/ip2w.log'
default_conf_path = '/usr/local/etc/ip2w.conf'

def server_log_config(log_path: str):
    log_path = Path(log_path).resolve()
    if not log_path.exists():
        log_path.touch()
    fh = logging.handlers.TimedRotatingFileHandler(log_path, 'd', 1, 7, 'utf-8')
    log_format = logging.Formatter('{asctime} {levelname} {module} {message}', style='{')
    fh.setFormatter(log_format)

    logger_srv = logging.getLogger("server_logger")
    logger_srv.setLevel(logging.INFO)
    logger_srv.addHandler(fh)
    return logger_srv

### Log format
## {"api_token_ip": "xxx",
## api_token_weather": "xxx",
## "log_path": "/var/log/ip2w/ip2w.log"}
def conf_reader(conf_file: str):
    fp = None
    try:
        with open(conf_file, 'rt') as f_conf:
            fp = json.load(f_conf)
    except FileNotFoundError as ex:
        log.error(f"File not found: {conf_file}")
    except json.JSONDecodeError as ex:
        log.error("Wrong format, must be json.")
    except Exception as ex:
        log.error(f"Error: {ex}")

    return fp

# print(details.all, details.city, details.loc, details.country, details.country_name)
async def location_request(ip_address: str):
    try:
        handler_ip = ipinfo.getHandlerAsync(api_token_ip)
        details = await handler_ip.getDetails(ip_address)
        log.info(f"IP address {ip_address} resolve in {details.city} ")
        await handler_ip.deinit()
        return details.city
    except Exception as ex:
        await handler_ip.deinit()
        log.error(f"Error for {ip_address} ip: {ex}")

async def weather_request(city: str):
    params = {'q': city, 'lang': 'ru', 'appid': api_token_weather}
    try:
        handler_we = httpx.AsyncClient()
        response = await handler_we.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        log.info(f"{city} city weather: {response.json()['weather']}")
        log.debug(f"{city} city weather: {response.json()}")
        await handler_we.aclose()
        return response.json()
    except Exception as ex:
        await handler_we.aclose()
        log.error(f"Error for {city} city: {ex}")

def weather_format(we: dict):
    we_dict = {
     "city": we['name'],
     "temp": we['main']['temp'],
     "conditions": we['weather'][0]['description']
    }
    return json.dumps(we_dict)

async def get_weather(ip_address: str):
    city = await location_request(ip_address)
    if city:
        weather = await weather_request(city)
        return weather_format(weather)
    else:
        return None

conf = conf_reader(default_conf_path)
api_token_ip = conf.get('api_token_ip')
api_token_weather = conf.get('api_token_weather')
log_path = conf.get('log_path') or default_log_path
log = server_log_config(log_path)
#loop = asyncio.run(get_weather(ip)

# 'REQUEST_METHOD': 'GET',
# 'REQUEST_URI': '/ip2w',
# 'PATH_INFO': '/ip2w',
# https://peps.python.org/pep-3333/
def application(env, start_response):
    result = None
    if env['REQUEST_METHOD'] == 'GET':
        ip = str(urlparse(env['PATH_INFO']).path.strip('/').split('/')[-1])
        result = asyncio.run(get_weather(ip))

    if result:
        result = str(result).encode('utf-8')
        start_response('200 OK', [('Content-Type', 'text/json')])
        return [result]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/json')])
        return [b'{"error": "Address not found"}']