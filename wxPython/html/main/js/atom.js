



var Ellipse = class {
	constructor(ctx, tAdjust, speed, color, pointColor) {
		this.ctx = ctx;
		this.speed = speed;
		this.color = color;
		this.pointColor = pointColor;
		this.tAdjust = tAdjust;

		this.p1 = Array(150, 0);
		this.p2 = Array(150, 60);
		this.p3 = Array(90, 100);
		this.p4 = Array(0, 100);
	}

	drawQuadrant(q) {

		if (q == 1) {
			var px = 1;
			var py = 1;
		}
		else if (q == 2) {
			var px = -1;
			var py = 1;
		}
		else if (q == 3) {
			var px = -1;
			var py = -1;
		}
		else if (q == 4) {
			var px = 1;
			var py = -1;
		}

		this.ctx.lineCap = 'round';
		this.ctx.lineWidth = 5;
		this.ctx.strokeStyle=this.color;
//		newPath()
		this.ctx.beginPath();
		this.ctx.moveTo(this.p1[0] * px, this.p1[1] * py);
		this.ctx.bezierCurveTo(this.p2[0] * px, this.p2[1] * py, this.p3[0] * px, this.p3[1] * py, this.p4[0] * px, this.p4[1] * py);
		// closePath()
//		drawPath()
		this.ctx.stroke();

	}


	draw() {


		this.drawQuadrant(1);
		this.drawQuadrant(2);
		this.drawQuadrant(3);
		this.drawQuadrant(4);


	}


	drawPoint(t) {



		var localT = (t + this.tAdjust) % 1;

		if (t < 1) {
			var px = 1;
			var py = 1;
		}
		else if (t < 2) {
			var px = -1;
			var py = 1;
			localT = 1 - localT;
		}
		else if (t < 3) {
			var px = -1;
			var py = -1;
		}
		else {
			var px = 1;
			var py = -1;
			localT = 1 - localT;
		}

		
		var p = splitCubicAtT(Array(this.p1[0] * px, this.p1[1] * py), Array(this.p2[0] * px, this.p2[1] * py), Array(this.p3[0] * px, this.p3[1] * py), Array(this.p4[0] * px, this.p4[1] * py), localT)[0]
//		console.log(p);

		
//		fill(*[x / 255.0 for x in this.pointColor])
//		stroke(None)
		var _size = 35
//		oval(p[0] - _size / 2.0, p[1] - _size / 2.0, _size, _size)

		this.ctx.lineWidth = 0;
		this.ctx.strokeStyle = 0;
		this.ctx.fillStyle=this.pointColor;
		this.ctx.beginPath();
		this.ctx.arc(p[0], p[1], _size / 2.0, 0, 2*Math.PI);
		this.ctx.fill();
//		console.log('fill', this);

//		console.log(p[0] - _size / 2.0, p[1] - _size / 2.0);


	}
}
	
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



var rampDuration = 20.0;
var rampDurationStop = 50.0;


$(document).ready(function() {

	$('#atom')

	$('#atomButton').hover(function() {
	    startAnimation();
	  }, function() {
	    stopAnimation();
	  }
	);

	fps = 30.0;

	var c=document.getElementById("atom");
	var ctx=c.getContext("2d");

	factor = 1.0;

	e = new Ellipse(ctx, 1, 2.5 / factor, '#555', '#F8B334'); // yellow
	f = new Ellipse(ctx, 2, 3 / factor, '#555', '#97BF0D'); // green
	g = new Ellipse(ctx, 3, 4 / factor, '#555', '#009EE0'); // blue


	ctx.scale(150.0 / 500.0, 150.0 / 500.0);
	ctx.translate(250, 250);

	timeout = function timeout(keyFrame, once) {
		if (animation || once || rampStop > 0) {
			setTimeout(function () {

				speedAdjust = 1.0;
				startSpeedAdjust = 1.0;
				stopSpeedAdjust = 1.0;

				if (rampStart < rampDuration + 1) {
					startSpeedAdjust = rampStart / rampDuration;
				}
				if (rampStop > 0) {
					stopSpeedAdjust *= rampStop / rampDurationStop;
				}

				speedAdjust = speedAdjust * startSpeedAdjust * stopSpeedAdjust;


				ctx.save();
				ctx.setTransform(1, 0, 0, 1, 0, 0);
				ctx.clearRect(0, 0, c.width, c.height);
				ctx.restore();

				ctx.save();

				ctx.rotate((90) * Math.PI / 180.0);
				e.draw();
				e.drawPoint((keyFrame * e.speed / fps) % 4.0);

				ctx.restore();
				ctx.save();

				ctx.rotate((90 + 60) * Math.PI / 180.0);
				f.draw();
				f.drawPoint((keyFrame * f.speed / fps) % 4.0);

				ctx.restore();
				ctx.save();

				ctx.rotate((90 - 60) * Math.PI / 180.0);
				g.draw();
				g.drawPoint((keyFrame * g.speed / fps) % 4.0);
				
				ctx.restore();

				if (! once) {
					keyFrame += speedAdjust;
				}


				rampStart++;
				rampStop--;

				lastKeyFrame = keyFrame;
				if (rampStop == 0) {
					animation = false;
					console.log(keyFrame);		
					lastKeyFrame = keyFrame;
				}

				if (animation) {
					timeout(keyFrame, false);
				}
			}, 1000 / fps);
		}
	}

timeout(keyFrame, true);

//console.log(keyFrame);

// ctx.fillStyle='#abcdef';
// ctx.beginPath();
// ctx.arc(100, 100, 50, 0, 2*Math.PI);
// ctx.fill();


});