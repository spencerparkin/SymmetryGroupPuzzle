// symmetric_group_puzzle.js

var gl = null;
var perm_list = null;
var current_perm_data = null;
var perm_width = 0;
var perm_height = 0;
var perm_history = [];
var main_texture = null;
var perm_texture = null;
var shader_program = null;
var vertex_buffer = null;

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

var Encode = number => {
    let lower_part = number % 256;
    let upper_part = Math.floor(number / 256);
    return [lower_part, upper_part];
}

var Decode = (lower_part, upper_part) => {
    return lower_part + 256 * upper_part;
}

var MakeIdentityPerm = () => {
    let perm_data = new Uint8Array(perm_width * perm_height * 4);
    for(let row = 0; row < perm_height; row++) {
        for(let col = 0; col < perm_width; col++) {
            let row_encoded = Encode(row);
            let col_encoded = Encode(col);
            let k = row * perm_width * 4 + col * 4;
            perm_data[k + 0] = row_encoded[0];
            perm_data[k + 1] = row_encoded[1];
            perm_data[k + 2] = col_encoded[0];
            perm_data[k + 3] = col_encoded[1];
        }
    }
    return perm_data;
}

var ConcatinatePerm = (k) => {
    let concat_perm_data = perm_list[k]['perm_data'];
    let new_perm_data = new Uint8Array(perm_width * perm_height * 4);
    for(let row = 0; row < perm_height; row++) {
        for(let col = 0; col < perm_width; col++) {
            let i = row * perm_width * 4 + col * 4;
            let other_row = Decode(concat_perm_data[i + 0], concat_perm_data[i + 1]);
            let other_col = Decode(concat_perm_data[i + 2], concat_perm_data[i + 3]);
            let j = other_row * perm_width * 4 + other_col * 4;
            other_row = Decode(current_perm_data[j + 0], current_perm_data[j + 1]);
            other_col = Decode(current_perm_data[j + 2], current_perm_data[j + 3]);
            let row_encoded = Encode(other_row);
            let col_encoded = Encode(other_col);
            new_perm_data[i + 0] = row_encoded[0];
            new_perm_data[i + 1] = row_encoded[1];
            new_perm_data[i + 2] = col_encoded[0];
            new_perm_data[i + 3] = col_encoded[1];
        }
    }
    current_perm_data = new_perm_data;
}

var PromiseLevel = level => new Promise((resolve, reject) => {
    $.ajax({
        url: 'levels/level' + level + '.json',
        dataType: 'json',
        success: level_data => {
            perm_promise_list = [];
            $.each(level_data['perm_list'], (i, perm_info) => {
                perm_promise_list.push(PromisePermutation(perm_info));
            });
            Promise.all(perm_promise_list).then((results) => {

                perm_list = [];
                $.each(results, (i, perm_info) => { perm_list.push(perm_info); });

                $('#header').text('Symmetry Group Puzzle: ' + level_data['name']);

                perm_width = level_data['perm_width'];
                perm_height = level_data['perm_height'];

                perm_history = [];

                current_perm_data = MakeIdentityPerm();
                for(let i = 0; i < 20; i++) {
                    let k = perm_list.length;
                    let j = Math.floor(Math.random() * k);
                    ConcatinatePerm(j);
                }

                RegeneratePermTexture();

                resolve();
            });
        },
        failure: error => {
            reject();
        }
    });
});

var PromisePermutation = (perm_info) => new Promise((resolve, reject) => {
    let request = new XMLHttpRequest();
    request.open('GET', perm_info['file'], true);
    request.responseType = 'arraybuffer';
    request.onload = event => {
        // TODO: We need to be able to decompress compressed versions of this data.  GZip or ZLib?
        let perm_data = request.response;
        perm_data = new Uint8Array(perm_data);
        perm_info['perm_data'] = perm_data;
        resolve(perm_info);
    }
    request.onerror = error => {
        reject();
    }
    request.send(null);
});

var RegeneratePermTexture = () => {
    if(perm_texture === null) {
        perm_texture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, perm_texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    } else {
        gl.bindTexture(gl.TEXTURE_2D, perm_texture);
    }
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, perm_width, perm_height, 0, gl.RGBA, gl.UNSIGNED_BYTE, current_perm_data);
}

var PromiseMainTexture = (i) => new Promise((resolve, reject) => {
    let image = new Image();
    image.onload = () => {
        if(main_texture !== null) {
            gl.deleteTexture(main_texture);
        }
        main_texture = gl.createTexture();

        gl.bindTexture(gl.TEXTURE_2D, main_texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);

        let canvas = $('#canvas')[0];
        canvas.width = image.width;
        canvas.height = image.height;
        canvas.style.width = image.width + 'px';
        canvas.style.height = image.height + 'px';

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

    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, perm_texture);

    gl.useProgram(shader_program);

    let mainTexSamplerLoc = gl.getUniformLocation(shader_program, 'mainTexSampler');
    gl.uniform1i(mainTexSamplerLoc, 0);

    let permTexSamplerLoc = gl.getUniformLocation(shader_program, 'permTexSampler');
    gl.uniform1i(permTexSamplerLoc, 1);

    let permWidthLoc = gl.getUniformLocation(shader_program, 'permWidth');
    let permHeightLoc = gl.getUniformLocation(shader_program, 'permHeight');
    gl.uniform1f(permWidthLoc, perm_width);
    gl.uniform1f(permHeightLoc, perm_height);

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