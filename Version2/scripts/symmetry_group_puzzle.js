// symmetric_group_puzzle.js

var gl = null;
var perm_list = null;
var current_perm = null;

var OnDocumentReady = () => {
	try {
	    let canvas = $('#canvas')[0];
	    gl = canvas.getContext('webgl');
	    if(!gl) {
	        throw 'WebGL is not available.';
	    }

	    gl.clearColor(0.0, 0.0, 0.0, 1.0);

	    $('#canvas').click(OnCanvasClicked);



	} catch(error) {
	    alert('Error: ' + error.toString());
	}
}

var PromiseLevel = (level) => new Promise((resolve, reject) => {
    $.ajax({
        url: 'levels/level' + level + '.json',
        dataType: 'json',
        success: (level_data) => {
            if(level_data.error) {
                alert(level_data.error);
                reject();
            } else {
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
            }
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

var RenderLevel = () => {
}

var OnCanvasClicked = event => {
}

var OnCanvasMouseWheel = event => {
}

var OnNewPuzzleButtonClicked = () => {
    Promise.all([
        PromiseLevel(0)
    ]).then(() => {
        RenderLevel();
    });
}

var OnNewImageButtonClicked = () => {
}

$(document).ready(OnDocumentReady);