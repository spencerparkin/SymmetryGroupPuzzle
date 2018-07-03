# GameServer.py

import os
import cherrypy

from PyPermGroup import Perm, StabChain

class GameServer(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    @cherrypy.expose
    def default(self, **kwargs):
        return cherrypy.lib.static.serve_file(root_dir + '/SymmetryGroupPuzzle.html', content_type='text/html')

    def LoadStabChain(self, puzzle_number):
        stab_chain_file = 'Puzzles/Puzzle%d_StabChain.json' % puzzle_number
        with open(stab_chain_file, 'r') as handle:
            json_text = handle.read()
            stab_chain = StabChain()
            stab_chain.from_json(json_text)
            return stab_chain

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def computer_can_solve(self, **kwargs):
        computer_can_solve = False
        try:
            puzzle_number = int(kwargs['puzzle_number'])
            stab_chain = self.LoadStabChain(puzzle_number)
            if stab_chain.worded():
                computer_can_solve = True
        except:
            pass
        return {'computer_can_solve': computer_can_solve}

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