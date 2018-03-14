
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
	$("#sidebar #" + b64ID + " .badges").hide();
	$("#sidebar #" + b64ID + " .reloadAnimation").show();
	python('self.reloadPublisher(None, ____' + b64ID + '____)');
}

function reloadSubscription(b64ID) {
	// $("#sidebar #" + b64ID + " .badges").hide();
	// $("#sidebar #" + b64ID + " .reloadAnimation").show();
	python('self.reloadSubscription(None, ____' + b64ID + '____)');
}

function finishReloadPublisher(b64ID) {
	$("#sidebar #" + b64ID + " .badges").show();
	$("#sidebar #" + b64ID + " .reloadAnimation").hide();
}

function finishReloadSubscription(b64ID) {
	// $("#sidebar #" + b64ID + " .badges").show();
	// $("#sidebar #" + b64ID + " .reloadAnimation").hide();
}

function resetFontAppearance(fontID) {
	$("#" + fontID + ".font").find('a.status').hide();
}

function installAllFonts(publisherID, subscriptionID, familyID, setName, formatName) {
	python('self.installAllFonts(____' + publisherID + '____, ____' + subscriptionID + '____, ____' + familyID + '____, ____' + setName + '____, ____' + formatName + '____)');
}

function removeAllFonts(publisherID, subscriptionID, familyID, setName, formatName) {
	python('self.removeAllFonts(____' + publisherID + '____, ____' + subscriptionID + '____, ____' + familyID + '____, ____' + setName + '____, ____' + formatName + '____)');
}

function installFonts(fonts, fromMenu) {

	var pythonFontList = Array();

	fonts.forEach(function(font) {

		publisherID = font[0];
		subscriptionID = font[1];
		fontID = font[2];
		version = font[3];


		$("#" + fontID + ".font").find('a.installButton').hide();
		$("#" + fontID + ".font").find('a.removeButton').hide();
		$("#" + fontID + ".font").find('a.status').show();
		$("#" + fontID + ".font").find('a.more').hide();

		pythonFontList.push('[____' + publisherID + '____, ____' + subscriptionID + '____, ____' + fontID + '____, ____' + version + '____]');


	});

	call = '[' + pythonFontList.join(', ') + ']';

	if (fromMenu) {
		setTimeout(function() { 
			python('self.installFonts(' + call + ')');
		}, 100);
	}
	else {
		python('self.installFonts(' + call + ')');
	}
}

function removeFonts(fonts, fromMenu) {

	var pythonFontList = Array();

	fonts.forEach(function(font) {

		publisherID = font[0];
		subscriptionID = font[1];
		fontID = font[2];


		$("#" + fontID + ".font").find('a.removeButton').hide();
		$("#" + fontID + ".font").find('a.status').show();

		pythonFontList.push('[____' + publisherID + '____, ____' + subscriptionID + '____, ____' + fontID + '____]');


	});

	call = '[' + pythonFontList.join(', ') + ']';
	if (fromMenu) {
		setTimeout(function() { 
			python('self.removeFonts(' + call + ')');
		}, 100);
	}
	else {
		python('self.removeFonts(' + call + ')');
	}
}

function removeFont(publisherID, subscriptionID, fontID) {

	installButton = $("#" + fontID + ".font").find('a.install').closest('.installButton');
	statusButton = $("#" + fontID + ".font").find('a.status').closest('.statusButton');
	removeButton = $("#" + fontID + ".font").find('a.remove').closest('.removeButton');

	installButton.hide();
	removeButton.hide();
	statusButton.show();

//	setTimeout(function() { 
		python('self.removeFont(____' + publisherID + '____, ____' + subscriptionID + '____, ____' + fontID + '____)'); 
//	}, 100);
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

	$("#sidebar .publisher").click(function() {
		$("#sidebar .publisher").removeClass('selected');
		$(this).addClass('selected');
		python('self.setPublisherHTML(\'' + $(this).attr('id') + '\')'); 
	});


	$("#main #publisher .removePublisherButton").click(function() {
		$( this ).addClass( "hover" );
		id = $(this).closest('.publisher').attr('id');
		python('self.removePublisher(\'' + id + '\')'); 
	});


	$("#url").on('keyup', function() {
		addUrl = $(this).val();
	});



	// $("#sidebar .publisher").hover(function() {
	//     $( this ).addClass( "hover" );
	//   }, function() {
	//     $( this ).removeClass( "hover" );
	//   }
	// );

	// $("#main .font").hover(function() {
	//     $( this ).addClass( "hover" );
	//   }, function() {
	//     $( this ).removeClass( "hover" );
	//   }
	// );

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

function showAddPublisher() {
	$('#addPublisher #url').val(null);
	$('#addPublisher #authenticationCheckBox').hide();

	$('#addPublisher').slideDown();
	registerKeypress(27, function(){ hidePanel(); });
	$('#addPublisher #url').focus();
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
	$('#addPublisher').slideUp();
	$('#preferences').slideUp();
	$('#publisherPreferences').slideUp();
	$('#subscriptionPreferences').slideUp();
	$('#about').slideUp();
	python('self.panelVisible = False');
	unregisterKeypress(27);
	
}

function showCenterMessage(html) {
	$('#centerMessage').html(html);
	$('#centerMessageWrapper').fadeIn();
}

function hideCenterMessage() {
	$('#centerMessageWrapper').fadeOut();
}

/* ///////////////////////////////////////////////////////////////////////////////////////////////////// */


// JQUERY

	$( function() {
	    $( document ).tooltip();
	  } );

