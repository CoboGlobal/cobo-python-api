import sys 
sys.path.append("..")
import unittest
import argparse
from cobo_custody.config import DEV_ENV
from testcase.test_client import ClientTest
from testcase.test_mpc_client import MPCClientTest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_secret", type=str, required=True)
    parser.add_argument("--mpc_api_secret", type=str, required=True)

    args = parser.parse_args()

    ClientTest.api_secret = args.api_secret
    ClientTest.env = DEV_ENV

    MPCClientTest.mpc_api_secret = args.mpc_api_secret
    MPCClientTest.env = DEV_ENV

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for testcase in (ClientTest, MPCClientTest):
        suite.addTests(loader.loadTestsFromTestCase(testcase))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
