import sys

from PyQt5.QtWidgets import QApplication

import logger
from app.player import MusicPlayer


def main():
    logger.boot()
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
