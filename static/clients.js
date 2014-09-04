 var getCookie=function(name) {
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


var place_all_clients = function(json_clients)
{

};


/*var get_clients = function()
{
$.post( "/rnr/clients_all", {'csrfmiddlewaretoken':getCookie('csrftoken')},
	function( data ) {
	  alert( "Data Loaded: " + data );
	})
.done( function( data ) {alert( "Data Loaded: " + data );});
};
//;

var gg = function()
{
$.getJSON('/rnr/clients_all', { get_param: 'value' }, function(data) {
    $.each(data, function(index, element) {
        $('body').append($('<div>', {
            text: element.name
        }));
    });
});
};

var ggg = function()
{
 
  $.post("/rnr/clients_all", {
    ajax: "true",
    action: "",
    'csrfmiddlewaretoken':getCookie('csrftoken')
}).always(function(data){
      alert(data);
      var items = [];
      $.each( data, function( key, val ) {
      alert(key, val);
      items.push( "<li id='" + key + "'>" + val + "</li>" );
});
});
};


*/

var LoadWorkTypes = function() {
	$('#work_types').html("");
	
	$.getJSON( "/rnr/get_work_types_json", function(data){
	      $.each( data, function( index, element ){
	    	  
	    	  $('#work_types').append('<p id=' + element.slug + ' class="ui-widget work_type">'+ element.worktype_name +'</p>')
		     // alert(element.slug + " " +  );
		    });
});
};


var LoadClients = function() {
$('#mytable tbody').html("");
$.getJSON( "/rnr/clients_all", function(data) {
table = "";//"<table id='client_table' class='ui-widget ui-widget-content'>"
      $.each( data, function( index, element ) {
	var items = [];
	row = ""
	row =row.concat("<tr>");
	
	row =row.concat("<td id=" +  element.client_slug + ">");
	row =row.concat(element.attribs.client_name);
	row =row.concat("</td>");
	
	row =row.concat("<td id=" +  element.attribs.client_language__slug + ">");
	row =row.concat(element.attribs.client_language__language_name);
	row =row.concat("</td>");
	row =row.concat("<td>");
	
	$.each(element.contacts, function(index, element) {
		btn = '<button ' + 'id="' + element.slug +'" role="button" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only del_contact_button" type="button"><span class="ui-button-icon-primary ui-icon ui-icon-closethick"></span></button>'
		
	    row =row.concat("<div class=contact_email id='"+element.slug + "'>" + element.contact_email + btn + "</div>");
	});
	row =row.concat("</tr>");
	table = table.concat(row);
});
      //table = table.concat("</table>");
      $('#mytable tbody').append(table);
      
});
};


var LoadDelDialog = function() {
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







var CreateUser = function(){
	//send form data as ajax
	//alert("sended");
	var client_name = $( "#client_name" ).val();
	var client_language = $( "#client_language" ).val();
	var client_emails = $( "#client_emails" ).val();
	//alert (client_emails.split(","));
	//add_new_client
	
/*	
	$.ajax("/rnr/add_new_client", {
	    data : JSON.stringify(myJSObject),
	    contentType : 'application/json',
	    type : 'POST',
	});
	
	
	
	 $.post("/rnr/clients_all", {
    ajax: "true",
    action: "",
    'csrfmiddlewaretoken':getCookie('csrftoken')
	
	
*/	
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
		$("#client_add_errors").html("");
		 $('#frm_add_client').trigger("reset");
		 $('#dlg_add_user').dialog("close");
		 LoadClients();
		return true;
	}
	else{
		$("#client_add_errors").html(data);
		return false;
	};	
	});
	
	
	//alert(client_name + client_language +client_emails);
//	$(this).dialog.("close");
};


$(document).ready(function(){
	LoadClients();
	LoadWorkTypes();
	
	LoadDelDialog();
//	LoadWorkTypes();
	$( "#dlg_add_user" ).dialog({
        autoOpen: false,
        height: 400,
        width: 450,
        modal: true,
        buttons: {
        	"Create User": function(){CreateUser();        	
        	},//$(this).dialog("close");},
        	Cancel: function() {$(this).dialog("close");
        	$('#frm_add_client').trigger("reset");
        	$("#client_add_errors").html("");}
				
         },
         title: "Add new Client",
//         position: {
//            my: "left center",
//            at: "left center"
//         },
        
        });
	
	$( "#opener" ).button();
    $( "#opener" ).click(function() {
        $( "#dlg_add_user" ).dialog( "open" );
     });
    
    
    
    $( "#opn_confirm_del" ).button();
    $( "#opn_confirm_del" ).click(function() {
        $( "#dlg_confirm_del_contact" ).dialog( "open" );
     });
    
    
	});


$(window).load(function() {
	 // executes when complete page is fully loaded, including all frames, objects and images
	 //alert("window is loaded");
	 
	$( "#mytable tbody button" ).click(function() {
  	  //$( "#dlg_confirm_del_contact" ).dialog( "open" );
        var cid = $(this).attr("id");
        var cont = $(this).parent().text();
        //alert(cont);
        $("#del_contact").text(cont);
        ans = $( "#dlg_confirm_del_contact" ).dialog( "open" );
        alert(ans);
        if (ans===true){
        	$("div #"+cid).remove();
        };
        //alert(k);
        
        
     });
	 
	});
