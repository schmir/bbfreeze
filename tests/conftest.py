import os


def pytest_configure(config):
    os.chdir(os.path.dirname(__file__))
