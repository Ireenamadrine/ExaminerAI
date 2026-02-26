#!/usr/bin/env python3

from core.bootstrap import boot_app
from cli.router import route_command

def main():
    boot_app()
    route_command()

if __name__ == "__main__":
    main()
