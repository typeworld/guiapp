
function python(code) {
    window.location.href = "x-python://" + code;
}

function debug(string) {
    window.location.href = "x-python://self.debug(\'" + string + "\')";
}

function linkout(url) {
    window.location.href = url;
}


keypressFunctions = [];

function registerKeypress(key, method) {
	keypressFunctions[key] = method;
}

function unregisterKeypress(key) {
	keypressFunctions[key] = null;
}


$( document ).ready(function() {


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
//	$('#addPublisher #url').val(null);
	$('#addPublisher').slideDown();
	registerKeypress(27, function(){ hideAddPublisher(); });
	$('#addPublisher #url').focus();
}

function hideAddPublisher() {
	unregisterKeypress(27);
	$('#addPublisher').slideUp();
}