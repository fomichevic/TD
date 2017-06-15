var canvas, gl, program, colorUniform, width, height, time, u;

function getShader(id) {
	var element = document.getElementById(id);
	var getType = {
		'x-shader/x-vertex' : gl.VERTEX_SHADER,
		'x-shader/x-fragment' : gl.FRAGMENT_SHADER,
	};
	var type, source, shader;
	if (!element) {
		console.log('Shader ' + id + ' not found.');
		return null;
	}
	source = element.text;
	type = getType[element.type];
	if (!type) {
		console.log('Unknown shader type ' + element.type);
		return null;
	}
	shader = gl.createShader(type);
	gl.shaderSource(shader, source);
	gl.compileShader(shader);
	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		console.log('Failed to compile the shader: ' + gl.getShaderInfoLog(shader));
		gl.deleteShader(shader);
		return null;
		}
	return shader;
}

function createProgram(vertex, fragment) {
	var program = gl.createProgram();
	gl.attachShader(program, vertex);
	gl.attachShader(program, fragment);
	gl.linkProgram(program);
	if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
		console.log('Failed to link the program: ' + gl.getProgramInfoLog(program));
		gl.deleteProgram(program);
		return null;
	}
	return program;
}

function resize(width, height) {
	if (gl.canvas.width == width && gl.canvas.height == height)
		return;
	gl.canvas.width = width;
	gl.canvas.height = height;
	gl.viewport(0, 0, width, height);
}

function rgb(red, green, blue, alpha){
	return {
		r: red,
		g: green,
		b: blue,
		a: alpha
	};
}

function draw(points, color, count){
	gl.bufferData(gl.ARRAY_BUFFER, toScreen(points), gl.DYNAMIC_DRAW);
    gl.uniform4f(colorUniform, color.r, color.g, color.b, color.a);
    gl.drawArrays(gl.TRIANGLES, 0, count);
}

function drawLine(p1, p2, color){
	gl.bufferData(gl.ARRAY_BUFFER, toScreen([p1.x, p1.y, p2.x, p2.y]), gl.DYNAMIC_DRAW);
	gl.uniform4f(colorUniform, color.r, color.g, color.b, color.a);
	gl.drawArrays(gl.LINES, 0, 2);
}

function drawGrid(){
	for (var i = 0; i <= 200; i += 20)
		drawLine(new vec2(0, i), new vec2(200, i), rgb(1, 1, 1, 1));
	for (var i = 0; i <= 200; i += 20)
		drawLine(new vec2(i, 0), new vec2(i, 200), rgb(1, 1, 1, 1));
}

function drawRegularPolygon(points, color){
	draw(points, color, points.length / 2);
}

function unit(pos){
	this.pos = pos;
	this.stopAt = pos;
	this.chooseTarget = function t(){
		var r = Math.floor(Math.random() * 4);
		switch(r){
			case 0:
				if (this.pos.x <= 8)
					return new vec2(1, 0);
				else
					return t();
			case 1:
				if (this.pos.y <= 8)
					return new vec2(0, 1);
				else
					return t();
			case 2:
				if (this.pos.x >= 1)
					return new vec2(-1, 0);
				else
					return t();
			default:
				if (this.pos.y >= 1)
					return new vec2(0, -1);
				else
					return t();
		}
	};
	this.target = new vec2(0, 0);
	this.update = ()=>{
		if (len(substract(this.pos, this.stopAt)) < 0.01){
			this.target = this.chooseTarget();
			this.stopAt = add(this.pos, this.target);
		}
		this.pos = add(this.pos, multiply(this.target, 0.05));
	};
	this.draw = ()=>{
		drawRegularPolygon(regularPolygon(add(multiply(this.pos, 20), new vec2(10, 10)), 5, 10, Math.sin(time)), rgb(Math.abs(Math.sin(time / 2)), Math.abs(Math.sin(time / 2 + 1)), Math.abs(Math.sin(time / 2 + 2)), 1));
	};
}

function toScreen(points){
	var scrPoints = new Float32Array(points);
	for (var i = 0; i < points.length; i++)
		scrPoints[i] = ((i % 2 == 0) ? xToScreen(scrPoints[i]) : yToScreen(scrPoints[i]));
	return scrPoints;
}

function regularPolygon(center, n, rad, alpha){
	var data = new Float32Array(n * 6);
	var temp = rotate(new vec2(rad, 0), alpha);
	var psi = 2 * Math.PI / n;
	for (var i = 0; i < n; i++){
		data[i * 6] = center.x;
		data[i * 6 + 1] = center.y;
		data[i * 6 + 2] = add(center, temp).x;
		data[i * 6 + 3] = add(center, temp).y;
		temp = rotate(temp, psi);
		data[i * 6 + 4] = add(center, temp).x;
		data[i * 6 + 5] = add(center, temp).y;
	}
	return data;
}

function rectangle(pos, size){
	var x = pos.x, y = pos.y, w = size.x, h = size.y;
	return new Float32Array([
			x,     y,
			x + w, y,
			x + w, y + h,
			
			x + w, y + h,
			x,     y + h,
			x,     y,
		]);
}

function genRectangle(){
	var pos = new vec2(Math.floor(Math.random() * width), Math.floor(Math.random() * height));
	var size = new vec2(Math.floor(Math.random() * (width - pos.x)), Math.floor(Math.random() * (height - pos.y)));
	return rectangle(pos, size);
}

function add(v1, v2){
	return new vec2(v1.x + v2.x, v1.y + v2.y);
}

function substract(v1, v2){
	return new vec2(v1.x - v2.x, v1.y - v2.y);
}

function multiply(v, scalar){
	return new vec2(v.x * scalar, v.y * scalar);
}

function rotate(vec, alpha){
	return new vec2(vec.x * Math.cos(alpha) - vec.y * Math.sin(alpha), vec.x * Math.sin(alpha) + vec.y * Math.cos(alpha));
}

function vec2(x, y){
	this.x = x;
	this.y = y;
}

function len(v){
	return Math.sqrt(v.x * v.x + v.y * v.y);
}

function xToScreen(x){
	return (x / width) * canvas.clientWidth;
}

function yToScreen(y){
	return (1 - y / height) * canvas.clientHeight;
}

function clear(){
	gl.clearColor(0.0, 0.0, 0.0, 1.0)
	gl.clear(gl.COLOR_BUFFER_BIT);
}

function init(){
	canvas = document.getElementById('glCanvas');
	gl = canvas.getContext('webgl');
	if (!gl) {
		console.log('Unable to initialize WebGL. Your browser may not support it.');
		return;
	}
	program = createProgram(getShader('vertex'), getShader('fragment'));
	colorUniform = gl.getUniformLocation(program, 'uColor');
	resize(canvas.clientWidth, canvas.clientHeight);
	gl.clearColor(0.0, 0.0, 0.0, 0.0)
	gl.clear(gl.COLOR_BUFFER_BIT);
	gl.useProgram(program);
	gl.enableVertexAttribArray(gl.getAttribLocation(program, 'aPosition'));
	gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
	gl.vertexAttribPointer(gl.getAttribLocation(program, 'aPosition'), 2, gl.FLOAT, false, 0, 0);
	gl.uniform2f(gl.getUniformLocation(program, 'uResolution'), gl.canvas.width, gl.canvas.height);
	width = 200;
	height = 200;
	time = 0;
	requestAnimationFrame(function upd(){
		requestAnimationFrame(upd);
		time = (time + 3 * Math.PI / 180) % (2 * Math.PI);
	});
}

function main(){
	init();
	u = new unit(new vec2(5, 5));
	requestAnimationFrame(function drawFrame(){
		requestAnimationFrame(drawFrame);
		clear();
		drawGrid();
		u.update();
		u.draw();
	});
}