
function Interpolate(a, b, p) {
	return a + (b - a) * p;
}

function NormalizeMinMax(source_floor, source_ceiling, target_floor, target_ceiling, value) {
	if (target_floor == 0) {
		return (value - source_floor) / parseFloat(source_ceiling - source_floor) * target_ceiling;
	}
	else {
		return (value - source_floor) / parseFloat(source_ceiling - source_floor) * (target_ceiling - target_floor) + target_floor;
	}
}

function InterpolateMany(valuelist, p) {
	p = parseFloat(p);
	if (valuelist.length == 1) {
		return Array(valuelist[0], valuelist[0], valuelist[0]);
	}
	// Return first item
	else if (p == 0.0) {
		return Array(valuelist[0], valuelist[0], valuelist[0]);
	}
	// Return last item
	else if (p == 1.0) {
		return Array(valuelist[valuelist.length - 1], valuelist[valuelist.length - 1], valuelist[valuelist.length - 1]);
	}
	// Interpolate
	else {
		for (var i = 0; i < valuelist.length; i++) {
			// p is exactly on one of the values
			if (p == i / parseFloat(valuelist.length - 1)) {
				return Array(valuelist[i], valuelist[i], valuelist[i]);
			}
			// Interpolate
			else if (i * 1.0 / parseFloat(valuelist.length - 1) < p && p < (i + 1) * 1.0 / parseFloat(valuelist.length - 1)) {
				v1 = valuelist[i];
				v2 = valuelist[i + 1];
				// Hier liegt der Hase begraben
				_p_floor = i * 1.0 / parseFloat(valuelist.length - 1);
				_p_ceil = _p_floor + 1.0 / parseFloat(valuelist.length - 1);
				_p = NormalizeMinMax(_p_floor, _p_ceil, 0, 1, p);
				return Array(Interpolate(v1, v2, _p), v1, v2);
			}
		}
	}
}



function Ellipse(ctx, tAdjust, speed, trailColor, pointColor, direction, canvasSize) {
	this.ctx = ctx;
	this.speed = speed;
	this.trailColor = trailColor;
	this.pointColor = pointColor;
	this.tAdjust = tAdjust;
	this.direction = direction;
	this.canvasSize = canvasSize;

	this.p1 = Array(150, 0);
	this.p2 = Array(150, 60);
	this.p3 = Array(90, 100);
	this.p4 = Array(0, 100);
}

Ellipse.prototype.drawQuadrant = function (q) {
	if (q == 1) {
		var px = 1;
		var py = 1;
		this.ctx.moveTo(this.p1[0] * px, this.p1[1] * py);
		this.ctx.bezierCurveTo(this.p2[0] * px, this.p2[1] * py, this.p3[0] * px, this.p3[1] * py, this.p4[0] * px, this.p4[1] * py);
	}
	else if (q == 2) {
		var px = -1;
		var py = 1;
		this.ctx.bezierCurveTo(this.p3[0] * px, this.p3[1] * py, this.p2[0] * px, this.p2[1] * py, this.p1[0] * px, this.p1[1] * py);
	}
	else if (q == 3) {
		var px = -1;
		var py = -1;
		this.ctx.bezierCurveTo(this.p2[0] * px, this.p2[1] * py, this.p3[0] * px, this.p3[1] * py, this.p4[0] * px, this.p4[1] * py);
	}
	else if (q == 4) {
		var px = 1;
		var py = -1;
		this.ctx.bezierCurveTo(this.p3[0] * px, this.p3[1] * py, this.p2[0] * px, this.p2[1] * py, this.p1[0] * px, this.p1[1] * py);
	}
}


Ellipse.prototype.draw = function () {
	this.ctx.fillStyle = this.color;
	this.ctx.beginPath();
	this.drawQuadrant(1);
	this.drawQuadrant(2);
	this.drawQuadrant(3);
	this.drawQuadrant(4);
	this.ctx.fill();
}

Ellipse.prototype.drawTrail = function (keyFrame, opticalSize) {

	this.ctx.save();
	this.ctx.scale(.96, .96);

	var trailSize = 150;
	for (var i = trailSize; i >= 0; i--) {
		var k = i * 0.004 * parseFloat(fps);
		var t = i / parseFloat(trailSize);
		r = parseInt(InterpolateMany(Array(this.trailColor[0][0], this.trailColor[1][0], 0), t)[0]);
		g = parseInt(InterpolateMany(Array(this.trailColor[0][1], this.trailColor[1][1], 0), t)[0]);
		b = parseInt(InterpolateMany(Array(this.trailColor[0][2], this.trailColor[1][2], 0), t)[0]);
		a = InterpolateMany(Array(.4, .2, 0), t)[0];
		rgbaColor = 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
		this.drawPoint(((keyFrame - k) * this.speed / fps) % 4.0, rgbaColor, Interpolate(20 / opticalSize, 5, t));
	}

	this.ctx.shadowColor = "#000";
	this.ctx.shadowBlur = 20 / opticalSize;
	this.ctx.shadowOffsetX = 0;
	this.ctx.shadowOffsetY = 0;
	this.drawPoint((keyFrame * this.speed / fps) % 4.0, this.pointColor, 30 / opticalSize);
	this.ctx.shadowColor = 0;

	this.ctx.restore();
}

Ellipse.prototype.drawPoint = function (t, color, size) {

	// t += this.direction;

	var localT = (t + this.tAdjust) % 1;
	// localT = localT * this.direction;

	if (t < 1) {
		var px = 1;
		var py = 1;
	}
	else if (t < 2) {
		var px = -1;
		var py = 1;
		localT = (1 - localT);
	}
	else if (t < 3) {
		var px = -1;
		var py = -1;
	}
	else {
		var px = 1;
		var py = -1;
		localT = (1 - localT);
	}


	var p = splitCubicAtT(Array(this.p1[0] * px, this.p1[1] * py), Array(this.p2[0] * px, this.p2[1] * py), Array(this.p3[0] * px, this.p3[1] * py), Array(this.p4[0] * px, this.p4[1] * py), localT)[0]
	this.ctx.lineWidth = 0;
	this.ctx.strokeStyle = 0;
	this.ctx.fillStyle = color;
	this.ctx.beginPath();
	this.ctx.arc(p[0], p[1], size / 2.0, 0, 2 * Math.PI);
	this.ctx.fill();


}

var fps = 25.0;
var rampDuration = parseInt(.6 * fps);
var rampDurationStop = parseInt(1.3 * fps);


var timeout;
var keyFrame, fps, factor, c, ctx, e, f, g;
var animation = false;
var rampStart, rampStop;
rampStop = 0;
keyFrame = 60;
var lastKeyFrame;

function startAnimation() {
	if (animation == false || rampStop > 0) {
		rampStart = 0;
		rampStop = 0;
		animation = true;
		timeout(lastKeyFrame || keyFrame, false);
	}
}

function stopAnimation() {
	rampStop = rampDurationStop;
	rampStart = rampDuration;
}

function animationHasStopped() {

}




function setupCanvas(canvas) {
	// Get the device pixel ratio, falling back to 1.
	var dpr = window.devicePixelRatio || 1;
	// Get the size of the canvas in CSS pixels.
	var rect = canvas.getBoundingClientRect();
	// Give the canvas pixel dimensions of their CSS
	// size * the device pixel ratio.
	canvas.width = rect.width * dpr;
	canvas.height = rect.height * dpr;
	canvas.style.width = rect.width + 'px';
	canvas.style.height = rect.height + 'px';
	var ctx = canvas.getContext('2d');
	// Scale all drawing operations by the dpr, so you
	// don't have to worry about the difference.
	ctx.scale(dpr, dpr);
	return ctx;
}


$(document).ready(function () {

	$('#atom').hover(function () {
		startAnimation();
	}, function () {
		stopAnimation();
	}
	);

	var canvas = document.getElementById("atom");
	var ctx = setupCanvas(canvas);
	var rect = canvas.getBoundingClientRect();

	var factor = rect.width / 400.0;

	var e = new Ellipse(ctx, 1, 2.5, Array(Array(0, 255, 168), Array(41, 35, 92)), '#FFC500', 1, canvas.width); // yellow
	var f = new Ellipse(ctx, 2, 3, Array(Array(0, 175, 255), Array(102, 36, 130)), '#52E952', 1, canvas.width); // green
	var g = new Ellipse(ctx, 3, 4, Array(Array(82, 233, 82), Array(106, 71, 0)), '#FF9AFF', 1, canvas.width); // pink


	timeout = function timeout(keyFrame, once) {
		if (animation || once || rampStop > 0) {
			setTimeout(function () {

				speedAdjust = .5;
				startSpeedAdjust = 1.0;
				stopSpeedAdjust = 1.0;

				if (rampStart < rampDuration + 1) {
					startSpeedAdjust = rampStart / rampDuration;
				}
				if (rampStop > 0) {
					stopSpeedAdjust *= rampStop / rampDurationStop;
				}

				speedAdjust = speedAdjust * startSpeedAdjust * stopSpeedAdjust;

				opticalSize = rect.width / 200.0;
				opticalSize = Math.min(.9, opticalSize);
				opticalSize = Math.max(.8, opticalSize);


				// Initial save
				ctx.save();
				ctx.clearRect(0, 0, canvas.width, canvas.height);
				ctx.translate(rect.width / 2.0, rect.height / 2.0);
				ctx.scale(-1 * factor, factor);

				// draw ellipses first
				ctx.save();
				ctx.rotate((90) * Math.PI / 180.0);
				e.draw();
				ctx.restore();
				ctx.save();
				ctx.rotate((90 + 60) * Math.PI / 180.0);
				f.draw();
				ctx.restore();
				ctx.save();
				ctx.rotate((90 - 60) * Math.PI / 180.0);
				g.draw();
				ctx.restore();

				// draw points second
				ctx.save();
				ctx.rotate((90) * Math.PI / 180.0);
				e.drawTrail(keyFrame, opticalSize);
				ctx.restore();

				ctx.save();
				ctx.rotate((90 + 60) * Math.PI / 180.0);
				f.drawTrail(keyFrame, opticalSize);
				ctx.restore();

				ctx.save();
				ctx.rotate((90 - 60) * Math.PI / 180.0);
				g.drawTrail(keyFrame, opticalSize);
				ctx.restore();

				// Restore
				ctx.restore();


				ctx.save();

				ctx.scale(opticalSize, opticalSize);
				ctx.translate((rect.width / opticalSize - rect.width) / 2.0, (rect.height / opticalSize - rect.height) / 2.0);

				// Draw Plus
				ctx.lineWidth = 20 * factor / opticalSize;


				// white horizontal
				ctx.beginPath();
				ctx.strokeStyle = '#fff';
				ctx.moveTo(145 * factor, 200 * factor);
				ctx.lineTo(255 * factor, 200 * factor);
				ctx.stroke();

				if (rect.width > 100) {
					// blue horizontal
					ctx.beginPath();
					ctx.strokeStyle = '#00AFFF';
					ctx.moveTo(140 * factor, 200 * factor);
					ctx.lineTo(155 * factor, 200 * factor);
					ctx.stroke();

					// pink horizontal
					ctx.beginPath();
					ctx.strokeStyle = '#FF9AFF';
					ctx.moveTo(245 * factor, 200 * factor);
					ctx.lineTo(260 * factor, 200 * factor);
					ctx.stroke();
				}

				// white vertical
				ctx.beginPath();
				ctx.strokeStyle = '#fff';
				ctx.moveTo(200 * factor, 145 * factor);
				ctx.lineTo(200 * factor, 255 * factor);
				ctx.stroke();

				if (rect.width > 100) {
					// green vertical
					ctx.beginPath();
					ctx.strokeStyle = '#52E952';
					ctx.moveTo(200 * factor, 140 * factor);
					ctx.lineTo(200 * factor, 155 * factor);
					ctx.stroke();

					// orange vertical
					ctx.beginPath();
					ctx.strokeStyle = '#FFBD00';
					ctx.moveTo(200 * factor, 245 * factor);
					ctx.lineTo(200 * factor, 260 * factor);
					ctx.stroke();
				}

				ctx.restore();



				if (!once) {
					keyFrame += speedAdjust;
				}


				rampStart++;
				rampStop--;

				lastKeyFrame = keyFrame;
				if (rampStop == 0) {
					animation = false;
					lastKeyFrame = keyFrame;
					animationHasStopped();
				}

				if (animation) {
					timeout(keyFrame, false);
				}
			}, 1000 / fps);
		}
	}

	timeout(keyFrame, true);

});