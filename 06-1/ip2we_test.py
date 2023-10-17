import unittest
import httpx

class uWSGIServer(unittest.TestCase):
  host = "localhost"
  port = 80

  def setUp(self):
    self.conn = httpx.Client()
    self.base = f"http://{self.host}:{self.port}/"
    self.iptest = f"{self.base}/ip2w/"

  def tearDown(self):
    self.conn.close()

  def test_server_header(self):
    """Server header exists"""
    r = self.conn.get(self.base)
    self.assertIsNotNone(r.headers)

  def test_LA_city(self):
    ip = '1.1.1.1'
    r = self.conn.get(f"{self.iptest}{ip}")
    city = r.json()['city']
    self.assertEqual(city, 'Лос-Анджелес')

  def test_zero_ip(self):
    ip = "0.0.0.0"
    r = self.conn.get(f"{self.iptest}{ip}")
    code = r.status_code
    self.assertEqual(code, 404)

  def test_local_ip(self):
    ip = "10.10.10.10"
    r = self.conn.get(f"{self.iptest}{ip}")
    json_err = r.json()['error']
    self.assertEqual(json_err, "Address not found")
