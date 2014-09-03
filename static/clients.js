 



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
    }

var place_all_clients = function(json_clients)
{

};


var get_clients = function()
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




var jqxhr = function() {

$.getJSON( "/rnr/clients_all", function(data) {
table = "<table id='client_table' border=1>"
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
//	row =row.concat("<td>");
//	  $.each(element.contacts);
//	row =row.concat(element.contacts);
//	row =row.concat("</td>");
	row =row.concat("<td>");
	
	
	$.each(element.contacts, function(index, element) {
	    row =row.concat("<div class=email id='"+element.slug + "'>" + element.contact_email + "</div>");
//	    alert(row);
	});
	row =row.concat("</tr>");
	table = table.concat(row);
});
      table = table.concat("</table>");
      $('#mytable').append(table);
});
};


