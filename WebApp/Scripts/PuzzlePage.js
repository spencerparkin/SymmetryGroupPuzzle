// PuzzlePage.js

var gl = null;
var puzzleState = null;
var puzzleTexture = null;
var puzzleTextureSize = null;
var puzzleTextureNumber = 0;
var puzzleShaderProgram = null;
var puzzleVertexBuffer = null;
var puzzleVertexBufferSize = 1024;
var puzzleVertexBufferStride = 8;

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
	    //$('#canvas').mousemove(OnCanvasMouseMoved);

        // Get the background image texture and the puzzle state, then render the puzzle.
        Promise.all([
            PromiseShaderProgram(),
            PromiseTexture(),
            PromisePuzzleState()
        ]).then(() => {
            RenderPuzzle();
        });

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

    let window = puzzleState.window;
    let textureAspectRatio = puzzleTextureSize.width / puzzleTextureSize.height;
    let windowWidth = window.max_point.x - window.min_point.x;
    let windowHeight = window.max_point.y - window.min_point.y;
    let windowAspectRatio = windowWidth / windowHeight;
    if(textureAspectRatio > windowAspectRatio) {
        let delta = 0.5 * (windowWidth * puzzleTextureSize.height / puzzleTextureSize.width - windowHeight);
        window.min_point.y -= delta;
        window.max_point.y += delta;
    } else {
        let delta = 0.5 * (windowHeight * puzzleTextureSize.width / puzzleTextureSize.height - windowWidth);
        window.min_point.x -= delta;
        window.max_point.x += delta;
    }

    gl.uniform2f(minPointLoc, window.min_point.x, window.min_point.y);
    gl.uniform2f(maxPointLoc, window.max_point.x, window.max_point.y);

    if(puzzleVertexBuffer === null) {
        puzzleVertexBuffer = gl.createBuffer();

        gl.bindBuffer(gl.ARRAY_BUFFER, puzzleVertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, puzzleVertexBufferSize, gl.DYNAMIC_DRAW);

        let vertexLoc = gl.getAttribLocation(puzzleShaderProgram, 'localVertex');
        gl.vertexAttribPointer(vertexLoc, 2, gl.FLOAT, false, puzzleVertexBufferStride, 0);
        gl.enableVertexAttribArray(vertexLoc);
    } else {
        gl.bindBuffer(gl.ARRAY_BUFFER, puzzleVertexBuffer);
    }

    DrawTriangles([
        {x: window.min_point.x, y: window.min_point.y},
        {x: window.max_point.x, y: window.min_point.y},
        {x: window.min_point.x, y: window.max_point.y},
        {x: window.max_point.x, y: window.min_point.y},
        {x: window.max_point.x, y: window.max_point.y},
        {x: window.min_point.x, y: window.max_point.y}
    ], [
       1.0, 0.0, 0.0,
       0.0, 1.0, 0.0,
       0.0, 0.0, 1.0
    ]);

    for(let i = 0; i < puzzleState.shape_list.length; i++) {
        let shape = puzzleState.shape_list[i];
        let linear_transform = shape.transform.linear_transform;
        let localToWorld = [
            linear_transform.xAxis.x, linear_transform.xAxis.y, 0.0,
            linear_transform.yAxis.x, linear_transform.yAxis.y, 0.0,
            shape.transform.translation.x, shape.transform.translation.y, 1.0
        ];
        let dataArray = [];
        for(let j = 0; j < shape.polygon.triangle_list.length; j++) {
            let triangle = shape.polygon.triangle_list[j];
            for(let k = 0; k < triangle.vertex_list.length; k++) {
                let vertex = triangle.vertex_list[k];
                dataArray.push({x: vertex.x, y: vertex.y});
            }
        }
        DrawTriangles(dataArray, localToWorld);
    }

    return true;
}

var DrawTriangles = (dataArray, localToWorld) => {
    let arrayBuffer = new ArrayBuffer(puzzleVertexBufferSize);
    let dataView = new DataView(arrayBuffer);

    for(let i = 0; i < dataArray.length; i++) {
        dataView.setFloat32(puzzleVertexBufferStride * i + 0, dataArray[i].x, true);
        dataView.setFloat32(puzzleVertexBufferStride * i + 4, dataArray[i].y, true);
    }

    gl.bufferSubData(gl.ARRAY_BUFFER, 0, arrayBuffer);
    let localToWorldLoc = gl.getUniformLocation(puzzleShaderProgram, 'localToWorld');
    gl.uniformMatrix3fv(localToWorldLoc, false, new Float32Array(localToWorld));
    gl.drawArrays(gl.TRIANGLES, 0, dataArray.length);
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
    image.src = 'Images/Image' + puzzleTextureNumber.toString() + '.png';
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

var GetMouseLocation = event => {
    let canvas = $('#canvas')[0];
    let context = canvas.getContext('2d');
    let rect = canvas.getBoundingClientRect();
    let lerpX = (event.clientX - rect.left) / (rect.right - rect.left);
    let lerpY = 1.0 - (event.clientY - rect.top) / (rect.bottom - rect.top);
    let window = puzzleState.window;
    let location = {
        x: window.min_point.x + lerpX * (window.max_point.x - window.min_point.x),
        y: window.min_point.y + lerpY * (window.max_point.y - window.min_point.y)
    }
    return location;
}

var OnCanvasClicked = event => {
    let location = GetMouseLocation(event);
    let promise = $.ajax({
        url: 'mutate_puzzle',
        data: JSON.stringify({
            data: puzzleState,
            point: location,
            type: 'reflection'
        }),
        type: 'POST',
        contentType: 'application/json'
    });
    HandleStateChangePromise(promise);
}

var OnCanvasMouseMoved = event => {
}

var OnCanvasMouseWheel = event => {
    let location = GetMouseLocation(event);
    let direction = event.wheelDeltaY < 0 ? 'ccw' : 'cw';
    let promise = $.ajax({
        url: 'mutate_puzzle',
        data: JSON.stringify({
            data: puzzleState,
            point: location,
            type: 'rotation',
            direction: direction
        }),
        type: 'POST',
        contentType: 'application/json'
    });
    HandleStateChangePromise(promise);
    event.preventDefault();
}

var HandleStateChangePromise = promise => {
    promise.done(json_data => {
        if(json_data.error) {
            alert('Error: ' + json_data.error);
        } else {
            puzzleState = json_data.puzzle;
            RenderPuzzle();
            if(json_data.solved) {
                alert('You are a super star!');
            }
        }
    }).fail(() => {
        alert('AJAX request failed!');    
    });
}

var OnNewPuzzleButtonClicked = () => {
}

var OnNewImageButtonClicked = () => {
    puzzleTextureNumber = (puzzleTextureNumber + 1) % 10;
    PromiseTexture().then(() => {
        RenderPuzzle();
    });
}

$(document).ready(OnDocumentReady);