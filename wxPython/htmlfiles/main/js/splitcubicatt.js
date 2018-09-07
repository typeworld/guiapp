
function calcCubicParameters(pt1, pt2, pt3, pt4) {


	x2 = pt2[0];
	y2 = pt2[1];
	x3 = pt3[0];
	y3 = pt3[1];
	x4 = pt4[0];
	y4 = pt4[1];
	dx = pt1[0];
	dy = pt1[1];
	cx = (x2 -dx) * 3.0;
	cy = (y2 -dy) * 3.0;
	bx = (x3 - x2) * 3.0 - cx;
	by = (y3 - y2) * 3.0 - cy;
	ax = x4 - dx - cx - bx;
	ay = y4 - dy - cy - by;
	return Array(Array(ax, ay), Array(bx, by), Array(cx, cy), Array(dx, dy));
}

function calcCubicPoints(a, b, c, d) {

	ax = a[0];
	ay = a[1]
	bx = b[0];
	by = b[1]
	cx = c[0];
	cy = c[1]
	dx = d[0];
	dy = d[1]

	x1 = dx;
	y1 = dy;
	x2 = (cx / 3.0) + dx;
	y2 = (cy / 3.0) + dy;
	x3 = (bx + cx) / 3.0 + x2;
	y3 = (by + cy) / 3.0 + y2;
	x4 = ax + dx + cx + bx;
	y4 = ay + dy + cy + by;
	return Array(Array(x1, y1), Array(x2, y2), Array(x3, y3), Array(x4, y4));
}


function _splitCubicAtT(a, b, c, d, t) {
	ts = Array();
	ts.push(t);

	ts.unshift(0.0);
	ts.push(1.0);
	segments = Array();

	var ax, bx, cx, dx, ay, by, cy, dy;

	ax = a[0];
	ay = a[1]
	bx = b[0];
	by = b[1]
	cx = c[0];
	cy = c[1]
	dx = d[0];
	dy = d[1]

	for (i = 0; i < ts.length; i++) {

		var t1, t2, delta, delta_2, delta_3, t1_2, t1_3;

		t1 = ts[i];
		t2 = ts[i+1];
		delta = (t2 - t1);

		delta_2 = delta*delta;
		delta_3 = delta*delta_2;
		t1_2 = t1*t1;
		t1_3 = t1*t1_2;

		//; calc new a, b, c and d

		var a1x, a1y, b1x, b1y, c1x, c1y, d1x, d1y, pt1, pt2, pt3, pt4;

		a1x = ax * delta_3;
		a1y = ay * delta_3;
		b1x = (3*ax*t1 + bx) * delta_2;
		b1y = (3*ay*t1 + by) * delta_2;
		c1x = (2*bx*t1 + cx + 3*ax*t1_2) * delta;
		c1y = (2*by*t1 + cy + 3*ay*t1_2) * delta;
		d1x = ax*t1_3 + bx*t1_2 + cx*t1 + dx;
		d1y = ay*t1_3 + by*t1_2 + cy*t1 + dy;
		cubicPoints = calcCubicPoints(Array(a1x, a1y), Array(b1x, b1y), Array(c1x, c1y), Array(d1x, d1y));
		pt1 = cubicPoints[0];
		pt2 = cubicPoints[1];
		pt3 = cubicPoints[2];
		pt4 = cubicPoints[3];
		segments.push((pt1, pt2, pt3, pt4));
	}
	return segments;
}


function splitCubicAtT(pt1, pt2, pt3, pt4, t) {
	var a, b, c, d;
	cubicParameters = calcCubicParameters(pt1, pt2, pt3, pt4);
	a = cubicParameters[0];
	b = cubicParameters[1];
	c = cubicParameters[2];
	d = cubicParameters[3];
	return _splitCubicAtT(a, b, c, d, t);
}




