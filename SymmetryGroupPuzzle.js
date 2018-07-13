// SymmetryGroupPuzzle.js

// TODO: Once the puzzle mechanics are working, it would be really nice to have undo/redo.

class Puzzle {
    constructor() {
        this.mesh_list = [];
        this.window_min_point = vec2.create();
        this.window_max_point = vec2.create();
        this.highlight_mesh = -1;
        this.move_queue = [];
        this.permutation = [];
        this.animation_lerp = 0.05;
    }
    
    PromiseComputerCanSolve(puzzle_number) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: 'computer_can_solve',
                dataType: 'json',
                data: {'puzzle_number': puzzle_number},
                contentType: 'application/json',
                type: 'GET',
                success: json_data => {
                    if(json_data['computer_can_solve'])
                        $('#solve_button').show();
                    else
                        $('#solve_button').hide();
                    resolve();
                },
                failure: error => {
                    alert(error);
                    reject();
                }
            });
        });
    }
    
    PromiseComputerSolve(puzzle_number) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: 'computer_solve',
                dataType: 'json',
                data: {'puzzle_number': puzzle_number, 'permutation': this.permutation},
                contentType: 'application/json',
                type: 'GET',
                success: json_data => {
                    resolve(json_data);
                },
                failure: error => {
                    alert(error);
                    reject();
                }
            });
        });
    }
    
    Promise(source) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: source,
                dataType: 'json',
                success: puzzle_data => {
                    let min_point = puzzle_data['window']['min_point'];
                    let max_point = puzzle_data['window']['max_point'];
                    vec2.set(this.window_min_point, min_point['x'], min_point['y']);
                    vec2.set(this.window_max_point, max_point['x'], max_point['y']);
                    for(let i = 0; i < this.mesh_list.length; i++)
                        this.mesh_list[i].ReleaseBuffers();
                    this.mesh_list = [];
                    let mesh_promise_list = [];
                    $.each(puzzle_data['mesh_list'], (i, mesh_data) => {
                        let mesh = new Mesh(mesh_data);
                        this.mesh_list.push(mesh);
                        mesh_promise_list.push(mesh.Promise('Puzzles/' + mesh_data.file));
                    });
                    Promise.all(mesh_promise_list).then(() => {
                        this.permutation = [];
                        //this.QueueScrambleMoves(50);
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
        let animation_enabled = $('#animation_check').is(':checked');
        let canvas = $('#canvas')[0];
        
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, picture_mesh_texture.tex);
        
        gl.useProgram(mesh_shader_program.program);
        
        let texSamplerLoc = gl.getUniformLocation(mesh_shader_program.program, 'texSampler');
        gl.uniform1i(texSamplerLoc, 0);
        
        let minPointLoc = gl.getUniformLocation(mesh_shader_program.program, 'minPoint');
        gl.uniform2fv(minPointLoc, this.window_min_point);
        
        let maxPointLoc = gl.getUniformLocation(mesh_shader_program.program, 'maxPoint');
        gl.uniform2fv(maxPointLoc, this.window_max_point);
        
        let localToWorldLoc = gl.getUniformLocation(mesh_shader_program.program, 'localToWorld');
        let localVertexLoc = gl.getAttribLocation(mesh_shader_program.program, 'localVertex');

        let blendFactorLoc = gl.getUniformLocation(mesh_shader_program.program, 'blend_factor');
        gl.uniform4f(blendFactorLoc, 1.0, 1.0, 1.0, 1.0);

        let constColorLoc = gl.getUniformLocation(mesh_shader_program.program, 'const_color');
        gl.uniform4f(constColorLoc, 1.0, 0.0, 0.0, 0.9);

        for(let i = 0; i < this.mesh_list.length; i++) {
            let mesh = this.mesh_list[i];
            if(mesh.type === 'picture_mesh') {
                mesh.Render(localVertexLoc, localToWorldLoc, animation_enabled);
            }
        }

        // Now blend the capture mesh we would like to highlight.
        if(this.highlight_mesh >= 0) {
            gl.uniform4f(blendFactorLoc, 0.0, 0.0, 0.0, 0.0);
            let mesh = this.mesh_list[this.highlight_mesh];
            gl.lineWidth(5.0); // Unfortunately, I don't think this is supported.
            mesh.Render(localVertexLoc, localToWorldLoc, false, false, true);
        }
    }
    
    AnimationSettled() {
        let animation_enabled = $('#animation_check').is(':checked');
        if(!animation_enabled)
            return true;
        else {
            for(let i = 0; i < this.mesh_list.length; i++) {
                let mesh = this.mesh_list[i];
                if(mesh.type === 'picture_mesh' && !mesh.AnimationSettled())
                    return false;
            }
            return true;
        }
    }
    
    AdvanceAnimation(snap=false) {
        for(let i = 0; i < this.mesh_list.length; i++) {
            let mesh = this.mesh_list[i];
            if(mesh.type === 'picture_mesh')
                mesh.AdvanceAnimation(snap, this.animation_lerp)
        }
    }
    
    ApplyMove(move) {
        let capture_mesh = this.mesh_list[move[0]];
        let symmetry = capture_mesh.symmetry_list[move[1]];
        for(let i = 0; i < this.mesh_list.length; i++) {
            let mesh = this.mesh_list[i];
            if(mesh.type === 'picture_mesh' && capture_mesh.CapturesMesh(mesh)) {
                mat3.mul(mesh.local_to_world, symmetry, mesh.local_to_world);
                // TODO: Re-orthonormalize the mesh transform here to combat accumulated round-off error?
            }
        }
        
        if(capture_mesh.perm_list.length > 0) {
            let symmetry_perm = capture_mesh.perm_list[move[1]];
            this.permutation = this.MultiplyPerms(symmetry_perm, this.permutation);
        }
    }
    
    QueueScrambleMoves(count) {
        let capture_mesh_list = [];
        for(let i = 0; i < this.mesh_list.length; i++) {
            let mesh = this.mesh_list[i];
            if(mesh.type === 'capture_mesh')
                capture_mesh_list.push(i);
        }
        let last_j = -1;
        for(let i = 0; i < count; i++) {
            let j = 0;
            do {
                j = Math.floor(Math.random() * capture_mesh_list.length);
            } while(j === last_j);
            last_j = j;
            j = capture_mesh_list[j];
            let mesh = this.mesh_list[j];
            let k = Math.floor(Math.random() * mesh.symmetry_list.length);
            this.move_queue.push([j, k]);
        }
    }
    
    QueueSolutionMoves(puzzle_number) {
        $('body').css('cursor', 'progress');
        this.FlushMoveQueue();
        this.PromiseComputerSolve(puzzle_number).then(json_data => {
            $('body').css('cursor', 'default');
            let move_map = {};
            for(let i = 0; i < json_data['generator_list'].length; i++) {
                let generator = json_data['generator_list'][i];
                let found = false;
                for(let j = 0; j < this.mesh_list.length; j++) {
                    let mesh = this.mesh_list[j];
                    if(mesh.type !== 'capture_mesh')
                        continue;
                    for(let k = 0; k < mesh.perm_list.length; k++) {
                        let perm = mesh.perm_list[k];
                        if(this.EqualPerms(perm, generator['map'])) {
                            move_map[generator['word'][0]['name']] = [j, k];
                            found = true;
                            break;
                        }
                    }
                    if(found)
                        break;
                }
                if(!found) {
                    alert('Error!  Generator permutation not found.');
                    return;
                }
            }
            let inv_perm = json_data['inv_permutation'];
            let identity = this.MultiplyPerms(this.permutation, inv_perm['map']);
            if(!this.IsIdentityPerm(identity)) {
                alert('Solve failed!');
                return;
            }
            let move_sequence = [];
            for(let i = inv_perm['word'].length - 1; i >= 0; i--) {
                let element = inv_perm['word'][i];
                for(let j = 0; j < Math.abs(element['exponent']); j++) {
                    let move = move_map[element['name']];
                    // Reflections are their own inverse.  The only 2 rotations (the first two)
                    // are inverses of one another, so we can easily invert the move here.
                    // If there is only 1 symmetry of the shape, however, it is a reflection.
                    if(element['exponent'] < 0 && move[1] < 2 && this.mesh_list[move[0]].perm_list.length > 1) {
                        move = [move[0], 1 - move[1]];
                    }
                    move_sequence.push(move);
                }
            }
            let count = move_sequence.length;
            if(confirm('The computer found a solution with ' + count.toString() + ' move(s).  Show solution sequence?')) {
                this.move_queue = this.move_queue.concat(move_sequence);
            }
        });
    }
    
    ProcessNextMove() {
        let move = this.move_queue.pop();
        this.ApplyMove(move);
    }
    
    FlushMoveQueue() {
        while(this.move_queue.length > 0) {
            this.ProcessNextMove();
        }
    }
    
    EvalPerm(perm, input) {
        let output = input < perm.length ? perm[input] : input;
        return output;
    }
    
    MultiplyPerms(perm_a, perm_b) {
        let size = perm_a.length > perm_b.length ? perm_a.length : perm_b.length;
        let new_perm = [];
        for(let i = 0; i < size; i++) {
            let j = this.EvalPerm(perm_b, i);
            let k = this.EvalPerm(perm_a, j);
            new_perm.push(k);
        }
        return new_perm;
    }
    
    EqualPerms(perm_a, perm_b) {
        let size = perm_a.length > perm_b.length ? perm_a.length : perm_b.length;
        for(let i = 0; i < size; i++) {
            let j = this.EvalPerm(perm_a, i);
            let k = this.EvalPerm(perm_b, i);
            if(j !== k)
                return false;
        }
        return true;
    }
    
    IsIdentityPerm(perm) {
        for(let i = 0; i < perm.length; i++) {
            let j = perm[i];
            if(i !== j)
                return false;
        }
        return true;
    }
    
    IsSolved(sanity_check=false) {
        for(let i = 0; i < this.mesh_list.length; i++) {
            let mesh = this.mesh_list[i];
            if(mesh.type === 'picture_mesh' && !mesh.IsSolved())
                return false;
        }
        
        if(sanity_check && !this.IsIdentityPerm(this.permutation)) {
            // When this happens, it can mean that the real group of the puzzle is a factor
            // group of the group that we computed for the puzzle.
            alert('Puzzle physically solved, but we are not at the identity permutation!')
            return false;
        }
        
        return true;
    }

    CalcMouseLocation(event) {
        let canvas = $('#canvas')[0];
        let context = canvas.getContext('2d');
        let rect = canvas.getBoundingClientRect();
        let lerpX = (event.clientX - rect.left) / (rect.right - rect.left);
        let lerpY = 1.0 - (event.clientY - rect.top) / (rect.bottom - rect.top);
        let lerp_vec = vec2.create();
        vec2.set(lerp_vec, lerpX, lerpY);
        let location = vec2.create();
        vec2.sub(location, this.window_max_point, this.window_min_point);
        vec2.mul(location, location, lerp_vec);
        vec2.add(location, location, this.window_min_point);
        //console.log(location[0].toString() + ', ' + location[1].toString());
        return location;
    }

    FindCaptureMeshContainingPoint(point) {
        let smallest_area = 999999.0;
        let j = -1;
        for(let i = 0; i < this.mesh_list.length; i++) {
            let mesh = this.mesh_list[i];
            if(mesh.type === 'capture_mesh' && mesh.ContainsPoint(point)) {
                let area = mesh.CalcArea();
                if(area < smallest_area) {
                    smallest_area = area;
                    j = i;
                }
            }
        }
        return j;
    }
}

class Mesh {
    constructor(mesh_data) {
        this.type = mesh_data['type'];
        this.local_to_world = mat3.create();
        this.anim_local_to_world = mat3.create();
        this.center = vec2.create();
        this.triangle_list = [];
        this.vertex_list = [];
        this.index_buffer = null;
        this.vertex_buffer = null;
        this.line_vertex_buffer = null;
        this.line_count = 0;
        if('symmetry_list' in mesh_data) {
            this.symmetry_list = [];
            for(let i = 0; i < mesh_data['symmetry_list'].length; i++) {
                let symmetry_data = mesh_data['symmetry_list'][i];
                let transform = new Float32Array([
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
                this.symmetry_list.push(transform);
            }
        }
        if('permutation_list' in mesh_data) {
            this.perm_list = mesh_data['permutation_list'];
        }
    }

    ReleaseBuffers() {
        if(this.index_buffer !== null) {
            gl.deleteBuffer(this.index_buffer);
            this.index_buffer = null;
        }
        if(this.vertex_buffer !== null) {
            gl.deleteBuffer(this.vertex_buffer);
            this.vertex_buffer = null;
        }
        if(this.line_vertex_buffer !== null) {
            gl.deleteBuffer(this.line_vertex_buffer);
            this.line_vertex_buffer = null;
        }
    }
    
    Promise(source) {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: source,
                dataType: 'json',
                success: mesh_data => {
                    this.ReleaseBuffers();
                    this.triangle_list = mesh_data.mesh.triangle_list;
                    this.vertex_list = mesh_data.mesh.vertex_list;
                    this.index_buffer = gl.createBuffer();
                    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.index_buffer);
                    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, this.MakeIndexBufferData(), gl.STATIC_DRAW);
                    this.vertex_buffer = gl.createBuffer();
                    gl.bindBuffer(gl.ARRAY_BUFFER, this.vertex_buffer);
                    gl.bufferData(gl.ARRAY_BUFFER, this.MakeVertexBufferData(), gl.STATIC_DRAW);
                    this.CalcCenter();
                    if('outline' in mesh_data) {
                        this.line_vertex_buffer = gl.createBuffer();
                        gl.bindBuffer(gl.ARRAY_BUFFER, this.line_vertex_buffer);
                        gl.bufferData(gl.ARRAY_BUFFER, this.MakeLineVertexBufferData(mesh_data.outline), gl.STATIC_DRAW);
                    }
                    resolve();
                },
                failure: error => {
                    alert(error);
                    reject();
                }
            });
        });
    }
    
    CalcCenter() {
        vec2.set(this.center, 0.0, 0.0);
        for(let i = 0; i < this.vertex_list.length; i++)
            vec2.add(this.center, this.center, this.GetVertex(i));
        vec2.scale(this.center, this.center, 1.0 / this.vertex_list.length);
    }
    
    Render(localVertexLoc, localToWorldLoc, animation_enabled, render_mesh=true, render_outline=false) {
        let local_to_world = this.local_to_world;
        if(animation_enabled)
            local_to_world = this.anim_local_to_world;
        
        gl.uniformMatrix3fv(localToWorldLoc, false, local_to_world);
        
        if(render_mesh) {
            gl.bindBuffer(gl.ARRAY_BUFFER, this.vertex_buffer);
            gl.vertexAttribPointer(localVertexLoc, 2, gl.FLOAT, false, 8, 0);
            gl.enableVertexAttribArray(localVertexLoc);
            
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.index_buffer);
            
            gl.drawElements(gl.TRIANGLES, this.triangle_list.length * 3, gl.UNSIGNED_SHORT, 0);
        }
        
        if(render_outline && this.line_vertex_buffer !== null) {
            gl.bindBuffer(gl.ARRAY_BUFFER, this.line_vertex_buffer);
            gl.vertexAttribPointer(localVertexLoc, 2, gl.FLOAT, false, 8, 0);
            gl.enableVertexAttribArray(localVertexLoc);
            
            gl.drawArrays(gl.LINES, 0, this.line_count * 2);
        }
    }
    
    IsSolved() {
        let eps = 0.001;
        for(let i = 0; i < 9; i++) {
            let value = 0.0;
            if(i === 0 || i === 4 || i === 8)
                value = 1.0;
            if(Math.abs(this.local_to_world[i] - value) >= eps)
                return false;
        }
        return true;
    }
    
    AnimationSettled() {
        let epsilon = 0.001;
        let diff_mat = mat3.create();
        mat3.subtract(diff_mat, this.anim_local_to_world, this.local_to_world);
        let i = 0;
        let j = 0;
        for(i = 0; i < 9; i++) {
            let diff = diff_mat[i];
            if(Math.abs(diff) < epsilon)
                j++;
        }
        if(j == i) {
            mat3.copy(this.anim_local_to_world, this.local_to_world);
            return true;
        }
        return false;
    }
    
    AdvanceAnimation(snap=false, lerp=0.1) {
        if(snap) {
            mat3.copy(this.anim_local_to_world, this.local_to_world);
        } else {
            let anim_x_axis = vec2.create();
            let anim_y_axis = vec2.create();
            
            vec2.set(anim_x_axis, this.anim_local_to_world[0], this.anim_local_to_world[1]);
            vec2.set(anim_y_axis, this.anim_local_to_world[3], this.anim_local_to_world[4]);
            
            let target_x_axis = vec2.create();
            let target_y_axis = vec2.create();
            
            vec2.set(target_x_axis, this.local_to_world[0], this.local_to_world[1]);
            vec2.set(target_y_axis, this.local_to_world[3], this.local_to_world[4]);
            
            anim_x_axis = this.Slerp(anim_x_axis, target_x_axis, lerp);
            anim_y_axis = this.Slerp(anim_y_axis, target_y_axis, lerp);
            
            let center0 = vec2.create();
            let center1 = vec2.create();
            
            vec2.transformMat3(center0, this.center, this.anim_local_to_world);
            vec2.transformMat3(center1, this.center, this.local_to_world);
            
            let interpolated_center = vec2.create();
            vec2.lerp(interpolated_center, center0, center1, lerp);
            
            let interpolated_orient = mat2.create();
            interpolated_orient[0] = anim_x_axis[0];
            interpolated_orient[1] = anim_x_axis[1];
            interpolated_orient[2] = anim_y_axis[0];
            interpolated_orient[3] = anim_y_axis[1];
            
            let anim_translation = vec2.create();
            vec2.transformMat2(anim_translation, this.center, interpolated_orient);
            vec2.scale(anim_translation, anim_translation, -1.0);
            vec2.add(anim_translation, anim_translation, interpolated_center);
            
            this.anim_local_to_world[0] = anim_x_axis[0];
            this.anim_local_to_world[1] = anim_x_axis[1];
            this.anim_local_to_world[3] = anim_y_axis[0];
            this.anim_local_to_world[4] = anim_y_axis[1];
            this.anim_local_to_world[6] = anim_translation[0];
            this.anim_local_to_world[7] = anim_translation[1];
        }
    }
    
    Slerp(normal_a, normal_b, lerp) {
        let epsilon = 0.0001;
        let result = vec2.create();
        let dot = vec2.dot(normal_a, normal_b);
        if(Math.abs(dot + 1.0) < epsilon) {
            let rot_mat = mat2.create();
            mat2.fromRotation(rot_mat, Math.PI * lerp);
            vec2.transformMat2(result, normal_a, rot_mat);
        } else if(Math.abs(dot - 1.0) < epsilon) {
            vec2.copy(result, normal_b);
        } else {
            let angle = Math.acos(dot);
            let vec_a = vec2.create();
            let vec_b = vec2.create();
            vec2.scale(vec_a, normal_a, Math.sin((1.0 - lerp) * angle));
            vec2.scale(vec_b, normal_b, Math.sin(lerp * angle));
            vec2.add(result, vec_a, vec_b);
            vec2.scale(result, result, 1.0 / Math.sin(angle));
        }
        return result;
    }
    
    MakeIndexBufferData() {
        let index_list = [];
        for(let i = 0; i < this.triangle_list.length; i++) {
            for(let j = 0; j < 3; j++) {
                index_list.push(this.triangle_list[i][j]);
            }
        }
        return new Uint16Array(index_list);
    }
    
    MakeVertexBufferData() {
        let vertex_list = [];
        for(let i = 0; i < this.vertex_list.length; i++) {
            let vertex = this.vertex_list[i];
            vertex_list.push(vertex['x']);
            vertex_list.push(vertex['y']);
        }
        return new Float32Array(vertex_list);
    }
    
    MakeLineVertexBufferData(outline) {
        this.line_count = 0;
        let vertex_list = [];
        for(let i = 0; i < outline.sub_region_list.length; i++) {
            let sub_region = outline.sub_region_list[i];
            let polygon_list = [sub_region.border_polygon];
            polygon_list = polygon_list.concat(sub_region.hole_list);
            for(let j = 0; j < polygon_list.length; j++) {
                let polygon = polygon_list[j];
                for(let k = 0; k < polygon.vertex_list.length; k++) {
                    let vertex = polygon.vertex_list[k];
                    vertex_list.push(vertex['x']);
                    vertex_list.push(vertex['y']);
                    vertex = polygon.vertex_list[(k + 1) % polygon.vertex_list.length];
                    vertex_list.push(vertex['x']);
                    vertex_list.push(vertex['y']);
                    this.line_count++;
                }
            }
        }
        return new Float32Array(vertex_list);
    }
    
    CapturesMesh(mesh) {
        if(this.type === 'capture_mesh' && mesh.type == 'picture_mesh') {
            // The puzzle is built such that no picture mesh straddles the boundary of a capture mesh.
            // It follows that to conclude a given mesh is completely covered by the capture mesh,
            // we need only check that any arbitrarily chosen _interior_ point of the given mesh is
            // inside any triangle of this, the capture mesh.
            let triangle = mesh.triangle_list[0];
            let point_a = mesh.GetVertex(triangle[0]);
            let point_b = mesh.GetVertex(triangle[1]);
            let point_c = mesh.GetVertex(triangle[2]);
            let interior_point = vec2.create();
            vec2.add(interior_point, point_a, point_b);
            vec2.add(interior_point, interior_point, point_c);
            vec2.scale(interior_point, interior_point, 1.0 / 3.0);
            vec2.transformMat3(interior_point, interior_point, mesh.local_to_world);
            if(this.ContainsPoint(interior_point))
                return true;
        }
        return false;
    }
    
    ContainsPoint(point) {
        let eps = 0.001;
        for(let i = 0; i < this.triangle_list.length; i++) {
            let triangle = this.triangle_list[i];
            let j = 0;
            for(j = 0; j < 3; j++) {
                let k = (j + 1) % 3;
                let edge_vector = vec2.create();
                vec2.sub(edge_vector, this.GetVertex(triangle[k]), this.GetVertex(triangle[j]));
                let vector = vec2.create();
                vec2.sub(vector, point, this.GetVertex(triangle[j]));
                let result = vec3.create();
                vec2.cross(result, edge_vector, vector);
                if(result[2] < -eps)
                    break;
            }
            if(j === 3)
                return true;
        }
        return false;
    }
    
    CalcArea() {
        let total_area = 0.0;
        for(let i = 0; i < this.triangle_list.length; i++) {
            let triangle = this.triangle_list[i];
            let edge_vector_a = vec2.create();
            let edge_vector_b = vec2.create();
            vec2.sub(edge_vector_a, this.GetVertex(triangle[1]), this.GetVertex(triangle[0]));
            vec2.sub(edge_vector_b, this.GetVertex(triangle[2]), this.GetVertex(triangle[0]));
            let result = vec3.create();
            vec2.cross(result, edge_vector_a, edge_vector_b);
            let area = Math.abs(result[2]);
            total_area += area;
        }
        return total_area;
    }
    
    GetVertex(i) {
        let vertex_data = this.vertex_list[i];
        let vertex = vec2.create();
        vec2.set(vertex, vertex_data['x'], vertex_data['y']);
        return vertex;
    }
}

var OnPuzzleMenuItemClicked = (i) => {
    puzzle_number = i;
    let puzzle_file = 'Puzzles/Puzzle' + puzzle_number.toString() + '.json';
    Promise.all([
        puzzle.Promise(puzzle_file),
        puzzle.PromiseComputerCanSolve(puzzle_number)
    ]).then(() => {
        puzzle.Render();
        $('#puzzle_name').text('Puzzle ' + puzzle_number.toString());
    });
}

var BuildPuzzleMenu = () => {
    $.ajax({
        url: 'puzzle_count',
        dataType: 'json',
        success: json_data => {
            let count = json_data['puzzle_count'];
            let puzzle_menu_div = document.getElementById('puzzle_menu');
            for(let i = 1; i <= count; i++) {
                let img = document.createElement('IMG')
                img.src = 'Puzzles/Puzzle' + i.toString() + '_Icon.png';
                img.addEventListener('click', (e) => {OnPuzzleMenuItemClicked(i)});
                puzzle_menu_div.appendChild(img);
            }
        },
        failure: error => {
            alert(error);
        }
    });
}

var gl = null;
var puzzle = new Puzzle();
var puzzle_number = 1;
var mesh_shader_program = {
    'vert_shader_source': 'Shaders/MeshVertShader.txt',
    'frag_shader_source': 'Shaders/MeshFragShader.txt',
};
var picture_mesh_count = 0;
var picture_mesh_texture = {
    'number': 0,
    'source': 'Images/image0.png',
};

var OnDocumentReady = () => {
	try {
	    BuildPuzzleMenu();
	    
	    let canvas = $('#canvas')[0];
	    canvas.style.width = '800px';
	    canvas.style.height = '800px';
	    canvas.width = 800;
	    canvas.height = 800;
	    
	    gl = canvas.getContext('webgl2');
	    if(!gl) {
	        throw 'WebGL is not available.';
	    }

	    gl.clearColor(0.0, 0.0, 0.0, 1.0);
	    gl.enable(gl.BLEND);
	    gl.disable(gl.DEPTH_TEST);
	    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

	    $('#canvas').click(OnCanvasClicked);
	    $('#canvas').mousemove(OnCanvasMouseMove);

        setInterval(OnIntervalHit, 10);

        Promise.all([
            puzzle.Promise('Puzzles/Puzzle' + puzzle_number.toString() + '.json'),
            puzzle.PromiseComputerCanSolve(puzzle_number),
            PromiseShaderProgram(mesh_shader_program),
            PromiseTexture(picture_mesh_texture)
        ]).then(() => {
            puzzle.Render();
            $('#puzzle_name').text('Puzzle ' + puzzle_number.toString());
        });
        
        $.ajax({
            url: 'image_count',
            dataType: 'json',
            success: json_data => {
                picture_mesh_count = json_data['image_count'];
            },
            failure: error => {
                alert(error);
            }
        });

	} catch(error) {
	    alert('Error: ' + error.toString());
	}
}

var OnCanvasClicked = event => {
    let location = puzzle.CalcMouseLocation(event);
    let i = puzzle.FindCaptureMeshContainingPoint(location);
    if(i >= 0) {
        let mesh = puzzle.mesh_list[i];
        let smallest_distance = 99999.0;
        let j = -1;
        // We skip the first 2, because they're rotations.  We only care about the reflections here.
        // But if there is only 1 symmetry, it is a reflection.
        let start = mesh.symmetry_list.length > 1 ? 2 : 0;
        for(let k = start; k < mesh.symmetry_list.length; k++) {
            let reflection = mesh.symmetry_list[k];
            let location_reflected = vec2.create();
            vec2.transformMat3(location_reflected, location, reflection);
            let distance = vec2.distance(location_reflected, location);
            if(distance < smallest_distance) {
                smallest_distance = distance;
                j = k;
            }
        }
        if(j >= 0) {
            puzzle.move_queue.push([i, j]);
        }
    }
}

var OnCanvasMouseWheel = event => {
    let location = puzzle.CalcMouseLocation(event);
    let i = puzzle.FindCaptureMeshContainingPoint(location);
    if(i >= 0) {
        let mesh = puzzle.mesh_list[i];
        if(mesh.symmetry_list.length > 1) {
            // The first two symmetries are always CCW/CW rotations, respectively,
            // if the shape has rotational symmetry.
            let j = event.deltaY > 0 ? 1 : 0;
            puzzle.move_queue.push([i, j]);
            event.preventDefault();
        }
    }
}

var OnCanvasMouseMove = event => {
    let location = puzzle.CalcMouseLocation(event);
    let i = puzzle.FindCaptureMeshContainingPoint(location);
    if(i != puzzle.highlight_mesh) {
        if(!$('#hover_highlights_check').is(':checked'))
            i = -1;
        puzzle.highlight_mesh = i;
        puzzle.Render();
    }
}

var ChangeImage = (delta) => {
    if(picture_mesh_count > 0) {
        picture_mesh_texture.number = picture_mesh_texture.number + delta;
        if(picture_mesh_texture.number >= picture_mesh_count)
            picture_mesh_texture.number = 0;
        else if(picture_mesh_texture.number < 0)
            picture_mesh_texture.number = picture_mesh_count - 1;
        picture_mesh_texture.source = 'Images/image' + picture_mesh_texture.number.toString() + '.png';
        PromiseTexture(picture_mesh_texture).then(() => {
            puzzle.Render();
        });
    }
}

var OnNextImageButtonClicked = () => {
    ChangeImage(1);
}

var OnPrevImageButtonClicked = () => {
    ChangeImage(-1);
}

var OnScrambleButtonClicked = () => {
    puzzle.QueueScrambleMoves(30);
}

var OnSolveButtonClicked = () => {
    puzzle.QueueSolutionMoves(puzzle_number);
}

var OnAnimationToggleClicked = () => {
    puzzle.AdvanceAnimation(true);
}

var OnAnimationSliderMoved = (slider_value) => {
    let slow_lerp = 0.05;
    let fast_lerp = 0.5;
    puzzle.animation_lerp = slow_lerp + (slider_value / 100.0) * (fast_lerp - slow_lerp);
}

var settle_render = false;
var OnIntervalHit = () => {
    if(puzzle.AnimationSettled()) {
        if(settle_render) {
            settle_render = false;
            puzzle.Render();
        }
        if(puzzle.move_queue.length > 0) {
            puzzle.ProcessNextMove();
            puzzle.Render();
            if(puzzle.IsSolved()) {
                $('#puzzle_name').text('Puzzle ' + puzzle_number.toString() + ' solved!');
            } else {
                $('#puzzle_name').text('Puzzle ' + puzzle_number.toString());
            }
        }
    } else {
        puzzle.AdvanceAnimation();
        puzzle.Render();
        settle_render = true;
    }
}

$(document).ready(OnDocumentReady);