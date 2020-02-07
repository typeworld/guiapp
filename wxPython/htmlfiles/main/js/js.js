
function startLoadingAnimation() {
	startAnimation();
}

function stopLoadingAnimation() {
	stopAnimation();
}


window.onerror = function (msg, url, lineNo, columnNo, error) {
 
 	debug('JavaScript error:');
 	debug('JavaScript error, Msg: ' + msg.replace("''", "\""));
 	debug('JavaScript error, url: ' + url);
 	debug('JavaScript error, lineNo: ' + lineNo);
 	debug('JavaScript error, columnNo: ' + columnNo);
 	debug('JavaScript error, error: ' + error.replace("''", "\""));

  return false;
}

function python(code) {
	// debug(code);
    window.location.href = "x-python://" + code;
}

function debug(string) {
    window.location.href = "x-python://self.debug(\'" + string + "\')";
}

function linkout(url) {
    window.location.href = url;
}

function setPreference(key, value) {
    python('client.preferences.set(____' + key + '____, ____' + value + '____)');
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
	python('self.onContextMenu(____' + evt.pageX + '____, ____' + evt.pageY + '____, ____' + $(evt.target).closest('.contextmenu').attr('class') + '____, ____' + $(evt.target).closest('.contextmenu').attr('id') + '____)')
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

	$(".countdownMinutes").each(function() {

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

  	python('self.checkFontExpirations()');

	setTimeout(function () { recalcMinutesCountdown(); }, 10000);
}

$( document ).ready(function() {

	// Automatically reload subscriptions
	autoReloadSubscriptions = function(immediately) {
		if (immediately) {
			python('self.autoReloadSubscriptions()');
			autoReloadSubscriptions();
		}
		else {
			setTimeout(function () {
				python('self.autoReloadSubscriptions()');
				autoReloadSubscriptions();
			}, 1000 * 60); // every minute
		}
	};

	setTimeout(function () { autoReloadSubscriptions(true); }, 2000); // First load after 2 seconds


	setTimeout(function () { recalcMinutesCountdown(); }, 3000); // First load after 3 seconds	



	$(document).bind("contextmenu",function(evt){
		contextmenu(evt);
		evt.preventDefault();
    	return false;
	});

	$("#main #publisher .removePublisherButton").click(function() {
		$( this ).addClass( "hover" );
		id = $(this).closest('.publisher').attr('id');
		python('self.removePublisher(\'' + id + '\')'); 
	});


	$(".font").on("click", function() {
		debug('font clicked');
		showMetadata();
	});


	$("#url").on('keyup', function() {
		addUrl = $(this).val();
	});


	$(document).on("keyup", function( event ) {
		for(var key in keypressFunctions) {
		    if(keypressFunctions.hasOwnProperty(key)) {
		        if (event.which == key) {
			        keypressFunctions[key]();
		        }
		    }
		}
	});

});

function showAddSubscription() {
	$('#addSubscription #url').val(null);
	$('#addSubscription #authenticationCheckBox').hide();

    // Reset Form
    $("#addSubscriptionFormSubmitButton").show();
    $("#addSubscriptionFormCancelButton").show();
    $("#addSubscriptionFormSubmitAnimation").hide();


	$('#addSubscription').slideDown();
	registerKeypress(27, function(){ hidePanel(); });
	$('#addSubscription #url').focus();
	python('self.panelVisible = True')
}

function showMain() {
	$('#welcome').slideUp();
	$('#main').slideDown();
}

function hideMain() {
	$('#welcome').slideDown();
	$('#main').slideUp();
}

function showAbout() {
	$('#about').slideDown();
	registerKeypress(27, function(){ hidePanel(); });
	python('self.panelVisible = True')
}

function showPreferences() {
	$('#preferences').slideDown();
	registerKeypress(27, function(){ hidePanel(); });
	python('self.panelVisible = True')
}

function showPublisherPreferences() {
	$('#publisherPreferences').slideDown();
	registerKeypress(27, function(){ hidePanel(); });
	python('self.panelVisible = True')
}

function setPublisherHTML(b64ID) {
	python('self.setPublisherHTML(____' + b64ID + '____)');
}

function hidePanel() {
	$('#addSubscription').slideUp();
	$('#preferences').slideUp();
	$('#publisherPreferences').slideUp();
	$('#subscriptionPreferences').slideUp();
	$('#about').slideUp();
	python('self.panelVisible = False');
	unregisterKeypress(27);
	python('self.setSideBarHTML()');

}

function showMetadata() {

	$("#metadataWrapper").animate({width: 300}, 300);
	$("#main").animate({right: 300}, 300);
}

function hideMetadata() {
	$("#metadataWrapper").animate({width: 0}, 300);
	$("#main").animate({right: 0}, 300);
}

function showCenterMessage(html, completeFunction) {
	$('#centerMessage').html(html);
	$('#centerMessageWrapper').show();
	if (completeFunction) {
		setTimeout(function () { 
			completeFunction;
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



