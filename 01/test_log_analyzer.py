import unittest
import typing
import os
from log_analyzer import log_file, log_get, log_args, log_read_conf, log_string_parse, log_statistics, log_report, config

class Test(unittest.TestCase):
    def setUp(self):
        global log_counter, log_req_time_total
        log_req_time_total = 0.34143 + 0.154
        log_counter = {'/saadsfas/sdfasdf': [0.34143, 0.154],
                       '/api/v2/slot/4822/groups': [0.157],
                       '/api/v2/internal/banner/24442283/info': [0.053],
                       '/api/v2/internal/banner/24440845/info': [0.061],
                       '/api/v2/internal/banner/24439023/info': [0.071],
                       '/api/v2/internal/banner/24440992/info': [0.063],
                       '/api/v2/internal/banner/24413886/info': [0.058]}

    def tearDown(self):
        pass

    def test_log_file(self):
        l_name = log_file('.')
        self.assertIsInstance(l_name.date, int)

    def test_log_get(self):
        log_path = "log/nginx-access-ui.log-20170630.gz"
        self.assertIsInstance(log_get(log_path), typing.Generator)

    def test_log_args(self):
        self.assertTrue(log_args())

    def test_log_read_conf(self):
        self.assertIsInstance(log_read_conf('./log_analyzer.conf'), dict)

    def test_log_string_parse(self):
        good_string =   "".join('''1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" ''',
                                '''"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157''')
        wrong_string =  "".join('''1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "TUP /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" ''',
                                '''"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157''')
        result = log_string_parse(good_string)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], float)
        self.assertNotEqual(result[0], "-")
        result_wr = log_string_parse(wrong_string)
        self.assertEqual(result_wr[0], "")

    def test_log_stat(self):
        stat = log_statistics(100)
        print(stat)
        self.assertTrue(stat)

    def test_log_report(self):
        date = 20201020
        stat = [{"count": 2767,
                 "time_avg": 62.994999999999997,
                 "time_max": 9843.5689999999995,
                 "time_sum": 174306.35200000001,
                 "url": "/api/v2/internal/html5/phantomjs/queue/?wait=1m",
                 "time_med": 60.073,
                 "time_perc": 9.0429999999999993,
                 "count_perc": 0.106},
                {"count": 1410,
                 "time_avg": 67.105999999999995,
                 "time_max": 9853.3729999999996,
                 "time_sum": 94618.864000000001,
                 "url": "/api/v2/internal/gpmd_plan_report/queue/?wait=1m&worker=5",
                 "time_med": 60.124000000000002,
                 "time_perc": 4.9089999999999998,
                 "count_perc": 0.053999999999999999}
                ]
        log_report(stat, date, config['REPORT_DIR'])
        self.assertTrue(os.path.exists(f"{config['REPORT_DIR']}/report-{date}.html"))
