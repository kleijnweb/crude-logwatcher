import argparse

from logwatcher.config import App


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', type=str, help='Path to the config YAML file')

    app = App()
    app.get_reader().read()
