WIN = false;
MAC = false;
LINUX = false;


loadCSS = function (href) {

	var cssLink = $("<link>");
	$("head").append(cssLink); //IE hack: append before setting href

	cssLink.attr({
		rel: "stylesheet",
		type: "text/css",
		href: href
	});

};



function startLoadingAnimation() {
	startAnimation();
}

function stopLoadingAnimation() {
	stopAnimation();
}

function replace(incoming) {
	// return incoming;
	return incoming.replace("'", "____");
}

window.onerror = function (msg, url, lineNo, columnNo, error) {

	// msg = msg.replace("''", "\"");
	// error = error.replace("''", "\"");

	debug('JavaScript error: msg: ' + replace(msg) + ', url: ' + replace(url) + ', lineNo: ' + replace(lineNo) + ', columnNo: ' + replace(columnNo) + ', error: ' + replace(error));
	// debug('JavaScript error, Msg: ' + msg.replace("''", "\""));
	// debug('JavaScript error, url: ' + url);
	// debug('JavaScript error, lineNo: ' + lineNo);
	// debug('JavaScript error, columnNo: ' + columnNo);
	// debug('JavaScript error, error: ' + error.replace("''", "\""));

	return false;
};

function python(code) {
	// debug(code);
	window.location.href = "https://type.world/x-python/" + code;
}

function debug(string) {
	// window.location.href = "x-python://self.debug(____" + string + "____)";
	python("self.debug(____" + string + "____)");
}

function linkout(url) {
	window.location.href = url;
}

function setPreference(key, value) {
	debug(key + ' - ' + value);
	python('client.set(____' + key + '____, ____' + value + '____)');
}

function setCustomLanguage(language) {
	debug(language);
	setPreference("customLocaleChoice", language);
	// setPreference("localizationType", "customLocale");
}

function setPublisherPreference(b64ID, key, value) {
	python('client.publisher(self.b64decode(____' + b64ID + '____)).set(____' + key + '____, ____' + value + '____)');
}

function setSubscriptionPreference(b64ID, key, value) {
	python('self.setSubscriptionPreference(self.b64decode(____' + b64ID + '____), ____' + key + '____, ____' + value + '____)');
}

function setPublisherPassword(b64ID, username, password) {
	python('client.publisher(self.b64decode(____' + b64ID + '____)).setPassword(____' + username + '____, ____' + password + '____)');
}

function contextmenu(evt) {
	if (WIN) {
		x = evt.pageX * window.devicePixelRatio;
		y = evt.pageY * window.devicePixelRatio;
	}
	else {
		x = evt.pageX;
		y = evt.pageY;
	}
	python('self.onContextMenu(____' + x + '____, ____' + y + '____, ____' + $(evt.target).closest('.contextmenu').attr('class') + '____, ____' + $(evt.target).closest('.contextmenu').attr('id') + '____)');
}

function resetFontAppearance(fontID) {
	$("#" + fontID + ".font").find('a.status').hide();
}

function setCursor(name, timeout) {
	$('html').css('cursor', 'wait !important');
	$('*').css('cursor', 'wait !important');
	$('body').css('cursor', 'wait !important');

	setTimeout(function () {
		$('html').css('cursor', 'inherit');
		$('*').css('cursor', 'inherit');
		$('body').css('cursor', 'inherit');
	}, timeout);
}

keypressFunctions = [];

function registerKeypress(key, method) {
	keypressFunctions[key] = method;
}

function unregisterKeypress(key) {
	keypressFunctions[key] = null;
}


function recalcMinutesCountdown() {

	$(".countdownMinutes").each(function () {

		timestamp = parseFloat($(this).attr('timestamp'));
		if (timestamp) {
			min = parseInt(parseFloat((timestamp - parseFloat(Date.now() / 1000))) / 60);
			if (min <= 0) {
				min = '0';
			}
			else if (min < 1) {
				min = '<1';
			}

			$(this).html(min + "'");
			$(this).addClass('countdown');
		}
		else {
			$(this).removeClass('countdown');

		}

	});

	// python('self.checkFontExpirations()');

	// setTimeout(function () { recalcMinutesCountdown(); }, 10000);
}

function documentReady() {

	// $.get("https://polyfill.io/v3/polyfill.min.js?features=Array.prototype.find,Promise,Object.assign", function (data) {
	// 	$("#download").html(data);
	// 	python("self.data(____" + data + "____)");
	// });


	// load("https://polyfill.io/v3/polyfill.min.js?features=Array.prototype.find,Promise,Object.assign", function (contents) {
	// 	// contents is now set to the contents of "site.com/t.txt"
	// 	$("#download").html(contents);
	// });
	// // Automatically reload subscriptions
	// minutely = function () {
	// 	python('self.minutely()');
	// 	setTimeout(function () {
	// 		minutely();
	// 	}, 1000 * 60); // every minute

	// };


	$(".pullServerUpdates").click(function () {
		python('self.pullServerUpdates(force = True)');
	});


	$(document).bind("contextmenu", function (evt) {
		contextmenu(evt);
		// evt.preventDefault();
		return false;
	});

	$("#main #publisher .removePublisherButton").click(function () {
		$(this).addClass("hover");
		id = $(this).closest('.publisher').attr('id');
		python('self.removePublisher(\'' + id + '\')');
	});

	$(".visitUserAccount").click(function () {
		python("self.visitUserAccount()");
	});


	$(".font").on("click", function () {
		showMetadata();
	});


	$("#url").on('keyup', function () {
		addUrl = $(this).val();
	});


	$(document).on("keyup", function (event) {
		for (var key in keypressFunctions) {
			if (keypressFunctions.hasOwnProperty(key)) {
				if (event.which == key) {
					keypressFunctions[key]();
				}
			}
		}
	});

	tippy.setDefaultProps({
		delay: 1000,
		theme: "black",
	});
	$('[alt]').each(function () {
		tippy(this, {
			content: $(this).attr('alt'),
			allowHTML: true,
			maxWidth: 350 * zoomFactor,
		});
	});

	// resize();

	$(window).resize(function () {
		// resize();
	});

}

var zoomFactor = 1.0;
var sideBarSize = 300;

function zoom() {

	$('.zoom').css('zoom', zoomFactor);
	$('.tippy-popper, .tippy-tooltip, .tippy-content').css('zoom', zoomFactor);
	$('.nozoom').css('zoom', 1.0);
	$('.sidebar').css('width', (sideBarSize * zoomFactor) + 'px');
	$('#sidebar').css('width', (sideBarSize) + 'px');
	// $('#sidebarBottom').css('width', (sideBarSize) + 'px');
	$('.main').css('left', (sideBarSize * zoomFactor) + 'px');
	$('#atom').css('width', (120 / zoomFactor) + 'px');
	$('#atom').css('height', (120 / zoomFactor) + 'px');

	// $('.main').css('width', ($(window).width() / zoomFactor) + 'px');
	// resize();
}

function resize() {

}

function showMetadata() {
	$("#metadataWrapper").animate({ width: sideBarSize }, 300, function () { resize(); });
	$(".main").animate({ right: sideBarSize }, 300);
}

function hideMetadata() {
	$("#metadataWrapper").animate({ width: 0 }, 300, function () { resize(); });
	$(".main").animate({ right: 0 }, 300);
}


function startMinutely() {
	setTimeout(function () { python('self.minutely()'); setInterval(function () { python('self.minutely()'); }, 1000 * 30); }, 0); // First load after 2 seconds
}



$(document).ready(function () {

	// if (WIN) {
	python("self.onLoad(None)");
	// }

	documentReady();

	// setTimeout(function () { recalcMinutesCountdown(); }, 3000); // First load after 3 seconds	

	$('#addSubscription #url').keyup(function () { if ($('#addSubscription #url').val().startsWith("typeworldgithub://")) { $('#addSubscription #authenticationCheckBox').slideDown(); } else { $('#addSubscription #authenticationCheckBox').slideUp(); } });
	$('#addSubscription #usePassword').click(function () { debug($('#addSubscription #usePassword').val()); if ($('#addSubscription #usePassword').is(":checked")) { } else { } });

	$("#addSubscriptionForm").submit(function (event) {

		event.preventDefault();
		$("#addSubscriptionFormSubmitButton").click();


	});

	$("#addSubscriptionFormSubmitButton").click(function () {

		$("#addSubscriptionFormSubmitButton").hide();
		$("#addSubscriptionFormCancelButton").hide();
		$("#addSubscriptionFormSubmitAnimation").show();

		python('self.addSubscriptionViaDialog(____' + $('#addSubscriptionForm #url').val() + '____, ____' + $('#addSubscriptionForm #username').val() + '____, ____' + $('#addSubscriptionForm #password').val() + '____)');

	});

	// loadCSS("file://##htmlroot##/main/css/tippy.css");


	// debug($("#dpiMeasurementInPt").width() / parseFloat($("#dpiMeasurementInPx").width()));

});


function ReloadCSS() {
	for (var i = 0; i < document.querySelectorAll("link[rel=stylesheet]").length; i++) {
		link = document.querySelectorAll("link[rel=stylesheet]")[i];
		link.href = link.href.replace(/\?.*|$/, "?" + Date.now());
	}
}


function showAddSubscription() {
	$('#addSubscription #url').val(null);
	$('#addSubscription #authenticationCheckBox').hide();

	// Reset Form
	$("#addSubscriptionFormSubmitButton").show();
	$("#addSubscriptionFormCancelButton").show();
	$("#addSubscriptionFormSubmitAnimation").hide();


	$('#addSubscription').slideDown();
	registerKeypress(27, function () { hidePanel(); });
	$('#addSubscription #url').focus();
	python('self.panelVisible = ____addSubscription____');
}

function showMain() {
	$('#welcome').slideUp();
	$('#main').slideDown();
}

function hideMain() {
	$('#welcome').slideDown();
	$('#main').slideUp();
	hideMetadata();
}

function showAbout() {
	$('#about').slideDown();
	registerKeypress(27, function () { hidePanel(); });
	python('self.panelVisible = ____about____');
}

function showPreferences() {
	$('#preferences').slideDown();
	registerKeypress(27, function () { hidePanel(); });
	// python('self.panelVisible = ____preferences____'); (Happens in Pythhon Code)
}

function showPublisherPreferences() {
	$('#publisherPreferences').slideDown();
	registerKeypress(27, function () { hidePanel(); });
	python('self.panelVisible = ____publisherPreferences____');

	function setPublisherHTML(b64ID) {
		python('self.setPublisherHTML(____' + b64ID + '____)');
	}
}

function hidePanel() {
	$('#addSubscription').slideUp();
	$('#preferences').slideUp();
	$('#publisherPreferences').slideUp();
	$('#subscriptionPreferences').slideUp();
	$('#about').slideUp();
	python('self.hidePanel(); self.setSideBarHTML();');
	unregisterKeypress(27);

}


function showCenterMessage(html, completeFunction) {
	$('#centerMessage').html(html);
	$('#centerMessageWrapper').show();
	if (completeFunction) {
		setTimeout(function () {
			completeFunction();
		}, 100);
	}
}

function hideCenterMessage() {
	$('#centerMessageWrapper').fadeOut();
}

function addSubscription(url, username, password, caption) {

	showCenterMessage(caption);
	setTimeout(function () {
		python('self.addSubscription(____' + url + '____, ____' + username + '____, ____' + password + '____)');
	}, 1100);


}

/* ///////////////////////////////////////////////////////////////////////////////////////////////////// */


// JQUERY

	// $( function() {
	//     $( document ).tooltip();
	//   } );



