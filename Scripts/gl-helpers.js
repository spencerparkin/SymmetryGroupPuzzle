// gl-helpers.js

var PromiseShaderProgram = (shader_program) => new Promise((resolve, reject) => {
    Promise.all([
        PromiseShader(shader_program.vert_shader_source, gl.VERTEX_SHADER),
        PromiseShader(shader_program.frag_shader_source, gl.FRAGMENT_SHADER)
    ]).then((results) => {
        let vert_shader = results[0];
        let frag_shader = results[1];
        if(shader_program.program !== null) {
            gl.deleteProgram(shader_program.program);
        }
        shader_program.program = gl.createProgram();
        gl.attachShader(shader_program.program, vert_shader);
        gl.attachShader(shader_program.program, frag_shader);
        gl.linkProgram(shader_program.program);
        if(!gl.getProgramParameter(shader_program.program, gl.LINK_STATUS)) {
            let error = gl.getProgramInfoLog(shader_program.program);
            gl.deleteProgram(shader_program.program);
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

var PromiseTexture = (texture) => new Promise((resolve, reject) => {
    let image = new Image();
    image.onload = () => {
        if(texture.tex !== null) {
            gl.deleteTexture(texture.tex);
        }
        texture.tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, texture.tex);
        if(texture.setup === undefined) {
            gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
            gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        } else {
            texture.setup(image);
        }
        resolve();
    }
    image.src = texture.source;
});