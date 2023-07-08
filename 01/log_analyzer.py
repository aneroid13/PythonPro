import os
import json
import gzip
import regex
import argparse
import logging
import logging.handlers
from pathlib import Path
from statistics import median
from string import Template
from collections import namedtuple
from json.decoder import JSONDecodeError


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

logging.basicConfig(level=logging.WARNING)

sys_logger = logging.getLogger("system_logger")
sys_logger_filename='./parse_log.txt'
sys_logger_format='[%(asctime)s] %(levelname).1s %(message)s'
sys_logger_level=logging.DEBUG
sys_logger_formatter = logging.Formatter(sys_logger_format)
console_handle = logging.StreamHandler()
console_handle.setLevel(sys_logger_level)
console_handle.setFormatter(sys_logger_formatter)
file_handle = logging.handlers.RotatingFileHandler(sys_logger_filename)
file_handle.setFormatter(sys_logger_formatter)
file_handle.setLevel(sys_logger_level)
sys_logger.addHandler(console_handle)
sys_logger.addHandler(file_handle)

log_req_time_total = 0.0
log_counter = {}

def log_file(dir):
    max_date = 0
    log_name = None
    reg_name = "^nginx-access-ui\.log-(\d{8})\.*(gz)*$"
    fname = namedtuple("Log_filename", ['name','date','ext'])
    for name in os.listdir(dir):
        get_name = regex.findall(reg_name, name)
        if get_name:
            if int(get_name[0][0]) > max_date:
                max_date = int(get_name[0][0])
                log_name = fname(name, int(get_name[0][0]), str(get_name[0][1]))
    return log_name

def log_get(logf):
    if logf.suffix == ".gz":
        log = gzip.open(logf, 'rt')
    else:
        log = open(logf, 'rt')
    with log as l_file:
        for line in l_file:
            yield line

def log_string_parse(log_str: str):
    global log_req_time_total
    url, time = "", 0.0
    tmpl = regex.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} .* \"(?:GET|POST|DELETE|PUT|HEAD|OPTIONS|-) (.*) HTTP/\d.\d\".* (\d+\.\d*)$")

    try:
        url, time = regex.findall(tmpl, log_str)[0]
        url = str(url)
        time = float(time)
        log_req_time_total += time
        sys_logger.log(logging.INFO, "Log string: " + log_str)
        sys_logger.log(logging.INFO, "Log parse url string: " + url + " access time:" + str(time))
    except IndexError as e:
        sys_logger.log(logging.WARNING, "Wrong string format: " + log_str)
    return url, time

def log_statistics(log_limit: int):
    url_stat = []
    for key, val in log_counter.items():
        times = val
        sys_logger.log(logging.INFO, "Log stats. URL: " + str(key) + " list time: " + str(times))
        url_stat.append({
            'url': key,
            'count': len(times),
            'count_perc': (1 / len(log_counter)) * 100,
            'time_max': max(times),
            'time_sum': sum(times),
            'time_avg': sum(times) / len(times),
            'time_med': median(times),
            'time_perc': (sum(times) / log_req_time_total) * 100
            })
    url_stat.sort(key=lambda x: x['time_sum'], reverse=True)

    if len(url_stat) < log_limit:
        log_limit = len(url_stat)

    return url_stat[0:log_limit]

def log_report(stat, file_date, report_dir):
    template_path = Path("./template.html")
    if not Path(report_dir).exists():
        Path(report_dir).mkdir()
    report_file_name = Path(f"{report_dir}/report-{file_date}.html")

    tmpl_ex = ""
    with open(template_path, "rt") as f_rep:
        for line in f_rep:
            tmpl_ex += line

    tmpl = Template(str(tmpl_ex))
    tmpl_sub = dict(table_json=json.dumps(stat))
    with open(report_file_name, "wt") as f_rep_fresh:
        f_rep_fresh.write(tmpl.safe_substitute(tmpl_sub))

def log_args():
    parser = argparse.ArgumentParser(description='HTTP log parser script')
    parser.add_argument('-c', '--config', default="./log_analyzer.conf", required=False, action='store', help='Path to config file')
    return parser.parse_args().config

def log_read_conf(conf_file: str):
    fp = None
    try:
        with open(conf_file, 'rt') as f_conf:
            fp = json.load(f_conf)
    except (FileNotFoundError, JSONDecodeError) as ex:
        if ex == FileNotFoundError:
            sys_logger.log(logging.ERROR, f"File not found: {conf_file}")
        elif ex == JSONDecodeError:
            sys_logger.log(logging.ERROR, "Wrong format, must be json.")
        else:
            sys_logger.log(logging.ERROR, ex)
    if fp:
        return fp
    else:
        return config

def main():
    current_config = log_read_conf(log_args())
    file = log_file(current_config['LOG_DIR'])
    full_path = Path().joinpath(current_config['LOG_DIR'], file.name)
    if file:
        for log_str in log_get(full_path):
            l_url, l_time = log_string_parse(log_str)
            if l_url in log_counter:
                log_counter[l_url].append(l_time)
            else:
               log_counter[l_url] = [l_time]

        url_stat = log_statistics(current_config['REPORT_SIZE'])
        log_report(url_stat, file.date, current_config['REPORT_DIR'])


if __name__ == "__main__":
    main()
