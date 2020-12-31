from py_server.genericserver import WsServer


def main():
    server = WsServer()
    server.start("localhost", 8765)


if __name__ == "__main__":
    main()
