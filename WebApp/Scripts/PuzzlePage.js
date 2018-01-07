// PuzzlePage.js

var gl = null;
var puzzleState = null;
var puzzleTexture = null;
var puzzleTextureSize = null;
var puzzleShaderProgram = null;
var puzzleVertexBuffer = null;
var puzzleVertexBufferSize = 1024;

var OnDocumentReady = () => {
	try {
	    // Create our OpenGL drawing context.
	    let canvas = $('#canvas')[0];
	    gl = canvas.getContext('webgl');
	    if(!gl) {
	        throw 'WebGL is not available.';
	    }

	    // Initialize some OpenGL state.
	    gl.clearColor(0.0, 0.0, 0.0, 1.0);

	    // Register some canvas callbacks.
	    $('#canvas').click(OnCanvasClicked);
	    /*$('#canvas').mousemove(OnCanvasMouseMoved);
        $('#canvas').bind('mousewheel', OnCanvasMouseWheel)*/

        // Get the background image texture and the puzzle state, then render the puzzle.
        /*Promise.all([
            PromiseShaderProgram(),
            PromiseTexture(),
            PromisePuzzleState()
        ]).then(() => {
            RenderPuzzle();
        });*/

	} catch(error) {
	    alert('Error: ' + error.toString());
	}
}

var RenderPuzzle = () => {
    if(puzzleState === null || puzzleShaderProgram === null || puzzleTexture === null) {
        return false;
    }

    let canvas = $('#canvas')[0];
    canvas.width = puzzleTextureSize.width;
    canvas.height = puzzleTextureSize.height;
    canvas.style.width = puzzleTextureSize.width + 'px';
    canvas.style.height = puzzleTextureSize.height + 'px';

    gl.viewport(0, 0, puzzleTextureSize.width, puzzleTextureSize.height);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, puzzleTexture);

    gl.useProgram(puzzleShaderProgram);

    let texSamplerLoc = gl.getUniformLocation(puzzleShaderProgram, 'texSampler');
    gl.uniform1i(texSamplerLoc, 0);

    let minPointLoc = gl.getUniformLocation(puzzleShaderProgram, 'minPoint');
    let maxPointLoc = gl.getUniformLocation(puzzleShaderProgram, 'maxPoint');

    // TODO: Expand window of puzzle to match aspect ratio of the texture/canvas.
    let window = puzzleState.window;

    gl.uniform2f(minPointLoc, window.min_point.x, window.min_point.y);
    gl.uniform2f(maxPointLoc, window.max_point.x, window.max_point.y);

    let localToWorldLoc = gl.getUniformLocation(puzzleShaderProgram, 'localToWorld');
    let stride = 16; // 4 bytes per component (32-bit floats), 2 components per vector, 2 vectors per vertex.

    if(puzzleVertexBuffer === null) {
        puzzleVertexBuffer = gl.createBuffer();

        gl.bindBuffer(gl.ARRAY_BUFFER, puzzleVertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, puzzleVertexBufferSize, gl.DYNAMIC_DRAW);

        let vertexLoc = gl.getAttribLocation(puzzleShaderProgram, 'localVertex');
        gl.vertexAttribPointer(vertexLoc, 2, gl.FLOAT, false, stride, 0);
        gl.enableVertexAttribArray(vertexLoc);

        let texCoordLoc = gl.getAttribLocation(puzzleShaderProgram, 'texCoord');
        gl.vertexAttribPointer(texCoordLoc, 2, gl.FLOAT, false, stride, 8);
        gl.enableVertexAttribArray(texCoordLoc);
    } else {
        gl.bindBuffer(gl.ARRAY_BUFFER, puzzleVertexBuffer);
    }

    let dataArray =
    [
        {x: window.min_point.x, y: window.min_point.y, u: 0.0, v: 0.0},
        {x: window.max_point.x, y: window.min_point.y, u: 1.0, v: 0.0},
        {x: window.min_point.x, y: window.max_point.y, u: 0.0, v: 1.0},
        {x: window.max_point.x, y: window.min_point.y, u: 1.0, v: 0.0},
        {x: window.max_point.x, y: window.max_point.y, u: 1.0, v: 1.0},
        {x: window.min_point.x, y: window.max_point.y, u: 0.0, v: 1.0}
    ];

    let arrayBuffer = new ArrayBuffer(puzzleVertexBufferSize);
    let dataView = new DataView(arrayBuffer);

    for(let i = 0; i < dataArray.length; i++) {
        dataView.setFloat32(stride * i + 0, dataArray[i].x, true);
        dataView.setFloat32(stride * i + 4, dataArray[i].y, true);
        dataView.setFloat32(stride * i + 8, dataArray[i].u, true);
        dataView.setFloat32(stride * i + 12, dataArray[i].v, true);
    }

    gl.bufferSubData(gl.ARRAY_BUFFER, 0, arrayBuffer);

    let localToWorld = new Float32Array([
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0
    ]);

    gl.uniformMatrix3fv(localToWorldLoc, false, localToWorld);
    gl.drawArrays(gl.TRIANGLES, 0, 6);

    return true;
}

var PromisePuzzleState = () => new Promise((resolve, reject) => {
    $.getJSON('new_puzzle', {'level': 0}, json_data => {
        if(json_data.error) {
            alert(json_data.error);
            reject();
        } else {
            puzzleState = json_data.puzzle;
            resolve();
        }
    });
});

var PromiseTexture = () => new Promise((resolve, reject) => {
    let image = new Image();
    image.onload = () => {
        if(puzzleTexture !== null) {
            gl.deleteTexture(puzzleTexture);
        }
        puzzleTexture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, puzzleTexture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        puzzleTextureSize = {width: image.width, height: image.height};
        resolve();
    }
    image.onerror = () => {
        reject();
    }
    image.src = 'Images/Image0.png';
});

var PromiseShaderProgram = () => new Promise((resolve, reject) => {
    Promise.all([
        PromiseShader('Shaders/PuzzlePageVertShader.txt', gl.VERTEX_SHADER),
        PromiseShader('Shaders/PuzzlePageFragShader.txt', gl.FRAGMENT_SHADER)
    ]).then((results) => {
        let vertexShader = results[0];
        let fragmentShader = results[1];
        if(puzzleShaderProgram !== null) {
            gl.deleteProgram(puzzleShaderProgram);
        }
        puzzleShaderProgram = gl.createProgram();
        gl.attachShader(puzzleShaderProgram, vertexShader);
        gl.attachShader(puzzleShaderProgram, fragmentShader);
        gl.linkProgram(puzzleShaderProgram);
        if(!gl.getProgramParameter(puzzleShaderProgram, gl.LINK_STATUS)) {
            let error = gl.getProgramInfoLog(puzzleShaderProgram);
            gl.deleteProgram(puzzleShaderProgram);
            alert('Error: ' + error.toString());
            reject();
        }
        resolve();
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

var OnCanvasClicked = event => {
    Promise.all([
        PromiseShaderProgram(),
        PromiseTexture(),
        PromisePuzzleState()
    ]).then(() => {
        RenderPuzzle();
    });
}

var OnCanvasMouseMoved = event => {
}

var OnCanvasMouseWheel = event => {
    alert('Wheel!');
}

$(document).ready(OnDocumentReady);