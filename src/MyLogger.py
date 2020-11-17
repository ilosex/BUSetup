import sys
from logging import StreamHandler


class StreamHandlerAndWindowWriter(StreamHandler):
    def __init__(self, app):
        super(StreamHandlerAndWindowWriter, self).__init__(stream=sys.stdout)
        self.app = app

    def emit(self, record):
        StreamHandler.emit(self, record)
        msg = self.format(record)
        self.app.log_window.append(msg)
        self.flush()
