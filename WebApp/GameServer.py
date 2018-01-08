# GameServer.py

# The game server is going to be stateless.  The client will maintain
# the puzzle state.  We're asked to provide a new initial puzzle state,
# or to manipulate a given puzzle state to then be returned to the client.
# I believe "restful" is another term used for this approach.  Note that
# my first inclination suggests that the best way to develop this application
# is as operating completely and exclusively on the client side.  Having each
# puzzle manipulation move require a round-trip query to the server could
# potentially, under heavy network conditions, provide a bad user experience.
# I'm willing to bet, however, that in most circumstances it will be reasonable,
# so to go as far as giving it all a try.

import os
import cherrypy
import json

from Math.Vector import Vector
from Puzzle.Puzzle import Puzzle
from Puzzle.Level import MakePuzzle

class GameServer(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    @cherrypy.expose
    def default(self, **kwargs):
        return cherrypy.lib.static.serve_file(root_dir + '/SymmetryGroupPuzzle.html', content_type='text/html')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def new_puzzle(self, **kwargs):
        try:
            level = int(kwargs['level'])
            puzzle = MakePuzzle(level)
            puzzle.Scramble(50)
            data = puzzle.Serialize()
            return {'puzzle': data}
        except Exception as ex:
            return {'error': str(ex)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def mutate_puzzle(self, **kwargs):
        try:
            content_length = cherrypy.request.headers['Content-Length']
            payload = cherrypy.request.body.read(int(content_length))
            payload = payload.decode('utf-8')
            payload = json.loads(payload)
            data = payload['data']
            puzzle = Puzzle().Deserialize(data)
            point = Vector().Deserialize(payload['point'])
            type = payload['type']
            if type == 'rotation':
                i = puzzle.NearestCutter(point)
                ccw = True if payload['direction'] == 'ccw' else False
                puzzle.RotateCutter(i, ccw)
            elif type == 'reflection':
                i, j = puzzle.NearestAxisOfSymmetry(point)
                puzzle.ReflectCutter(i, j)
            data = puzzle.Serialize()
            solved = puzzle.IsSolved()
            return {'puzzle': data, 'solved': solved}
        except Exception as ex:
            return {'error': str(ex)}

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.abspath(__file__))
    port = int(os.environ.get('PORT', 5100))
    server = GameServer(root_dir)
    config = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': port,
        },
        '/': {
            'tools.staticdir.root': root_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
        }
    }
    cherrypy.quickstart(server, '/', config=config)