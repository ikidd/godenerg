from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from json import dumps as json_dumps
from functools import reduce
from time import sleep
from datetime import datetime

from axpert.settings import http_conf
from axpert.protocol import CMD_REL


class BaseGodenergHandler(BaseHTTPRequestHandler):

    routes = {} 

    def do_GET(self):
        parsed_path = urlparse(self.path)
        route = parsed_path.path
        if route not in self.routes:
            self.send_response(404)
            self.wfile.write(b'Route not found')
        else:
            route_fnx = getattr(self, self.routes[route])
            route_fnx(parse_qs(parsed_path.query))


def html_response(fnx):
    def _inner(*args, **kwargs):
        self = args[0]
        try:
            response = fnx(*args, **kwargs)
            self.send_response(200)

        except Exception as e:
            response = str(e)
            self.send_response(500)
            self.log.exception(e)

        self.send_header('Content-type', 'text/html')
        self.end_headers()
        return self.wfile.write(response)

    return _inner


def json_response(fnx):
    def _inner(*args, **kwargs):
        self = args[0]

        try:
            response = fnx(*args, **kwargs)
            self.send_response(200)

        except KeyError as ke:
            self.send_response(400)
            response = dict(error=str(ke))

        except Exception as e:
            self.log.exception(e)
            self.send_response(500)
            response = dict(error=str(e))

        self.send_header('Content-type', 'application/json')
        self.end_headers()

        return self.wfile.write(
            json_dumps(response).encode()
        )

    return _inner


def http_server_create(log, comms_executor):
    http_handler = create_base_remote_cmd_handler(
        log, comms_executor, CMD_REL
    )
    server = HTTPServer(('', http_conf['port']), http_handler)
    server.serve_forever()


def create_base_remote_cmd_handler(log, comms_executor, cmds):

    class RemoteCommandsHandler(BaseRemoteCommandsHandler):

        def __init__(self, *args, **kwargs):
            self.log = log
            self.comms_executor = comms_executor
            self.cmds = cmds
            super(RemoteCommandsHandler, self).__init__(*args, **kwargs)

    return RemoteCommandsHandler


class BaseRemoteCommandsHandler(BaseGodenergHandler):

    routes = {
        '/cmds': 'get_cmds',
    }

    def execute_cmd(self, cmd_name):
        return self.cmds[cmd_name].json(
            self.comms_executor(self.cmds[cmd_name]).data,
            serialize=False
        )

    @json_response
    def get_cmds(self, req):
        '''
        - Get two commands as json in two separated
          nodes (one per command).
            * Req: /cmds?cmd=info&cmd=operation_mode
            * Res: {"info": {...}, "operation_mode": {...}}

        - Get a single command as json.
            * Req: /cmds?cmd=info
            * Res: {...}

        - Get the result of two commands merged into a single
          dictionary as json. All key/value pairs from each command
          response will be merge into the same output dictionary.
            * Req: /cmds?cmd=info&cmd=operation_mode&merge=1
            * Res: {...}
        '''
        if 'cmd' not in req or not req:
            raise KeyError(
                'Missing param "cmd" in querystring or value for param'
            )

        # If we are ask to merge (merge=1 in QS) or we have a single command.
        if ('merge' in req and req['merge'][0] == '1') or len(req['cmd']) == 1:
            data = (self.execute_cmd(cmd) for cmd in req['cmd'])
            return reduce(
                lambda merged, item: \
                    merged.update(item if item else {}) or merged,
                data, {}
            )

        else:
            return {
                cmd_name: self.execute_cmd(cmd_name) or {}
                for cmd_name in req['cmd']
            }
