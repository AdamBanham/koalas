import os 
# cheap trick to get a variable to all tests
## change below to be 'False' will mean that tests take some time (>10sec) will 
## be run, however to avoid these tests set the below to 'True'.
## tested affected by this setting have a decorator of 
## @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
os.environ['SKIP_SLOW_TESTS'] = 'False'