var canvas, gl, program, textureProgram, colorUniform, width, height, time, time_rad, u, pBuffer, tpBuffer, emptyBuffer;
const square = new Float32Array([0,0,  1,0,  1,1,  
								 1,1,  0,1,  0,0]);
var image = loadImage('atlas.png');
var RegionsData;
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

function rgba(red, green, blue, alpha){
	this.r = red;
	this.g = green;
	this.b = blue;
	this.a = alpha;
}

function draw(points, color){
	gl.useProgram(program);
	gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, toScreen(points), gl.DYNAMIC_DRAW);
	gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
    gl.uniform4f(colorUniform, color.r, color.g, color.b, color.a);
    gl.drawArrays(gl.TRIANGLES, 0, points.length / 2);
}

function drawLine(p1, p2, color){
	gl.useProgram(program);
	gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, toScreen([p1.x, p1.y, p2.x, p2.y]), gl.DYNAMIC_DRAW);
	gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
	gl.uniform4f(colorUniform, color.r, color.g, color.b, color.a);
	gl.drawArrays(gl.LINES, 0, 2);
}

function drawGrid(){
	for (var i = 0; i <= 200; i += 20)
		drawLine(new vec2(0, i), new vec2(200, i), new rgba(1, 1, 1, 1));
	for (var i = 0; i <= 200; i += 20)
		drawLine(new vec2(i, 0), new vec2(i, 200), new rgba(1, 1, 1, 1));
}

function drawImage(img, pos, size){
	if (!img.complete)
		return;
	console.log("Image is loaded");
	var points = toScreen(new Float32Array([pos.x,pos.y, pos.x+size.x,pos.y, pos.x+size.x,pos.y+size.y, 
											pos.x+size.x,pos.y+size.y, pos.x,pos.y+size.y, pos.x,pos.y]));
	gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, points, gl.DYNAMIC_DRAW);
	gl.bindBuffer(gl.ARRAY_BUFFER, tpBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, square, gl.DYNAMIC_DRAW);
	var texture = gl.createTexture();
	gl.bindTexture(gl.TEXTURE_2D, texture);
	gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
	gl.generateMipmap(gl.TEXTURE_2D);
	gl.useProgram(textureProgram);

	gl.enableVertexAttribArray(gl.getAttribLocation(program, 'aTexturePosition'));
	gl.bindBuffer(gl.ARRAY_BUFFER, tpBuffer);
	gl.vertexAttribPointer(gl.getAttribLocation(program, 'aTexturePosition'), 2, gl.FLOAT, false, 0, 0);

	gl.activeTexture(gl.TEXTURE0);
	gl.bindTexture(gl.TEXTURE_2D, texture);
	gl.uniform1i(gl.getUniformLocation(program, 'uTexture'), 0);

	gl.drawArrays(gl.TRIANGLES, 0, 6);
}

function loadImage(src){
	var img = new Image();
	img.crossOrigin = "";
	img.src = src;
	return img;
}

function toPerc(arr, width, height){
	var result = new Float32Array(arr);
	for (var i = 0; i < arr.length; i++)
		if (i % 2 == 0)
			result[i] /= width;
		else
			result[i] /= height;
	return result;
}

function getTextureRegionInfo(id){
	return RegionsData[id];
}

function TextureRegion(id){
	var data = getTextureRegionInfo(id);
	this.img = loadImage(data.src);
	this.pos = data.pos;
	this.size = data.size;
	this.draw = (pos, size)=>{
		if (!img.complete)
			return;
		console.log("TextureRegion is loaded");
		var points = toScreen(new Float32Array([pos.x,pos.y, pos.x+size.x,pos.y, pos.x+size.x,pos.y+size.y, 
												pos.x+size.x,pos.y+size.y, pos.x,pos.y+size.y, pos.x,pos.y]));
		gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
		gl.bufferData(gl.ARRAY_BUFFER, points, gl.DYNAMIC_DRAW);
		var reg = toPerc(new Float32Array([this.pos.x,this.pos.y, this.pos.x+this.size.x,this.pos.y, this.pos.x+this.size.x,this.pos.y+this.size.y, 
										   this.pos.x+this.size.x,this.pos.y+this.size.y, this.pos.x,this.pos.y+this.size.y, this.pos.x,this.pos.y]),
						img.width,
						img.height);
		gl.bindBuffer(gl.ARRAY_BUFFER, tpBuffer);
		gl.bufferData(gl.ARRAY_BUFFER, square, gl.DYNAMIC_DRAW);
		var texture = gl.createTexture();
		gl.bindTexture(gl.TEXTURE_2D, texture);
		gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
		gl.generateMipmap(gl.TEXTURE_2D);
		gl.useProgram(textureProgram);
	
		gl.enableVertexAttribArray(gl.getAttribLocation(program, 'aTexturePosition'));
		gl.bindBuffer(gl.ARRAY_BUFFER, tpBuffer);
		gl.vertexAttribPointer(gl.getAttribLocation(program, 'aTexturePosition'), 2, gl.FLOAT, false, 0, 0);
	
		gl.activeTexture(gl.TEXTURE0);
		gl.bindTexture(gl.TEXTURE_2D, texture);
		gl.uniform1i(gl.getUniformLocation(program, 'uTexture'), 0);
	
		gl.drawArrays(gl.TRIANGLES, 0, 6);
	}
}

function unit(pos){
	this.pos = pos;
	this.stopAt = pos;
	this.chooseTarget = function (){
		var r = Math.floor(Math.random() * 4);
		switch(r){
			case 0:
				if (this.pos.x <= 8)
					return new vec2(1, 0);
				else
					return this.chooseTarget();
			case 1:
				if (this.pos.y <= 8)
					return new vec2(0, 1);
				else
					return this.chooseTarget();
			case 2:
				if (this.pos.x >= 1)
					return new vec2(-1, 0);
				else
					return this.chooseTarget();
			default:
				if (this.pos.y >= 1)
					return new vec2(0, -1);
				else
					return this.chooseTarget();
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
		draw(regularPolygon(add(multiply(this.pos, 20), new vec2(10, 10)), 5, 10, Math.sin(time)), new rgba(Math.abs(Math.sin(time / 2)), Math.abs(Math.sin(time / 2 + 1)), Math.abs(Math.sin(time / 2 + 2)), 1));
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
	pBuffer = gl.createBuffer();
	tpBuffer = gl.createBuffer();
	program = createProgram(getShader('vertex'), getShader('fragment'));
	textureProgram = createProgram(getShader('vertex-texture'), getShader('fragment-texture'));
	colorUniform = gl.getUniformLocation(program, 'uColor');
	resize(canvas.clientWidth, canvas.clientHeight);
	gl.clearColor(0.0, 0.0, 0.0, 0.0)
	gl.clear(gl.COLOR_BUFFER_BIT);
	gl.useProgram(program);
	gl.bindBuffer(gl.ARRAY_BUFFER, pBuffer);
	gl.enableVertexAttribArray(gl.getAttribLocation(program, 'aPosition'));
	gl.vertexAttribPointer(gl.getAttribLocation(program, 'aPosition'), 2, gl.FLOAT, false, 0, 0);
	gl.uniform2f(gl.getUniformLocation(program, 'uResolution'), gl.canvas.width, gl.canvas.height);
	width = 200;
	height = 200;
	time = 0;
	var req = new XMLHttpRequest();
	req.open("GET", "http://127.0.0.1:5000/static/atlas.txt", false);
	req.onreadystatechange = ()=>{
		if (req.readyState == 4 && (req.status == 200 || req.status == 0))
			RegionsData = JSON.parse(req.responseText);
	}
	req.send(null);
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
		drawImage(image, new vec2(0, 0), new vec2(20, 20));
		u.update();
		u.draw();
	});
}