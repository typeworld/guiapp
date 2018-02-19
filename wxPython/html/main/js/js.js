
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

function installFont(publisherID, subscriptionID, fontID, version) {

	debug('Calling JS installFont()');

	installButton = $("#" + fontID + ".font").find('a.install').closest('.installButton');
	statusButton = $("#" + fontID + ".font").find('a.status').closest('.statusButton');
	removeButton = $("#" + fontID + ".font").find('a.remove').closest('.removeButton');

	installButton.hide();
	removeButton.hide();
	statusButton.show();

//	setTimeout(function() { 
		python('self.installFont(____' + publisherID + '____, ____' + subscriptionID + '____, ____' + fontID + '____, ____' + version + '____)'); 
//	}, 100);
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

function installAllFonts(publisherID, subscriptionID, familyID) {

	family = $("#" + familyID + ".family");

	i = 0;
	family.children('.font').each(function(index, el) {
		i++;
		
		div = $(el).find('a.install').closest('div.installButton');
		if (div.is(':visible')) {
			div.siblings('.statusButton').show();
			div.hide();
		}
	});

//	setTimeout(function() { 
		python('self.installAllFonts(____' + publisherID + '____, ____' + subscriptionID + '____, ____' + familyID + '____)'); 
//	}, 100);

}

function removeAllFonts(publisherID, subscriptionID, familyID) {

	family = $("#" + familyID + ".family");

	i = 0;
	family.children('.font').each(function(index, el) {
		i++;
		
		div = $(el).find('a.remove').closest('div.removeButton');
		if (div.is(':visible')) {
			div.siblings('.statusButton').show();
			div.hide();
		}
	});

//	setTimeout(function() { 
		python('self.removeAllFonts(____' + publisherID + '____, ____' + subscriptionID + '____, ____' + familyID + '____)'); 
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

function hidePanel() {
	$('#addPublisher').slideUp();
	$('#preferences').slideUp();
	$('#about').slideUp();
	python('self.panelVisible = False');
	unregisterKeypress(27);
	
}

/* ///////////////////////////////////////////////////////////////////////////////////////////////////// */


// JQUERY

	$( function() {
	    $( document ).tooltip();
	  } );

