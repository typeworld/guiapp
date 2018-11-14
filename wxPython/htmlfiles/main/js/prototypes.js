String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

/*
String.prototype.startsWith = function(prefix) {
    return this.indexOf(prefix, prefix.length) !== -1;
};
*/

if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

String.prototype.removeFromStart = function(string) {
	if (this.startsWith(string)) {
		return this.substr(string.length);
	}
	else {
		return this;
	}
};

String.prototype.removeFromEnd = function(string) {
	if (this.endsWith(string)) {
		return this.substr(0, this.length - string.length);
	}
	else {
		return this;
	}
};

String.prototype.URLfolder = function() {
	string = this;
	
	if (string.startsWith('http://') || string.startsWith('https://')) {
		string = string.removeFromStart('http://');
		string = string.removeFromStart('https://');
		parts = string.split('/');
		parts.shift();
		string = parts.join('/');
	}

	if (! string.startsWith('/')) {
		string = '/' + string;
	}
	return string;
};


String.prototype.has = function(obj) {
  return this.indexOf(obj) >= 0;
}

String.prototype.parameter = function(parameter) {
    
	if (this.has('?')) {
		return this + '&' + parameter;
	}
	else {
		return this + '?' + parameter;
	}
};



// Extend Array Object
if (Array.prototype.index==null)  Array.prototype.index = function(value)
{
  for(var i=0;i<this.length;i++){ 
   if(this[i]==value)
  return i;
  }
}

Array.prototype.has = function(obj) {
  return this.indexOf(obj) >= 0;
}


jQuery.fn.center = function () {
    this.css("position","absolute");
    this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) + 
                                                $(window).scrollTop()) + "px");
    this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) + 
                                                $(window).scrollLeft()) + "px");
    return this;
}

jQuery.fn.centerInViewPort = function () {

	viewPort = mainViewPortDimensions();
	offset = this.offset();

	$('html, body').animate({scrollTop: offset.top - $('#head').height() - (viewPort.height - this.outerHeight()) / 2.0});


	return true;
}


jQuery.fn.topInViewPort = function () {




	viewPort = mainViewPortDimensions();
	var offset = this.offset();

	while (Math.abs($(window).scrollTop() - (offset.top - $('#head').outerHeight())) > 1.0) {
		$(window).scrollTop(offset.top - $('#head').outerHeight());
		offset = this.offset();
	}

//	$('html, body').animate({scrollTop: offset.top - $('#head').outerHeight()}, 200);


	return true;
}