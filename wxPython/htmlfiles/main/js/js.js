
window.onerror = function (msg, url, lineNo, columnNo, error) {
 
 	debug('JavaScript error:');
 	debug('Msg: ' + msg);
 	debug('url: ' + url);
 	debug('lineNo: ' + lineNo);
 	debug('columnNo: ' + columnNo);
 	debug('error: ' + error);

  return false;
}

function python(code) {
    window.location.href = "x-python://" + code;
}

function debug(string) {
    window.location.href = "x-python://self.debug(\'" + string + "\')";
}

function linkout(url) {
    window.location.href = url;
}

function setPreference(key, value) {
    python('self.client.preferences.set(____' + key + '____, ____' + value + '____)');
}

function setPublisherPreference(b64ID, key, value) {
    python('self.client.publisher(self.b64decode(____' + b64ID + '____)).set(____' + key + '____, ____' + value + '____)');
}

function setPublisherPassword(b64ID, username, password) {
    python('self.client.publisher(self.b64decode(____' + b64ID + '____)).setPassword(____' + username + '____, ____' + password + '____)');
}

function contextmenu(evt) {
	python('self.onContextMenu(____' + evt.pageX + '____, ____' + evt.pageY + '____, ____' + $(evt.target).closest('.contextmenu').attr('class') + '____, ____' + $(evt.target).closest('.contextmenu').attr('id') + '____)')
}

function reloadPublisher(b64ID) {
	// $("#sidebar #" + b64ID + " .badges").hide();
	// $("#sidebar #" + b64ID + " .reloadAnimation").show();
	setTimeout(function () { 
		python('self.reloadPublisher(None, ____' + b64ID + '____)');
	}, 100);
}

function reloadSubscription(b64ID) {
	// $("#subscriptions #" + b64ID + " .badges").hide();
	// $("#subscriptions #" + b64ID + " .reloadAnimation").show();
	setTimeout(function () { 
		python('self.reloadSubscription(None, ____' + b64ID + '____)');
	}, 100);

	
}

function finishReloadPublisher(b64ID) {
	$("#sidebar #" + b64ID + " .badges").show();
	$("#sidebar #" + b64ID + " .reloadAnimation").hide();
}

function finishReloadSubscription(b64ID) {
	// $("#subscriptions #" + b64ID + " .badges").show();
	// $("#subscriptions #" + b64ID + " .reloadAnimation").hide();
}

function resetFontAppearance(fontID) {
	$("#" + fontID + ".font").find('a.status').hide();
}



keypressFunctions = [];

function registerKeypress(key, method) {
	keypressFunctions[key] = method;
}

function unregisterKeypress(key) {
	keypressFunctions[key] = null;
}

$( document ).ready(function() {

	// Automatically reload subscriptions
	reloadSubscriptions = function(immediately) {
		if (immediately) {
			python('self.reloadSubscriptions()');
			reloadSubscriptions();
		}
		else {
			setTimeout(function () {
				python('self.reloadSubscriptions()');
				reloadSubscriptions();
			}, 1000 * 60); // every minute
		}
	};
	setTimeout(function () { reloadSubscriptions(true); }, 2000); // First load after 2 seconds

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

function hidePanel() {
	$('#addSubscription').slideUp();
	$('#preferences').slideUp();
	$('#publisherPreferences').slideUp();
	$('#subscriptionPreferences').slideUp();
	$('#about').slideUp();
	python('self.panelVisible = False');
	unregisterKeypress(27);
	
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



