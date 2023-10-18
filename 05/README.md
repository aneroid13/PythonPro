Web server test suite
=====================

Implement a Web server. Libraries for helping manage TCP socket connections *may* be used (if server is asynchronous [epoll](https://github.com/m13253/python-asyncore-epoll) *must* be used). Libraries that implement any part of HTTP or multiprocessing model *must not* be used.

## Requirements ##

* Respond to `GET` with status code in `{200,403,404}`
* Respond to `HEAD` with status code in `{200,404}`
* Respond to all other request methods with status code `405`
* Directory index file name `index.html`
* Respond to requests for `/<file>.html` with the contents of `DOCUMENT_ROOT/<file>.html`
* Requests for `/<directory>/` should be interpreted as requests for `DOCUMENT_ROOT/<directory>/index.html`
* Respond with the following header fields for all requests:
  * `Server`
  * `Date`
  * `Connection`
* Respond with the following additional header fields for all `200` responses to `GET` and `HEAD` requests:
  * `Content-Length`
  * `Content-Type`
* Respond with correct `Content-Type` for `.html, .css, js, jpg, .jpeg, .png, .gif, .swf`
* Respond to percent-encoding URLs
* No security vulnerabilities!
* **Bonus:** init script for daemonization with commands: start, stop, restart, status

## Testing ##

* `httptest` folder from `http-test-suite` repository should be copied into `DOCUMENT_ROOT`
* Your HTTP server should listen `localhost:80`
* `http://localhost/httptest/wikipedia_russia.html` must been shown correctly in browser
* Lowest-latency response (tested using `ab`, ApacheBench) in the following fashion: `ab -n 50000 -c 100 -r http://localhost:8080/`


### Functional Test Result: ###

directory index file exists ... ok
document root escaping forbidden ... ok
Send bad http headers ... ok
file located in nested folders ... ok
absent file returns 404 ... ok
urlencoded filename ... ok
file with two dots in name ... ok
query string after filename ... ok
slash after filename ... ok
filename with spaces ... ok
Content-Type for .css ... ok
Content-Type for .gif ... ok
Content-Type for .html ... ok
Content-Type for .jpeg ... ok
Content-Type for .jpg ... ok
Content-Type for .js ... ok
Content-Type for .png ... ok
Content-Type for .swf ... ok
head method support ... ok
directory index file absent ... ok
large file downloaded correctly ... ok
post method forbidden ... ok
Server header exists ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.071s

OK


Ran 1 test in 0.005s

OK

### Load Test Result: ###

httperf --port 8080 --num-conns=100 --num-calls=5000

httperf --client=0/1 --server=localhost --port=8080 --uri=/ --send-buffer=4096 --recv-buffer=16384 --ssl-protocol=auto --num-conns=100 --num-calls=5000
Maximum connect burst length: 1

Total: connections 100 requests 500000 replies 500000 test-duration 1312.659 s

Connection rate: 0.1 conn/s (13126.6 ms/conn, <=1 concurrent connections)
Connection time [ms]: min 12888.5 avg 13126.6 max 13555.9 median 13116.5 stddev 104.6
Connection time [ms]: connect 0.1
Connection length [replies/conn]: 5000.000

Request rate: 380.9 req/s (2.6 ms/req)
Request size [B]: 62.0

Reply rate [replies/s]: min 360.0 avg 380.9 max 392.0 stddev 4.2 (262 samples)
Reply time [ms]: response 2.6 transfer 0.0
Reply size [B]: header 138.0 content 0.0 footer 0.0 (total 138.0)
Reply status: 1xx=0 2xx=0 3xx=0 4xx=500000 5xx=0

CPU time [s]: user 59.30 system 1252.85 (user 4.5% system 95.4% total 100.0%)
Net I/O: 74.4 KB/s (0.6*10^6 bps)

Errors: total 0 client-timo 0 socket-timo 0 connrefused 0 connreset 0
Errors: fd-unavail 0 addrunavail 0 ftab-full 0 other 0
