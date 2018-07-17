# GameServer.py

import os
import cherrypy
import json

class GameServer(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    @cherrypy.expose
    def default(self, **kwargs):
        return cherrypy.lib.static.serve_file(root_dir + '/SymmetryGroupPuzzle.html', content_type='text/html')

    def _load_stab_chain(self, puzzle_number):
        from PyPermGroup import StabChain
        stab_chain_file = 'Puzzles/Puzzle%d_StabChain.json' % puzzle_number
        with open(stab_chain_file, 'r') as handle:
            json_text = handle.read()
            stab_chain = StabChain()
            stab_chain.from_json(json_text)
            return stab_chain

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def test_import(self, **kwargs):
        result = {}
        try:
            import importlib
            spec = importlib.util.find_spec('PyPermGroup')
            if spec is None:
                raise Exception('No spec found!')
            mod = importlib.util.module_from_spec(spec)
            if mod is None:
                raise Exception('Failed to create module from spec!')
            spec.loader.exec_module(mod)
        except Exception as ex:
            result['error'] = str(ex)
        return result

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def puzzle_count(self, **kwargs):
        count = 0
        while True:
            puzzle_file = self.root_dir + '/Puzzles/Puzzle%d.json' % (count + 1)
            if not os.path.exists(puzzle_file):
                break
            count += 1
        return {'puzzle_count': count}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def image_count(self, **kwargs):
        count = 0
        while True:
            puzzle_file = self.root_dir + '/Images/image%d.png' % count
            if not os.path.exists(puzzle_file):
                break
            count += 1
        return {'image_count': count}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def computer_can_solve(self, **kwargs):
        computer_can_solve = False
        try:
            puzzle_number = int(kwargs['puzzle_number'])
            stab_chain = self._load_stab_chain(puzzle_number)
            if stab_chain.worded():
                computer_can_solve = True
        except:
            pass
        return {'computer_can_solve': computer_can_solve}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def computer_solve(self, **kwargs):
        try:
            from PyPermGroup import Perm
            puzzle_number = int(kwargs['puzzle_number'])
            stab_chain = self._load_stab_chain(puzzle_number)
            permutation = Perm()
            perm_array = [int(point) for point in kwargs['permutation[]']]
            permutation.from_array(perm_array)
            inv_permutation = stab_chain.factor(permutation, True)
            generator_list = stab_chain.generators()
            data = {
                'inv_permutation': json.loads(inv_permutation.to_json()),
                'generator_list': [json.loads(generator.to_json()) for generator in generator_list]
            }
            return data
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