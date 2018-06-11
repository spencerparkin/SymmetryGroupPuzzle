// SymmetryGroupPuzzle.js

class Puzzle {
    constructor() {
        this.mesh_list = [];
        this.window_min_point = vec2.create();
        this.window_max_point = vec2.create();
    }
    
    Promise(source) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: source,
                dataType: 'json',
                success: puzzle_data => {
                    let min_point = puzzle_data['window']['min_point'];
                    let max_point = puzzle_data['window']['max_point'];
                    set(this.window_min_point, min_point['x'], min_point['y']);
                    set(this.window_max_point, max_point['x'], max_point['y']);
                    this.mesh_list = [];
                    let mesh_promise_list = [];
                    $.each(results, (i, mesh_data) => {
                        mesh = new Mesh(mesh_data);
                        this.mesh_list.push(mesh);
                        mesh_promise_list.push(mesh.Promise(mesh_data.file));
                    });
                    Promise.all(mesh_promise_list).then(() => {
                        // TODO: Scramble the puzzle here.
                        resolve();
                    });
                },
                failure: error => {
                    alert(error);
                    reject();
                }
            });
        });
    }
    
    Render() {
    
    }
    
    IsSolved() {
        // TODO: Check that all mesh local-to-world matrices are the identity.
    }
}

class Mesh {
    constructor(mesh_data) {
        this.type = mesh_data['type'];
        this.local_to_world = mat3.create();
        this.anim_local_to_world = mat3.create();
        this.triangle_list = [];
        this.vertex_list = [];
        this.index_buffer = null;
        this.vertex_buffer = null;
        this.symmetry_list = null;
        if('symmetry_list' in mesh_data) {
            this.symmetry_list = [];
            for(let i = 0; i < mesh_data['symmetry_list'].length; i++) {
                let symmetry_data = mesh_data['symmetry_list'][i];
                let transform = Float32Array([
                    symmetry_data['linear_transform']['x_axis']['x'],
                    symmetry_data['linear_transform']['x_axis']['y'],
                    0.0,
                    symmetry_data['linear_transform']['y_axis']['x'],
                    symmetry_data['linear_transform']['y_axis']['y'],
                    0.0,
                    symmetry_data['translation']['x'],
                    symmetry_data['translation']['y'],
                    1.0
                ]);
                this.symmetry_list.push({
                    'transform': transform,
                    // TODO: Add hot-spot info?
                });
            }
        }
    }
    
    Promise(source) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: source,
                dataType: 'json',
                success: mesh_data => {
                    this.triangle_list = mesh_data.triangle_list;
                    this.vertex_list = mesh_data.vertex_list;
                    if(this.index_buffer !== null) {
                        gl.deleteBuffer(this.index_buffer);
                    }
                    this.index_buffer = gl.createBuffer();
                    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.index_buffer);
                    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, this.MakeIndexBufferData(), gl.STATIC_DRAW);
                    if(this.vertex_buffer !== null) {
                        gl.deleteBuffer(this.vertex_buffer);
                    }
                    this.vertex_buffer = gl.createBuffer();
                    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.vertex_buffer);
                    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, this.MakeVertexBufferData(), gl.STATIC_DRAW);
                },
                failure: error => {
                    alert(error);
                    reject();
                }
            });
        });
    }
    
    Render() {
    
    }
    
    MakeIndexBufferData() {
        let index_list = [];
        for(let i = 0; i < this.triangle_list.length; i++) {
            for(let j = 0; j < 3; j++) {
                index_list.push(this.triangle_list[i][j];
            }
        }
        return new Uint32Array(index_list);
    }
    
    MakeVertexBufferData() {
        let vertex_list = [];
        for(let i = 0; i < this.vertex_list; i++) {
            let vertex = this.vertex_list[i];
            vertex_list.push(vertex['x']);
            vertex_list.push(vertex['y']);
        }
        return new Float32Array(vertex_list);
    }
    
    CapturesMesh(mesh) {
        if(this.type === 'capture_mesh' && mesh.type == 'picture_mesh') {
            // The puzzle is built such that no picture mesh straddles the boundary of a capture mesh.
            // It follows that to conclude a given mesh is completely covered by the capture mesh,
            // we need only check that any arbitrarily chosen interior point of the given mesh is
            // inside any triangle of this, the capture mesh.
            let triangle = mesh.triangle_list[0];
            let point_a = mesh.vertex_list[triangle[0]];
            let point_b = mesh.vertex_list[triangle[1]];
            let point_c = mesh.vertex_list[triangle[2]];
            let interior_point = vec2.create();
            add(interior_point, point_a, point_b);
            add(interior_point, interior_point, point_c);
            scale(interior_point, interior_point, 1.0 / 3.0);
            vec2.transformMat3(interior_point, interior_point, this.local_to_world);
            for(let i = 0; i < this.triangle_list.length; i++) {
                triangle = this.triangle_list[i];
                for(let j = 0; j < 3; j++) {
                    let k = (j + 1) % 3;
                    let edge_vector = vec2.create();
                    sub(edge_vector, this.vertex_list[triangle[k]], this.vertex_list[triangle[j]]);
                    let vector = vec2.create();
                    sub(vector, interior_point, this.vertex_list[triangle[j]]);
                    vec3 result = vec3.create();
                    cross(result, edge_vector, vector);
                    if(result[2] < 0.0)
                        break;
                }
                if(j === 3)
                    return true;
            }
        }
        return false;
    }
}

var gl = null;
var puzzle = new Puzzle();
var picture_mesh_shader_program = {
    'vert_shader_source': 'Shaders/PictureVertShader.txt',
    'frag_shader_source': 'Shaders/PictureFragShader.txt',
};
var capture_mesh_shader_program = {
    'vert_shader_source': 'Shaders/CaptureVertShader.txt',
    'frag_shader_source': 'Shaders/CaptureFragShader.txt',
};
var picture_mesh_texture = {
    'source': null,
};

var OnDocumentReady = () => {
	try {
	    let canvas = $('#canvas')[0];
	    gl = canvas.getContext('webgl2');
	    if(!gl) {
	        throw 'WebGL is not available.';
	    }

	    gl.clearColor(0.0, 0.0, 0.0, 1.0);

	    $('#canvas').click(OnCanvasClicked);

        //...

	} catch(error) {
	    alert('Error: ' + error.toString());
	}
}

var OnCanvasClicked = event => {
}

var OnCanvasMouseWheel = event => {
}

var OnNewPuzzleButtonClicked = () => {
    Promise.all([
        puzzle.Promise('Puzzles/Puzzle1.json'),
        PromiseShaderProgram(picture_mesh_shader_program),
    ]).then(() => {
        //...
    });
}

var OnNewImageButtonClicked = () => {
}

$(document).ready(OnDocumentReady);