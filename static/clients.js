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


	function get_languages_all_json() {
		//client_language
		$('#client_language option').remove();
		
		$.getJSON( "/rnr/languages_all", function(data) {
			$.each( data, function( index, element ) {
				$("#client_language").append("<option value=" + element.slug + ">" + element.language_name + "</option>");
				$("#client_update_language").append("<option value=" + element.slug + ">" + element.language_name + "</option>");
			});
		});
	};
	
	function LoadClients() {
		//Clear existing data
		$('#existing_clients tbody > tr').remove();
		//Get data from server in json
		$.getJSON( "/rnr/clients_all", function(data) {
			//for all clients in data
			 
			$.each( data, function( index, element ) {
				var items = [];
				var row = "";
				row =row.concat('<tr class="client">');
				row =row.concat('<td class="client_name" id=' +  element.client_slug + ">");
				row =row.concat(element.attribs.client_name);
				row =row.concat("</td>");
				row =row.concat('<td class="client_display_name"' + ">");
				row =row.concat(element.attribs.client_display_name);
				row =row.concat("</td>");
				row =row.concat("<td id=" +  element.attribs.client_language__slug + ">");
				row =row.concat(element.attribs.client_language__language_name);
				row =row.concat("</td>");
				row =row.concat("<td>");
				//for all contacts in client
				$.each(element.contacts, function(index, element) {
				//<button title="Close" role="button" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only ui-dialog-titlebar-close" type="button"><span class="ui-button-icon-primary ui-icon ui-icon-closethick">
					var	btn = "";//'<span class="btn_del_contact"><i class="glyphicon glyphicon-trash btn_del_contact"></i></span>';
					
					row =row.concat("&nbsp<div class=contact_email id='"+element.slug + "'>" + element.contact_email + btn + "</div>");
				});
				row =row.concat("</tr>");
				$('#existing_clients tbody').append(row);
			});
			
		}).done(function(){
		$(".btn_del_contact").click(function(){
			//alert($(this).attr("id"));
			//alert($(this).closest("div").attr("id"));
			del_contact($(this).closest("div").attr("id"));
		});
		});
	};
	
	
	
	function add_new_client(){
		var client_name = $( "#client_name" ).val();
		var client_language = $( "#client_language" ).val();
		var client_emails = $( "#client_emails" ).val();
		var client_display_name = $("#client_display_name").val();
		var posting = $.post( "/rnr/add_new_client", {
			ajax: "true",
			"client_name": client_name,
			"client_display_name": client_display_name,
			"client_language" : client_language,
			"client_emails":client_emails,
			'csrfmiddlewaretoken':getCookie('csrftoken'),
		},"json");
		// Put the results in a div
		posting.done(function( data ) {
			//alert(data);
			if (data.success === true){
				reset_add_client_dialog(true);
				$("#dlg_add_client").modal('hide');
				
				LoadClients();
				return true;
			}
			else{
				
				reset_add_client_dialog(false);
				
				if (data.errors.client_name){
					$("#cg_client_name").removeClass("has-success");
					$("#cg_client_name").addClass("has-error");
					$("#hb_client_name").text(data.errors.client_name);
				}
				if (data.errors.client_display_name){
					$("#cg_client_display_name").removeClass("has-success");
					$("#cg_client_display_name").addClass("has-error");
					$("#hb_client_display_name").text(data.errors.client_name);
				}
				if (data.errors.client_emails){
					$("#cg_client_emails").removeClass("has-success");
					$("#cg_client_emails").addClass("has-error");
					$("#hb_client_emails").text(data.errors.client_emails);
				}
				return false;
			};	
		});
	};
	
	function reset_add_client_dialog(full){
		if (full){
			$("#client_name").val("");
			$("#cg_client_name").removeClass("has-error");
			$("#cg_client_name").removeClass("has-success");
			$("#hb_client_name").text("");
			
			$("#client_display_name").val("");
			$("#cg_client_display_name").removeClass("has-error");
			$("#cg_client_display_name").removeClass("has-success");
			$("#hb_client_display_name").text("");
			
			$("#cg_client_emails").removeClass("has-error");
			$("#cg_client_emails").removeClass("has-success");
			$("#client_emails").val("");
			$("#hb_client_emails").text("");
			
		}
		else{
		$("#cg_client_name").removeClass("has-error");
		$("#cg_client_name").addClass("has-success");
		$("#hb_client_name").text("");
		
		$("#cg_client_display_name").removeClass("has-error");
		$("#cg_client_display_name").addClass("has-success");
		$("#hb_client_display_name").text("");
		
		$("#cg_client_emails").removeClass("has-error");
		$("#cg_client_emails").addClass("has-success");
		$("#hb_client_emails").text("");
		}
		
	}

	function reset_update_client_dialog(full){
		if (full){
			$("#client_update_name").val("");
			$("#cg_client_update_name").removeClass("has-error");
			$("#cg_client_update_name").removeClass("has-success");
			$("#hb_client_update_name").text("");
			
			$("#client_update_display_name").val("");
			$("#cg_client_update_display_name").removeClass("has-error");
			$("#cg_client_update_display_name").removeClass("has-success");
			$("#hb_client_update_display_name").text("");
			
			$("#cg_client_update_emails").removeClass("has-error");
			$("#cg_client_update_emails").removeClass("has-success");
			$("#client_update_emails").val("");
			$("#hb_client_update_emails").text("");
			
		}
		else{
		$("#cg_client_update_name").removeClass("has-error");
		$("#cg_client_update_name").addClass("has-success");
		$("#hb_client_update_name").text("");
		
		$("#cg_client_update_display_name").removeClass("has-error");
		$("#cg_client_update_display_name").addClass("has-success");
		$("#hb_client_update_display_name").text("");
		
		$("#cg_client_update_emails").removeClass("has-error");
		$("#cg_client_update_emails").addClass("has-success");
		$("#hb_client_update_emails").text("");
		}
		
	}

	
	
	
	function del_contact(slug){
		$.post( "/rnr/del_contact", {
			ajax: "true",
			"contact_slug": selected_contact_slug,
			'csrfmiddlewaretoken':getCookie('csrftoken'),
		},"json").error(function(error){
			alert("error" + error.status)
		}).done(function(data){
			if (data.success===false){
				//alert(data.success);
				//alert(data.errors);
				$("#div_del_contact_error").text(data.errors);
				$("#dlg_error_delete_contact").modal('show');
			};
			
			
			LoadClients();
		});
		
	};
	
	function del_client(slug){
		$.post( "/rnr/del_client", {
			ajax: "true",
			"client_slug": selected_client_slug,
			'csrfmiddlewaretoken':getCookie('csrftoken'),
		},"json").error(function(error){
			alert("error" + error.status)
		}).done(function(){
			LoadClients();
		});
		
	};
	

function get_client_info(slug){
//Get client info and place it into dialog form
	$.getJSON( "/rnr/get_client_info",{'slug':slug}, function(data) {
	//alert(data);
	}).done(function(data){
		$("#client_update_name").val(data.client_name);
		$("#client_update_display_name").val(data.client_display_name);
		$("#client_update_language").val(data.client_language);
		
		$("#client_update_emails").val(data.client_contacts.join(', '));
		$("#dlg_update_client").modal('show');
	});
};

	
function update_client_info(){
//post as a create
	var client_update_name = $( "#client_update_name" ).val();
	var client_update_language = $( "#client_update_language" ).val();
	var client_update_emails = $( "#client_update_emails" ).val();
	var client_update_display_name = $("#client_update_display_name").val();
//	alert('Not implemented yet.');
	var posting = $.post( "/rnr/update_client_info", {
		"ajax": "true",
		"slug": selected_client_slug,
		"client_update_name": client_update_name,
		"client_update_display_name": client_update_display_name,
		"client_update_language" : client_update_language,
		"client_update_emails":client_update_emails,
		'csrfmiddlewaretoken':getCookie('csrftoken'),
	},"json").done(function(data){
		if (data.success === true){
				//alert('success');
				reset_update_client_dialog(true);
				$("#dlg_update_client").modal('hide');
				
				LoadClients();
			}
		else{
			
			reset_update_client_dialog(false);
			
			if (data.errors.client_update_display_name){
				$("#cg_client_update_display_name").removeClass("has-success");
				$("#cg_client_update_display_name").addClass("has-error");
				$("#hb_client_update_display_name").text(data.errors.client_update_display_name);
			}
			if (data.errors.client_update_emails){
				$("#cg_client_update_emails").removeClass("has-success");
				$("#cg_client_update_emails").addClass("has-error");
				$("#hb_client_update_emails").text(data.errors.client_update_emails);
			}
			if (data.errors.client_update_language){
				$("#cg_client_update_language").removeClass("has-success");
				$("#cg_client_update_language").addClass("has-error");
				$("#hb_client_update_language").text(data.errors.client_update_language);
			}
			
		}
	});
	
};
	
	var selected_contact_slug;
	
	function init_DelContactMenu(){
		//init Del contact menu
			var $DelContactMenu = $("#DelContactMenu");
			$DelContactMenu.hide();
			$("body").on("contextmenu", ".contact_email", function(e) {
				selected_contact_slug = $(this).attr("id");
				$DelContactMenu.css({left: e.pageX, top: e.pageY, display:"block"});
			    return false;
			  });
			$DelContactMenu.on("click", "li", function() {
				  if ($(this).index()===0){
					  if (confirm('Уверены, что хотите удалить этот контакт?')){
						  del_contact(selected_contact_slug);
						}
					  
					  //$("#dlg_error_delete_contact").modal('show');
				  }
				  $DelContactMenu.hide();
			  });
			
			$(document).click(function(){
				$DelContactMenu.hide();
			});
		};
	
	var selected_client_slug;
	
		function init_ClientMenu(){
			//init client menu
				var $ClientMenu = $("#ClientMenu");
				$ClientMenu.hide();
				$("#existing_clients").on("contextmenu", "td.client_name", function(e) {
					selected_client_slug = $(this).attr("id");
					$ClientMenu.css({left: e.pageX, top: e.pageY, display:"block"});
				    return false;
				  });
				$ClientMenu.on("click", "li", function() {
					  if ($(this).index()===0){
						  get_client_info(selected_client_slug);
					  }
					  else if ($(this).index()===1){
						  //alert("create outage");
						  if (confirm('Уверены, что хотите удалить клиента?')){
							  del_client(selected_client_slug);
							}
						  
					  }
					  $ClientMenu.hide();
				  });
				
				$(document).click(function(){
					$ClientMenu.hide();
				});
			};
	
	
	
	$(document).ready(function(){
		init_DelContactMenu();
		init_ClientMenu();
		$( "#create_client" ).click(function() {
		add_new_client();
		});
		$("#update_client").click(function(){
			//alert('updating');
			update_client_info();
			
		});
		LoadClients();
		get_languages_all_json();
		
		$("#dlg_add_client").on('hidden.bs.modal', function(){
			
			//alert("full clean");
			reset_add_client_dialog(true);
			
			
		});
		
		$('#dlg_update_client').on('hidden.bs.modal', function(){
			reset_update_client_dialog(true);
		});
		
	});
	
	