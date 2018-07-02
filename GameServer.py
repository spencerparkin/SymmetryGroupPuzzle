# GameServer.py

import os
import cherrypy

class GameServer(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    @cherrypy.expose
    def default(self, **kwargs):
        return cherrypy.lib.static.serve_file(root_dir + '/SymmetryGroupPuzzle.html', content_type='text/html')

    # TODO: Expose request to know if puzzle is solvable.  It is if a stab-chain file exists and is fully worded.
    # TODO: Expose request to solve a given permutation for a given puzzle.  Just return a list of permutations.
    #       The JS code can translate this into a sequence of moves.  The JS code can also keep track of the current
    #       permutation by multiplying permutations.

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