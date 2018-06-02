// symmetric_group_puzzle.js

var gl = null;
var perm_list = null;
var current_perm = null;
var main_texture = null;
var perm_texture = null;
var shader_program = null;
var vertex_buffer = null;

var OnDocumentReady = () => {
	try {
	    let canvas = $('#canvas')[0];
	    gl = canvas.getContext('webgl');
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

var PromiseLevel = (level) => new Promise((resolve, reject) => {
    $.ajax({
        url: 'levels/level' + level + '.json',
        dataType: 'json',
        success: level_data => {
            perm_promise_list = [];
            $.each(level_data['permutation_list'], (i, perm_info) => {
                perm_promise_list.push(PromisePermutation(perm_info));
            });
            Promise.all(perm_promise_list).then((results) => {

                perm_list = [];
                $.each(results, (i, perm_info) => { perm_list.push(perm_info); });

                $('#header').text('Symmetry Group Puzzle: ' + level_data['name']);

                let width = level_data['image_width'];
                let height = level_data['image_height'];

                let canvas = $('#canvas')[0];
                canvas.width = width;
                canvas.height = height;
                canvas.style.width = width + 'px';
                canvas.style.height = height + 'px';

                current_perm = new Image(width, height);
                // TODO: Scramble current permutation.

                resolve();
            });
        },
        failure: error => {
            reject();
        }
    });
});

var PromisePermutation = (perm_info) => new Promise((resolve, reject) => {
    let perm_image = new Image();
    perm_info['image'] = perm_image;
    perm_image.onload = () => { resolve(perm_info); }
    perm_image.onerror = () => { reject(); }
    perm_image.src = perm_info['file'];
});

var PromiseMainTexture = (i) => new Promise((resolve, reject) => {
    let image = new Image();
    image.onload = () => {
        if(main_texture !== null) {
            gl.deleteTexture(main_texture);
        }
        main_texture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, main_texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        resolve();
    }
    image.src = 'images/Image' + i.toString() + '.png';
});

var PromiseShaderProgram = () => new Promise((resolve, reject) => {
    Promise.all([
        PromiseShader('shaders/VertShader.txt', gl.VERTEX_SHADER),
        PromiseShader('shaders/FragShader.txt', gl.FRAGMENT_SHADER)
    ]).then((results) => {
        let vertexShader = results[0];
        let fragmentShader = results[1];
        if(shader_program !== null) {
            gl.deleteProgram(shader_program);
        }
        shader_program = gl.createProgram();
        gl.attachShader(shader_program, vertexShader);
        gl.attachShader(shader_program, fragmentShader);
        gl.linkProgram(shader_program);
        if(!gl.getProgramParameter(shader_program, gl.LINK_STATUS)) {
            let error = gl.getProgramInfoLog(shader_program);
            gl.deleteProgram(shader_program);
            alert('Error: ' + error.toString());
            reject();
        } else {
            resolve();
        }
    });
});

var PromiseShader = (source, type) => new Promise((resolve, reject) => {
    $.get(source, (text) => {
        let shader = gl.createShader(type);
        gl.shaderSource(shader, text);
        gl.compileShader(shader);
        if(!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            let error = gl.getShaderInfoLog(shader);
            gl.deleteShader(shader);
            alert('Error: ' + error.toString());
            reject();
        } else {
            resolve(shader);
        }
    });
});

var RenderLevel = () => {
    gl.viewport(0, 0, 512, 512);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, main_texture);

    gl.useProgram(shader_program);

    let mainTexSamplerLoc = gl.getUniformLocation(shader_program, 'mainTexSampler');
    gl.uniform1i(mainTexSamplerLoc, 0);

    if(vertex_buffer === null) {
        vertex_buffer = gl.createBuffer();

        var vertex_buffer_data = new Float32Array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, -1.0,
            1.0, 1.0,
            -1.0, 1.0,
            // OpenGL is going off the end of the buffer, so add some padding.  Hmmm...
            0.0, 0.0,
        ]);

        gl.bindBuffer(gl.ARRAY_BUFFER, vertex_buffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertex_buffer_data, gl.STATIC_DRAW);

        let vertexLoc = gl.getAttribLocation(shader_program, 'vertex');
        gl.vertexAttribPointer(vertexLoc, 2, gl.FLOAT, false, 8, 0);
        gl.enableVertexAttribArray(vertexLoc);
    } else {
        gl.bindBuffer(gl.ARRAY_BUFFER, vertex_buffer);
    }

    gl.drawArrays(gl.TRIANGLES, 0, 6);
}

var OnCanvasClicked = event => {
}

var OnCanvasMouseWheel = event => {
}

var OnNewPuzzleButtonClicked = () => {
    Promise.all([
        PromiseShaderProgram(),
        PromiseMainTexture(0),
        PromiseLevel(0)
    ]).then(() => {
        RenderLevel();
    });
}

var OnNewImageButtonClicked = () => {
}

$(document).ready(OnDocumentReady);