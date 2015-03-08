//used in $("#work_filter_number").typeahead()
var work_numbers = [];

//get all work types in json format {slug:name}
function get_worktypes_all_json()
	{
	$('#work_type option').remove();
	$.getJSON( "/rnr/get_worktypes_all_json", function(data)
		{
		$.each( data, function( index, element )
			{
			$("#work_type").append("<option value=" + element.worktype__slug + ">" + element.worktypedesc + "</option>");
			});
		});
	};

// Get all locations as json {slug, name}, append data to select_option location
function get_locations_all_json()
	{
	$('#work_location option').remove();
	$.getJSON( "/rnr/get_locations_all_json", function(data)
		{
		$.each( data, function( index, element )
			{
			$("#work_location").append("<option value=" + element.worklocation__slug + ">" + element.worklocdesc + "</option>");
			});
		});
	};


//Get regions based on selected location as json, append data to select_option work_region
function get_regions()
	{
	var location_slug = $("#work_location option:selected").attr("value");
	$("#work_region").html("");	
	$.getJSON( "/rnr/get_regions_json", {"location_slug":location_slug} , function(data)
		{
		$.each(data, function(index, element)
			{
			$("#work_region").append("<option value=" + element.workregion__slug + ">" + element.workregdesc + "</option>")
			});
		}).done(function()
			{
			$("#work_region").prop("selectedIndex",-1);
			});
	};

//get total count of works in database, displayed on 
function get_works_total_count()
	{
	$.getJSON( "/rnr/get_works_total_count", function(data)
		{
		$("#works_total").text(data.work_count);
		},'json');
	};

//get len queue
function get_message_queue_len()
	{
	$.getJSON("/rnr/get_message_queue_len", function(data)
		{
		$("#queue_len").text(data.message_queue_len);
		},'json');
	};

	
	
//get len queue
function reset_message_queue()
	{

	$.post("/rnr/reset_message_queue", {
		ajax: "true",
		"reset_queue": true
	}).error(function(error){
		alert(error.status);
	}).done(function(){
		//alert("complete");
		LoadWorks();
	});
	
};

	
	
	
	
	
	

	
//Load works in table
function LoadWorks()
	{
	//Clear existing data, place placeholder
	$('#existing_works tbody > tr').remove();
	//Get works info from server in json
	//get_work_numbers_json();
	//get_works_total_count();
//	get_message_queue_len();
	var work_filter_pending = $("#work_filter_pending").prop('checked');
	var work_filter_upcoming = $("#work_filter_upcoming").prop('checked');
	var work_filter_completed = $("#work_filter_completed").prop('checked');
	var work_filter_number = $("#work_filter_number").val();
	var work_filter_from = $("#work_filter_from").val();
	var work_filter_to = $("#work_filter_to").val();
	//alert (work_filter_from);
	//show WIP indicator
	$('#wip_image').css({display:'inline'});
	$('#btn_filter_works').prop('disabled',true);
	$.getJSON( "/rnr/get_works_json",
			{
			"work_filter_pending":work_filter_pending,
			"work_filter_upcoming":work_filter_upcoming,
			"work_filter_completed":work_filter_completed,
			"work_filter_number":work_filter_number,
			"work_filter_from": work_filter_from,
			"work_filter_to": work_filter_to
			
			}
			).done(function(data)
				{
				$("#works_selected").text(data.length);
				$.each( data, function( index, element )
						{
						var row = "";
					//success, error, warning, info
						cls_work_status = "";
						switch (element.work_state)
							{
							case "Upcoming":
								cls_work_status = 'class="success tr_work"'
								break;
							case "Pending":
								cls_work_status = 'class="warning tr_work"'
								break;
							case "Completed":
								cls_work_status = 'class="info tr_work"'
								break;
							case "Canceled":
								//alert("canceled work" + element.work_number);
								cls_work_status = 'class="active tr_work"'
								break;
							}
						row =row.concat("<tr id=" +
								element.slug +
								" " +
								cls_work_status +
								'data-toggle="context" data-target="#WorkContextMenu">');
						row =row.concat("<td>");
						row =row.concat(element.work_number);
					//add notification counters
						if (element.init_notifications != "0")
							{
							row = row.concat('<a href="/rnr/notifications/?work_slug=' +
								element.slug +
								'&notification_type=notification&notification_state=init' +
								'"><span class="badge init_notifications">' +
								element.init_notifications +
								'</span></a>')
							};
						if (element.sent_notifications != "0")
							{
							row = row.concat('<a href="/rnr/notifications/?work_slug=' +
								element.slug +
								'&notification_type=notification&notification_state=sent' +
								'"><span class="badge sent_notifications">' +
								element.sent_notifications +
								'</span></a>')
							};
						if (element.sent_error_notifications != "0")
							{
							row = row.concat('<a href="/rnr/notifications/?work_slug=' +
									element.slug +
									'&notification_type=notification&notification_state=sent_error' +
									'"><span class="badge sent_error_notifications">' +
									element.sent_error_notifications +
									'</span></a>')
							};
						if (element.init_cancel_notifications != "0")
							{
							row = row.concat('<a href="/rnr/notifications/?work_slug=' +
								element.slug +
								'&notification_type=cancel&notification_state=init' +
								'"><span class="badge init_cancel_notifications">' +
								element.init_cancel_notifications +
								'</span></a>')
							};
						if (element.sent_cancel_notifications != "0")
							{
							row = row.concat('<a href="/rnr/notifications/?work_slug=' +
								element.slug +
								'&notification_type=cancel&notification_state=sent' +
								'"><span class="badge sent_cancel_notifications">' +
								element.sent_cancel_notifications +
								'</span></a>')
							};
						if (element.sent_error_cancel_notifications != "0")
							{
							row = row.concat('<a href="/rnr/notifications/?work_slug=' +
								element.slug +
								'&notification_type=cancel&notification_state=sent_error' +
								'"><span class="badge sent_error_cancel_notifications">' +
								element.sent_error_cancel_notifications +
								'</span></a>')
							};
						row =row.concat("</td>");
						row =row.concat("<td>");
						row =row.concat(element.work_type);
						row =row.concat("</td>");
						
						row =row.concat("<td>");
						row =row.concat(element.work_created_date);
						row =row.concat("</td>");
						
						row =row.concat("<td>");
						row =row.concat(element.work_start_date);
						row =row.concat("</td>");
						
						
						row =row.concat("<td>");
						row =row.concat(element.work_end_date);
						row =row.concat("</td>");
						
						row =row.concat("<td>");
						row =row.concat(element.work_region);
						row =row.concat("</td>");
						
						row =row.concat("</tr>");
						
						$('#existing_works tbody').append(row);
					
						});
					$('#wip_image').css({display:'none'});
					$('#btn_filter_works').prop('disabled',false);
				}).error(function(){
					//something wrong with server
					alert('Server returned an error while getting work list.');
					$('#wip_image').css({display:'none'});
					$('#btn_filter_works').prop('disabled',false);
					
				});
	setTimeout(get_work_numbers_json, 5000);
	//get_work_numbers_json();
	get_message_queue_len();
	get_works_total_count();
	};

//get cookie from client browser
function getCookie(name)
	{
	var cookieValue = null;
	if (document.cookie && document.cookie != '')
	{
	var cookies = document.cookie.split(';');
	for (var i = 0; i < cookies.length; i++)
		{
		var cookie = jQuery.trim(cookies[i]);
		if (cookie.substring(0, name.length + 1) == (name + '='))
			{
			cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
			break;
			}
		}
	}
	return cookieValue;
	};

//set selected filter flags in cookie
function setFilterFlags()
	{
	var c = getCookie("filter_works")
	if (c != null)
		{
		c=c.replace(/\\054/g, ',');
		var n = JSON.parse(c);
		n = JSON.parse(n);
		
		//var filter_from_date = '2009-11-02';
		//var date_parts = filter_from_date.match(/(\d+)/g)
		//alert (date_parts);
		//realdate = new Date(date_parts[0], date_parts[1], date_parts[2])
		//alert(realdate);
//		$("#work_flter_from").val(n.work_filter_from);
		//$("#work_flter_to").datepicker({dateFormat: 'yy-mm-dd'});
		//$("#work_flter_to").datepicker('setDate', realdate);
		$("#work_filter_number").val(n.work_filter_number);
		$("#work_filter_upcoming").prop('checked', n.work_filter_upcoming==='true');
		$("#work_filter_pending").prop('checked', n.work_filter_pending==='true');
		$("#work_filter_completed").prop('checked', n.work_filter_completed==='true');
		//alert(n.work_filter_to);
		//alert(n.work_filter_from);
		
		}
	else
		{
		$("#work_filter_pending").prop('checked', true);
		$("#work_filter_upcoming").prop('checked', true);
		}
	};


function CreateWork()
	{
	var work_number = $( "#work_number" ).val();
	var work_type = $( "#work_type" ).val();
	var work_start_datetime = $('#start_date_datepicker').val() + " " + $('#work_start_time').val();
	var work_end_datetime = $('#end_date_datepicker').val() + " " + $('#work_end_time').val();
	var work_region = $( "#work_region" ).val();
	reset_add_work_dialog(false);
	var posting = $.post( "/rnr/add_new_work",
		{
		ajax: "true",
		"work_number": work_number,
		"work_type" : work_type,
		"work_start_datetime" : work_start_datetime,
		"work_end_datetime":work_end_datetime,
		"work_region":work_region,
		'csrfmiddlewaretoken':getCookie('csrftoken'),
		});
		// Put the results in a div
		posting.done(function( data )
			{
			//workaround, result is string, not json object.
			//alert(data);
			//var n = JSON.parse(data);
			//alert(n);
			if (data.success===true)
				{
				//alert()
//TODO reset dialog add work
				$("#dlg_add_work").modal("hide");
				reset_add_work_dialog(true);
				LoadWorks();
				}
			else
				//n object consists of error - app error and errors - form error
				{
				//if error in form fields:
				if (data.errors)
					{
					//alert(data.errors);
					
					if (data.errors.work_start_datetime)
						{
						//alert("error start time");
						
						$("#cg_start_date").removeClass("has-success");
						$("#cg_start_date").addClass("has-error");
						$("#hb_start_date").text(data.errors.work_start_datetime);
						
						
						}
					
					if (data.errors.work_end_datetime)
						{
						//alert("error end time");
						
						$("#cg_end_date").removeClass("has-success");
						$("#cg_end_date").addClass("has-error");
						$("#hb_end_date").text(data.errors.work_end_datetime);
						
						
						}
					
					if (data.errors.work_number)
						{
						$("#cg_work_number").removeClass("has-success");
						$("#cg_work_number").addClass("has-error");
						$("#hb_work_number").text(data.errors.work_number);
						
						}
					}
				if (data.error)
					{
					$("#cg_work_add_app_errors").removeClass("has-success");
					$("#cg_work_add_app_errors").addClass("has-error");
					$("#hb_work_add_app_errors").text(data.error);
					}
				//$("#cg_work_number").removeClass("has-success");
				//$("#cg_work_number").addClass("has-error");
				//$("#hb_work_number").text(data.error);
				};
			});
	};

//reset fields if full or warnings only
function reset_add_work_dialog(full)
	{
	if (full)
		{
		//clear values
		$("#work_number").val("");
		
		$("#start_date_datepicker").val("");
		$("#work_start_time").val("");
		
		$("#end_date_datepicker").val("");
		$("#work_end_time").val("");
		
		//clear warnings
		reset_add_work_dlg_warnings();
		}
	else
		{
		reset_add_work_dlg_warnings();
		}
	};

function reset_add_work_dlg_warnings()
	{
	$("#cg_work_number").removeClass("has-error");
	$("#cg_work_number").removeClass("has-success");
	$("#hb_work_number").text("");
	
	$("#cg_start_date").removeClass("has-error");
	$("#cg_start_date").removeClass("has-success");
	$("#hb_start_date").text("");
	
	$("#cg_end_date").removeClass("has-error");
	$("#cg_end_date").removeClass("has-success");
	$("#hb_end_date").text("");
	
	
	$("#cg_work_add_app_errors").removeClass("has-error");
	$("#cg_work_add_app_errors").removeClass("has-success");
	$("#hb_work_add_app_errors").text("");
	
	};

function reset_FilterFlags(){
	//reset checkboxes
	$("#work_filter_pending").prop('checked', true);
	$("#work_filter_upcoming").prop('checked', true);
	$("#work_filter_completed").prop('checked', false);
	//reset fields
	$("#work_filter_from").val("");
	$("#work_filter_to").val("");
	$("#work_filter_number").val("");
};

	function init_work_menu(){
		
			  var $WorkContextMenu = $("#WorkContextMenu");
			  $WorkContextMenu.hide();
			  $("body").on("contextmenu", "#existing_works tr.tr_work", function(e) {
				  //alert(e.pageX);
				var obj = $(this).closest("tr.tr_work");
				work_slug = obj.attr("id");
				obj.css("font-weight","Bold");
				
				$("#WorkContextMenu ul li a").eq(0).attr("href","/rnr/notifications/?work_slug="+work_slug);
				$("#WorkContextMenu ul li a").eq(1).attr("href","/rnr/notifications/?work_slug="+work_slug+"&create_notification=yes");
				
				$WorkContextMenu.css({
				      display: "block",
				      left: e.pageX,
				      top: e.pageY
				   });
				
			return false;
			});
			
				$WorkContextMenu.on("click", "li", function() {
					
					if ($(this).index()===2){
						//view_notification(selected_notification.attr("id"));
						//alert("menu 3 selected");
						
						$("#dlg_send_messages").modal('show');
						
						
						
						
						
					  }
					  else if ($(this).index()===3){
						  if (confirm('Уверены, что хотите отменить работы?')){
							gen_cancel(work_slug);
						  }
						  
						  
						  //alert("menu 4 selected. Not implemented yet");
						  
						  
						  
						  
						  //var send_notif_error = $("#send_error_messages").prop('checked');
							//alert (send_notif_error);
						  
							
							//alert("send");
						  
					  }
					  else if ($(this).index()===5){
						//alert("menu 5 selected");
						if (confirm('Уверены, что хотите удалить работы?')){
							delete_work(work_slug);
							}
					  }
				   $WorkContextMenu.hide();
				});
			  
			  
			  $WorkContextMenu.on("click", "a", function() {
				  //alert($(this).html());
			     $WorkContextMenu.hide();
			     $(this).closest("tr.tr_work").css("font-weight","normal");
			  });
			  
			  
			  
			  $("body").on("click", function(){
				  $WorkContextMenu.hide();
				$("#existing_works tr").css("font-weight","normal")  
			  });
			  
	};
	
	
	function gen_cancel(work_slug){
		$.post("/rnr/gen_cancel", {
			ajax: "true",
			"work_slug": work_slug
		}).error(function(error){
			alert(error.status);
		}).done(function(){
			//alert("complete");
			LoadWorks();
		});
	}
	
	function send_notifications(work_slug){
		//notification types
		var send_notif = $("#SpamNotifications").prop('checked');
		var send_notif_cancel = $("#SpamNotifCancel").prop('checked');
		//
		var send_error_messages = $("#send_error_messages").prop('checked');
		var send_init_messages = $("#send_init_messages").prop('checked');
		var send_sent_messages = $("#send_sent_messages").prop('checked');
		
		
		$.post( "/rnr/send_all_notifications", {
			ajax: "true",
			"send_notif":send_notif,
			"send_notif_cancel":send_notif_cancel,
			"send_error_messages":send_error_messages,
			"send_init_messages":send_init_messages,
			"send_sent_messages":send_sent_messages,
			
			"work_slug": work_slug,
			'csrfmiddlewaretoken':getCookie('csrftoken'),
		},"json").error(function(error){
			
			alert("error" + error.status);
			
		}).done(function(data){
			//alert(data);
			LoadWorks();
		});
		
	};
	
	function delete_work(work_slug){
		$.post( "/rnr/delete_work", {
			ajax: "true",
			"work_slug": work_slug,
			'csrfmiddlewaretoken':getCookie('csrftoken'),
		},"json").error(function(error){
			alert("error" + error.status)
		}).done(function(){
			LoadWorks();
		});
		
	};
	
	
	function get_work_numbers_json(){
		$.getJSON( "/rnr/get_work_numbers_json", function(data) {
			work_numbers = [];
			$.each( data, function( index, element ){
				work_numbers.push(element.work_number)
			});
			//clients = data;
			//alert(clients);
			//alert(work_numbers);
			
			//var autocomplete = $("work_filter_number").typeahead();
			//autocomplete.data('typeahead').source = work_numbers;
			
			$("#work_filter_number").typeahead('destroy');
			$("#work_filter_number").typeahead({
				source:work_numbers, 
				updater:function(item){
					//alert(item);
					return item;
						}});
		},'json');
};
	
	$(document).ready(function(){
		//Load_dlg_add_work();
		setFilterFlags();
		$("#WorkContextMenu").contextmenu();
		init_work_menu();
		get_worktypes_all_json();
		get_work_numbers_json();
		get_locations_all_json();
		LoadWorks();
		//Load_dlg_del_contact();
		$( "#create_work" ).click(function() {
			CreateWork();
		});
		//LoadClients();
		//get_languages_all_json();
		 $( "#start_date_datepicker" ).datepicker({
		 showButtonPanel: true
		 });
		 //$( "#work_filter_number" ).datepicker({
		//	 showButtonPanel: true,
		//	 dateFormat:'yy-mm-dd'
		//	 });
	 $( "#end_date_datepicker" ).datepicker({
		 showButtonPanel: true
		 });
		 $('#work_start_time').timepicker({ 'timeFormat': 'H:i' });
		 $('#work_end_time').timepicker({ 'timeFormat': 'H:i' });
	
		 $("#work_location").prop("selectedIndex",-1);
		$("#work_region").prop("selectedIndex",-1);
			
		$('#work_location').change(function(){
			get_regions();
		});
		
		$("#work_filter_from").datepicker({
			 showButtonPanel: false,
			 dateFormat: 'yy-mm-dd',
			 });
		$("#work_filter_to").datepicker({
			 showButtonPanel: false,
			 dateFormat: 'yy-mm-dd'
			 });
		
//		$('#btn_do_spam').click(function(){
//			send_notifications(work_slug);
//		});
		
		//$('#change_lang_ru').click(function(){
		//	set_language("ru");
		//	});
		
		//$('#change_lang_en').click(function(){
		//	set_language("en");
		//	});
		
		
		
		//var work_filter_pending = $("#work_filter_pending").prop('checked');
		//var work_filter_upcoming = $("#work_filter_upcoming").prop('checked');
		//var work_filter_completed = $("#work_filter_completed").prop('checked');
		
		
		//$('#work_filter_pending').on("click", LoadWorks);
		//$('#work_filter_upcoming').on("click", LoadWorks);
		$('#btn_filter_works').on("click", LoadWorks);
		
		$('#btn_reset_queue').on("click", reset_message_queue);
		
		$('#btn_filter_reset').on("click", reset_FilterFlags);
		
		$( '#frm_load_file' )
		  .submit( function( e ) {
			  e.preventDefault();
			  $("#file_parse_errors").html("");
			  $("#file_parse_errors").html("");
			  
			  $("#btn_load_file_subm").prop('disabled',true);
			  $("#wip_image_file_parse").css({display:'inline'});

			  $.ajax( {
		      url: '/rnr/load_works',
		      type: 'POST',
		      data: new FormData( this ),
		      processData: false,
		      contentType: false
		    },"json").done(function(data){
		    	
		    	var k = jQuery.parseJSON(data);
		    	if (k.success===true){
		    		//alert("success");
		    		$("#dlg_load_file").modal("hide");
		    		LoadWorks();
		    	}
		    	else{
		    		$("#file_parse_errors").html(k.error);
		    		//alert(k.error);
		    	}
		    	$("#btn_load_file_subm").prop('disabled',false);
		    	$("#wip_image_file_parse").css({display:'none'});
		    }).error(function(){
		    	//if something is completely wrong, reset process indicator, add warning
		    	$("#btn_load_file_subm").prop('disabled',false);
		    	$("#wip_image_file_parse").css({display:'none'});
		    	$("#file_parse_errors").html("http server returned an error.");
		    });
		    e.preventDefault();
		  } ); 
		
		$('#frm_do_spam')
			.submit(function(e)
				{
				e.preventDefault();
				
				//var frm_data = ;
				//frm_data.work_slug = work_slug;
				$("#dlg_send_messages").modal("hide");
				send_notifications(work_slug);
				setTimeout(get_message_queue_len(), 2);
				e.preventDefault();
				});
					
		
		
	});
	
function sleep(msecs){
	var start = new Date().getTime();
	for (var i=0; i< 1e7; i++){
		if ((new Date().getTime()-start)>msecs){
			break;
		}
	}
};