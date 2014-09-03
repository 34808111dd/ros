 



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
    
var get_clients = function()
{
$.post( "/rnr/clients_all", {'csrfmiddlewaretoken':getCookie('csrftoken')})
.done ( function( data ) {alert( "Data Loaded: " + data );});
};

$( "#add_client" ).button().on( "click", get_clients); 