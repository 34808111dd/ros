
	var work_slug;
	var clients=[];
	var mw_tr_obj = "";
	var outage_tr_obj = "";
	var outage_types = {};
	var notification_types = [];
	var work_numbers = [];
	


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
	
function getParameterByName(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
};




function get_work_numbers_json(){
		$.getJSON( "/rnr/get_work_numbers_json", function(data) {
			work_numbers = []
			$.each( data, function( index, element ){
				work_numbers.push(element.work_number)
			});
			//clients = data;
			//alert(clients);
			//alert(client_names);
			
			$("#notification_filter_work_number").typeahead({
				source:work_numbers, 
				updater:function(item){
					//alert(item);
					return item;
					}});
		},'json');
};

function filter_notifications(){
	var work_number = $("#notification_filter_work_number").val();
	$.getJSON( "/rnr/get_work_slug", {"work_number":work_number}, function(data) {
		//alert(data.slug);
		work_slug = data.slug;
	}).done(function(){
		//alert("time to filter");
		get_notifications();
	});
	
	
}

//REWORK IT
	function get_notifications(){
		//clear table
		$('#existing_notifications tbody > tr').remove();
		//if no work_slug presented - 
		
		//work_slug = getParameterByName("work_slug");
		if (work_slug != null){
			//$("#notification_filter_work_number").val()
			get_work_name(work_slug);
			get_client_names_json();
		
			notification_type = getParameterByName("notification_type");
			notification_state = getParameterByName("notification_state")
		
			params = {}
		
			params.work_slug = work_slug;
			
			if (notification_type != "") {
				params.notification_type = notification_type;
			}
			
			if (notification_state != "") {
				params.notification_state = notification_state;
			}
			
			
			$.getJSON( "/rnr/get_notifications_json", params , function(data){
				$.each(data, function(index, element){
					var row = "";
					row =row.concat("<tr id=" +  element.slug + ' class="tr_notification" data-toggle="context" data-target="#NotificationContextMenu">');
					row =row.concat('<td class="td_notification_client">');
					row =row.concat(element.notification_client__client_name);
					row =row.concat("</td>");
					var notification_state_class = ' class="' + element.state_class +'"';
					row =row.concat('<td' + notification_state_class + '>');
					row =row.concat(element.notification_state__notificationstate_name);
					row =row.concat("</td>");
					var notification_type__notificationtype_name = ' class="' + element.type_class +'"';
					row =row.concat('<td' + notification_type__notificationtype_name + '>');
					row =row.concat(element.notification_type__notificationtype_name);
					row =row.concat("</td>");
					$('#existing_notifications tbody').append(row);
					
				});
			});
//TODO - REWORK to avoid request with null work_number
	
		
			$("#work_number").prop("disabled",true);
			
			
			//if going from add_new_notification
			if (getParameterByName("create_notification") && open_dialog==true){
				$("#dlg_add_notification").modal("show");
			}
		}
	
	};
	
	function get_notification_type_all_json() {
		$('#notification_type option').remove();
		$.getJSON( "/rnr/get_notification_type_all_json", function(data) {
			$.each( data, function( index, element ) {
				$("#notification_type").append("<option value=" + element.notificationtype__slug + ">" + element.notificationtypedesc + "</option>");
			});
			notification_types = data;
		});
	};
	

	function get_outage_type_all_json() {
		$('#outage_type option').remove();
		$.getJSON( "/rnr/get_outage_type_all_json", function(data) {
			$.each( data, function( index, element ) {
				outage_types[element.outagetype_name] = element.slug;
				$("#outage_type").append("<option value=" + element.outagetype__slug + ">" + element.outagetypedesc + "</option>");
			});
		});
	};


function get_client_names_json() {
	$.getJSON( "/rnr/get_client_names_json", function(data) {
		client_names = []
		$.each( data, function( index, element ){
			client_names.push(element.client_name)
		});
		clients = data;
		//alert(clients);
		//alert(client_names);
		
		$("#client_name").typeahead({
			source:client_names, 
			updater:function(item){
				//alert(item);
				return item;
				}});
	},'json');
	};




/*
	function get_client_names_json() {
		$.getJSON( "/rnr/get_client_names_json", function(data) {
			alert(data);
			$("#client_name").typeahead({
				source:data, 
				updater:function(item){
					//alert(item);
					return item;
					}
					})},'json');
			}
	
*/	
	
	function get_work_name(slug) {
		$.getJSON( "/rnr/get_work_name_json", {"slug":slug},function(data) {
		
		}).done(function(data){
			$("#work_number").val(data.work_number);
			$("#notification_filter_work_number").val(data.work_number);
		})
		;
	};
	
	function init_MW_menu(){
	//init MW menu
		var $MWContextMenu = $("#MWContextMenu");
		$MWContextMenu.hide();
		$("#notification_outages").on("contextmenu", "td.MW_td", function(e) {
		mw_tr_obj = $(this).closest("tr.MW_tr");
		mw_tr_obj.css("font-weight","Bold");
		$MWContextMenu.css({left: e.pageX, top: e.pageY, display:"block"});
		    return false;
		  });
		  $MWContextMenu.on("click", "li", function() {
			  if ($(this).index()===0){
				  mw_tr_obj.remove();
			  }
			  else if ($(this).index()===1){
				  //alert("create outage");
				  $("#dlg_add_outage").modal("show")
			  }
		  $MWContextMenu.hide();
		  });
		
		$(document).click(function(){
		$MWContextMenu.hide();
		$("#notification_outages tr").css("font-weight","normal") 
		});
	};
	
	
	function init_outage_menu(){
	  //init Outage menu
		var $OutageContextMenu = $("#OutageContextMenu");
	  	$OutageContextMenu.hide();
	  	$("#notification_outages").on("contextmenu", "td.outage_td", function(e) {
		outage_tr_obj = $(this).closest("tr.outage_tr");
		outage_tr_obj.css("font-weight","Bold")
	    $OutageContextMenu.css({left: e.pageX, top: e.pageY, display:"block"});
	    return false;
	  });
	  
	  $OutageContextMenu.on("click", "li", function() {
		  outage_tr_obj.remove();
	    $OutageContextMenu.hide();
	  });
	  $(document).click(function(){
		$OutageContextMenu.hide();
		$("#notification_outages tr").css("font-weight","normal") 
		});
};

var selected_notification="";

function init_notification_menu(){
	var $NotificationContextMenu = $("#NotificationContextMenu");
	
	$("body").on("contextmenu", "#existing_notifications tr.tr_notification", function(e) {
		
		selected_notification = $(this).closest("tr.tr_notification");
	   $NotificationContextMenu.css({
	      display: "block",
	      left: e.pageX,
	      top: e.pageY
	   });
	   return false;
	});

	$NotificationContextMenu.on("click", "li", function() {
		
		if ($(this).index()===0){
			view_notification(selected_notification.attr("id"));
		  }
		  else if ($(this).index()===1){
			//send to client
			  if (confirm('Уверены, что хотите послать это клиенту?')){
				send_notification(selected_notification.attr("id"));
				}
		  }
		  else if ($(this).index()===2){
			  //alert("delete, not implemented yet");
			  if (confirm('Уверены, что хотите удалить оповещение?')){
				  delete_notification(selected_notification.attr("id"));
					}
		  }
		
	   $NotificationContextMenu.hide();
	});  
	
	$(document).click(function(){
		$NotificationContextMenu.hide();
		
	});
};

//response {'success':True,'error':[]} if success, else Http400
function delete_notification(notification_slug){
	$.post("/rnr/del_notification", {
		ajax: "true",
		"notification_slug": notification_slug
	}).error(function(error){
		alert(error.status);
	}).done(function(){
		//alert("complete");
		get_notifications();
	});
};


function view_notification(notification_slug){
	
	$.getJSON( "/rnr/view_notification", {"notification_slug":notification_slug},function(data) {
		$("#dlg_view_notification").modal("show");
		$("#dlg_view_notification_subject").val(data.notification_subject);
		$("#dlg_view_notification_text").val(data.notification_complete_text);
		//alert(data.notification_complete_text);
	});
	
	//$.getJSON( "/rnr/view_notification", {"notification_slug":notification_slug},function(data) {
	//$("#dlg_view_notification").modal("show");
	//$("#dlg_view_notification_text").val(data);
	//alert(data);
	//}).done(function(data){
	//	alert(data);
	//	$("#dlg_view_notification_text").val(data);
	//	$("#dlg_view_notification").modal("show");
	//});
	
};


function send_notification(notification_slug){
	$.post("/rnr/send_notification", {'notification_slug':notification_slug, 'csrfmiddlewaretoken':getCookie('csrftoken')}, function(data){
		if (data==="OK"){
			selected_notification.find("td:eq(1)").attr("class","success");	
		}
		else
			{
			selected_notification.find("td:eq(1)").attr("class","danger");	
			}
	
		
	});
}


function gen_notification(){
	var client_slug;
	var notification_type_slug = $("#notification_type option:selected").attr("value");
	var client_name = $("#client_name").val()
	
	$.each(clients, function(index,element){
		if (element.client_name === client_name){
			client_slug = element.slug;
		}
	});
	
	var json_notif = {
			"client_slug":client_slug,
			"work_slug":work_slug,
			"notification_type_slug":notification_type_slug,
			"MW":[]	}
	
	function CUR_mw(){
		this.mw_name = "";
		this.mw_outages = [];
	}
	
	var cur_mw = new CUR_mw();
	var old_mw_name = "";
	
	$("#notification_outages tr").each(function(){
		$this = $(this);
		if ($this.attr("class")==="MW_tr info"){
			//if cur mw, push
			if(cur_mw.mw_name!=""){
				json_notif.MW.push(cur_mw);
			}
			cur_mw = new CUR_mw()
			cur_mw.mw_name = $(this).children("td").text();
		}
		else if($this.attr("class")==="outage_tr"){	
			var cur_outage = {
					outage_type: $(this).children("td:eq(0)").attr("id"),
					outage_channel: $(this).children("td:eq(1)").text(),
			};
			
			cur_mw.mw_outages.push(cur_outage);
		}});
	
	json_notif.MW.push(cur_mw);
	var s = JSON.stringify(json_notif);
	
	$.post("/rnr/gen_notification", {'test':s, 'csrfmiddlewaretoken':getCookie('csrftoken')}, function(data){
		//alert(data.subject);
		//alert(data.body);
		$("#notification_subject").val(data.subject);
		$("#notification_text").val(data.body);
	},"json");
	
};

var open_dialog = true;

function save_notification(){
	var client_slug;
	var notification_type_slug = $("#notification_type option:selected").attr("value");
	var client_name = $("#client_name").val()
	
	$.each(clients, function(index,element){
		if (element.client_name === client_name){
			client_slug = element.slug;
		}
	});
	
	var json_notif = {
			"client_slug":client_slug,
			"work_slug":work_slug,
			"notification_type_slug":notification_type_slug,
			"MW":[]	}
	
	function CUR_mw(){
		this.mw_name = "";
		this.mw_outages = [];
	}
	
	var cur_mw = new CUR_mw();
	var old_mw_name = "";
	
	$("#notification_outages tr").each(function(){
		$this = $(this);
		if ($this.attr("class")==="MW_tr info"){
			//if cur mw, push
			if(cur_mw.mw_name!=""){
				json_notif.MW.push(cur_mw);
			}
			cur_mw = new CUR_mw()
			cur_mw.mw_name = $(this).children("td").text();
		}
		else if($this.attr("class")==="outage_tr"){
			//outage_type: outage_types[$(this).children("td:eq(0)").attr("id")],
			var cur_outage = {
					outage_type: $(this).children("td:eq(0)").attr("id"),
					outage_channel: $(this).children("td:eq(1)").text(),
			};
			//alert(cur_outage);
			//alert($(this).children("td:eq(0)").attr("id"));
			cur_mw.mw_outages.push(cur_outage);
		}});
	
	json_notif.MW.push(cur_mw);
	var s = JSON.stringify(json_notif);
	notification_text = $("#notification_text").val();
	notification_subject = $("#notification_subject").val();
	$.post("/rnr/save_notification", {'test':s, 'notification_text':notification_text, 'notification_subject':notification_subject, 'csrfmiddlewaretoken':getCookie('csrftoken')}, function(data){
		//alert(data);
		$("#dlg_add_notification").modal("hide");
		open_dialog = false;
		get_notifications();
	} );
	
};

function update_notification(){
	var notification_slug = selected_notification.attr("id");
	var message_subject = $("#dlg_view_notification_subject").val();
	var message_body = $("#dlg_view_notification_text").val();
	//alert(notification_slug);
	//alert(message_subject);
	//alert(message_body);
	
	
	$.post("/rnr/update_notification", {'notification_slug':notification_slug, 'message_subject':message_subject, 'message_body':message_body,'csrfmiddlewaretoken':getCookie('csrftoken')}, function(data){
		//alert(data);
	});
		
	
	//$.post( "/rnr/update_notification", {
	//	ajax: "true",
	//	notification_slug: selected_notification,
	//	message_subject: message_subject,
	//	message_body: message_body,
	//});
	
	//.error(function(error){
	//	alert("error" + error.status)
	//}).done(function(){
	//	
	//	alert("done");
	//});
};



$(document).ready(
	function() {
		init_notification_menu();
		init_MW_menu();
		init_outage_menu();
		$("#NotificationContextMenu").contextmenu();
		$("#MWContextMenu").contextmenu();
		$("#OutageContextMenu").contextmenu();
		
		$("#create_mw").click(function() {
			$("#dlg_add_MW").modal("show");
		});
		
		get_notification_type_all_json();
		get_outage_type_all_json();
		get_work_numbers_json();
		
		work_slug = getParameterByName("work_slug");
		//alert(work_slug);
		
		$("#btn_filter_notifications").click(function(){
			filter_notifications();
		});
		
		$("#start_date_datepicker").datepicker({
			showButtonPanel : true
		});
		$("#end_date_datepicker").datepicker({
			showButtonPanel : true
		});
		$('#MW_start_time').timepicker({
			'timeFormat' : 'H:i'
		});
		$('#MW_end_time').timepicker({
			'timeFormat' : 'H:i'
		});
		$("#generate_notification").click(function(){
			gen_notification();
		});
		$("#save_notification").click(function(){
			save_notification();
		});
		
		$("#update_notification").click(function(){
			update_notification();
		});
		
		$("#add_MW").click(function() {
			var start_time = $('#start_date_datepicker').val() + " " + $('#MW_start_time').val();
			var end_time = $('#end_date_datepicker').val() + " " + $('#MW_end_time').val();
			$("#notification_outages tbody").append('<tr class="MW_tr info"' + '><td colspan="2" class="MW_td">'
												+ start_time + " - " + end_time + "</td></tr>");
		});
		
		$("#add_outage").click(
			function() {
			//$('<tr class="outage_tr"><td  class="outage_td">' + $("#outage_type option:selected").text() + '</td><td class="outage_td">'+ $("#channel_name").val() + '</td></tr>').insertAfter(mw_tr_obj);
				$('<tr class="outage_tr"><td id='+ $("#outage_type option:selected").val() +' class="outage_td">' + $("#outage_type option:selected").text() + '</td><td class="outage_td">'+ $("#channel_name").val() + '</td></tr>').insertAfter(mw_tr_obj);
		});
		get_notifications();
});

