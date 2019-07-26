import json
from pprint import pprint

class TestValidateJson(object):
    def test_pybytes_config(self):
        with open('../flash/pybytes_config.json.example') as f:
            json.load(f)

    def test_pybytes_project(self):
        with open('../flash/pybytes_project.json.example') as f:
            json.load(f)
