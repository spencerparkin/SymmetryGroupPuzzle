// PuzzlePage.js

var gl = null;
var puzzle = null;
var texture = null;
var shaderProgram = null;

var OnDocumentReady = () => {
	try {
	    // Create our OpenGL drawing context.
	    let canvas = $('#canvas')[0];
	    gl = canvas.getContext('webgl');
	    if(!gl) {
	        throw 'WebGL is not available.';
	    }

	    // Initialize some OpenGL state.
	    gl.viewport(0, 0, canvas.width, canvas.height);
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
    //...render on canvas as a function of the texture and the puzzle JSON blob...
    //...should i try to look into a 2D math library for JS?...
}

var PromisePuzzleState = () => new Promise((resolve, reject) => {
    $.getJSON('new_puzzle', {'level': 0}, json_data => {
        if(json_data.error) {
            alert(json_data.error);
            reject();
        } else {
            puzzle = json_data.puzzle;
            resolve();
        }
    });
});

var PromiseTexture = () => new Promise((resolve, reject) => {
    if(texture !== null) {
        gl.deleteTexture(texture);
        texture = null;
    }
    let image = new Image();
    image.onload = () => {
        texture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
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
        let shaderProgram = gl.createProgram();
        gl.attachShader(shaderProgram, vertexShader);
        gl.attachShader(shaderProgram, fragementShader);
        gl.linkProgram(shaderProgram);
        if(!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
            let error = gl.getProgramInfoLog(shaderProgram);
            gl.deleteProgram(shaderProgram);
            alert('Error: ' + error.toString());
            reject();
        }
        resolve(shaderProgram);
    });
});

var PromiseShader = (source, type) => new Promise((resolve, reject) => {
    $.get(source, (text) => {
        let shader = gl.createShader(type);
        gl.shaderSource(shader, text);
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
    // debug...
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