/* Wheels section
 * getCookie, document.ready and window.ready
 */

//Get cookie by name
//Used in POST queries to send csrftoken value.
function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
};

/*
 *Data load section
 */

function LoadClients() {
	//Clear existing data
	$('#existing_clients tbody').html("");
	//Get data from server in json
	$.getJSON( "/rnr/clients_all", function(data) {
		//for all clients in data
		 
		$.each( data, function( index, element ) {
			var items = [];
			var row = ""
			row =row.concat("<tr>");
			row =row.concat("<td id=" +  element.client_slug + ">");
			row =row.concat(element.attribs.client_name);
			row =row.concat("</td>");
			row =row.concat("<td id=" +  element.attribs.client_language__slug + ">");
			row =row.concat(element.attribs.client_language__language_name);
			row =row.concat("</td>");
			row =row.concat("<td>");
			//for all contacts in client
			$.each(element.contacts, function(index, element) {
			var	btn = '<button ' + 'id="' + element.slug +'" class="btn_del_contact" type="button"></button>'
				row =row.concat("<div class=contact_email id='"+element.slug + "'>" + element.contact_email + btn + "</div>");
			});
			row =row.concat("</tr>");
			$('#existing_clients tbody').append(row);
		});
		Load_btn_del_contact();
		
	})
	.done(Load_btn_del_contact());
};

function blah(){
	var d = $(this).attr("id");
	alert(d);
};

var LoadWorkTypes = function() {
	$('#existing_work_types').html("");
	$.getJSON( "/rnr/get_work_types_json", function(data){
		$.each( data, function( index, element ){
			$('#existing_work_types').append('<p id=' + element.slug + ' class="ui-widget work_type">'+ element.worktype_name +'</p>')
		});
	});
};

//On document ready - load data, apply styling
//Load data, add jQuery UI to dialog elements
$(document).ready(function(){
	LoadClients();
	LoadWorkTypes();
	Load_ui_elements();
	//Load_btn_del_contact();
	
});

//$(window).ready(Load_btn_del_contact());

function Load_btn_del_contact(){
	//$( ".selector" ).button;
	$( ".btn_del_contact" ).button({ icons: { primary: "ui-icon-trash" } });
	$( ".btn_del_contact" ).click(function() {
       var cid = $(this).attr("id");
       
       var cont = $(this).parent().text();
       $("#del_contact").text(cont);
      ans = $( "#dlg_confirm_del_contact" ).dialog( "open" );
      alert(ans);
       if (ans===true){
       	$("div #"+cid).remove();
       };
    });
	
}


//Add new client dialog
function Load_dlg_add_client(){
	$( "#dlg_add_client" ).dialog({
        autoOpen: false,
        height: 400,
        width: 450,
        modal: true,
        buttons: {
        			"Create User": function(){CreateClient();},
        			Cancel: function() {
        				$(this).dialog("close");
        				$('#frm_add_client').trigger("reset");
        				$("#dlg_add_client_errors").html("");
        				}
         		},
         title: "Add new Client",        
        });
};


function Load_dlg_add_work(){
	$( "#dlg_add_work" ).dialog({
        autoOpen: false,
        height: 450,
        width: 450,
        modal: true,
        buttons: {
        			"Create Work": function(){CreateClient();},
        			Cancel: function() {
        				$(this).dialog("close");
        				$('#frm_add_work').trigger("reset");
        				$("#dlg_add_work_errors").html("");
        				}
         		},
         title: "Add new Work",        
        });
};

//Delete contact confirm dialog
function Load_dlg_del_contact(){
	$( "#dlg_confirm_del_contact" ).dialog({
		autoOpen: false,
		resizable: false,
		height:180,
		modal: true,
		buttons: {
			"Delete Contact": function() {
				$( this ).dialog( "close" );
				return true;
			},
			Cancel: function() {
				$( this ).dialog( "close" );
				return false;
			}
		}
	});
};


//Load UI elements with jQuery styling.
//Loads after data and dialogs are loaded - on window ready
function Load_ui_elements(){
	
	Load_dlg_add_client();
	Load_dlg_del_contact();
	Load_dlg_add_work();

	
	//Add Create client button
	$( "#btn_create_client" ).button();
	$( "#btn_add_work" ).button();
	//bind Create client dialog on click
	$( "#btn_create_client" ).click(function() {
	$( "#dlg_add_client" ).dialog( "open" );});
	//btn_add_work
	$( "#btn_add_work" ).click(function() {
		$( "#dlg_add_work" ).dialog( "open" );})
		
		
	$( "#client_language" ).selectmenu();
	
	
	 $( "#start_date_datepicker" ).datepicker({
		 showButtonPanel: true
		 });
	 $( "#end_date_datepicker" ).datepicker({
		 showButtonPanel: true
		 });
	 $('#work_start_time').timepicker({ 'timeFormat': 'H:i' });
	 $('#work_end_time').timepicker({ 'timeFormat': 'H:i' });
	//Add button styling to delete contact button
//	$( ".btn_del_contact" ).button();
	//bind click on btn_del_contact to open delete contact dialog
//	$( ".btn_del_contact" ).click(function() {
//	$( "#dlg_confirm_del_contact" ).dialog( "open" );});

};


function DelContact(contact_slug){
	alert(contact_slug);
};


/* Content management functions
 * for clients:
 * - Get all clients via ajax and json
 * - Load data in #existing_clients table tbody
 */

function CreateClient(){
	//send form data as ajax
	//alert("sended");
	var client_name = $( "#client_name" ).val();
	var client_language = $( "#client_language" ).val();
	var client_emails = $( "#client_emails" ).val();
	var posting = $.post( "/rnr/add_new_client", {
		ajax: "true",
		"client_name": client_name,
		"client_language" : client_language,
		"client_emails":client_emails,
		'csrfmiddlewaretoken':getCookie('csrftoken'),
	});
	// Put the results in a div
	posting.done(function( data ) {
		//alert(data);
		if (data === "OK"){
			$("#dlg_add_client_errors").html("");
			$('#frm_add_client').trigger("reset");
			$('#dlg_add_client').dialog("close");
			LoadClients();
			return true;
		}
		else{
			$("#dlg_add_client_errors").html(data);
			return false;
		};	
	});
};



function CreateWork(){
	//send form data as ajax
	//alert("sended");
	var client_name = $( "#client_name" ).val();
	var client_language = $( "#client_language" ).val();
	var client_emails = $( "#client_emails" ).val();
	var posting = $.post( "/rnr/add_new_work", {
		ajax: "true",
		"client_name": client_name,
		"client_language" : client_language,
		"client_emails":client_emails,
		'csrfmiddlewaretoken':getCookie('csrftoken'),
	});
	// Put the results in a div
	posting.done(function( data ) {
		//alert(data);
		if (data === "OK"){
			$("#dlg_add_client_errors").html("");
			$('#frm_add_client').trigger("reset");
			$('#dlg_add_client').dialog("close");
			LoadClients();
			return true;
		}
		else{
			$("#dlg_add_client_errors").html(data);
			return false;
		};	
	});
};


