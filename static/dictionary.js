var selected_record_slug = '';

function init_RecordMenu(){
//init context menu on record
var $RecordMenu = $("#RecordMenu");
$RecordMenu.hide();

$("#records_table").on("contextmenu", "td", function(e) {
e.preventDefault();
selected_record_slug = $(this).parent().children("td:first").text();
$RecordMenu.css({left: e.pageX, top: e.pageY, display:"block", position:"absolute"});
e.preventDefault();
});
$RecordMenu.on("click", "li", function() {
	if ($(this).index()===0){
		
		if (confirm('Уверены, что хотите удалить запись?')){
			del_dict_record();
			}
		
		$("#records_table").bootstrapTable('refresh');
		}
	$RecordMenu.hide();
	});
	$(document).click(function(){
		$RecordMenu.hide();
	});
};
	
	

function reset_dlg_warnings(){
	$("#cg_init_word").removeClass("has-error");
	$("#cg_init_word").removeClass("has-success");
	$("#hb_init_word").text("");
	$("#cg_replace_word").removeClass("has-error");
	$("#cg_replace_word").removeClass("has-success");
	$("#hb_replace_word").text("");

}

function reset_dlg_fields(){
	$("#init_word").val("");
	$("#replace_word").val("");
}

function add_new_record(){
	var init_word = $( "#init_word" ).val();
	var replace_word = $( "#replace_word" ).val();
	var posting = $.post( "/rnr/add_dict_record", {
		ajax: "true",
		"init_word": init_word,
		"replace_word": replace_word,
	},"json");
	// Put the results in a div
	posting.done(function( data ) {
		if (data.success == true){
			reset_dlg_fields();
			reset_dlg_warnings();
			$("#dlg_add_record").modal('hide');
			$("#records_table").bootstrapTable('refresh');
		}
		else{
			reset_dlg_warnings();
			
			if (data.errors.init_word){
				$("#cg_init_word").removeClass("has-success");
				$("#cg_init_word").addClass("has-error");
				$("#hb_init_word").text(data.errors.init_word);
			}
			if (data.errors.replace_word){
				$("#cg_replace_word").removeClass("has-success");
				$("#cg_replace_word").addClass("has-error");
				$("#hb_replace_word").text(data.errors.replace_word);
			}
		};
	});
};


function del_dict_record(){
	var posting = $.post( "/rnr/del_dict_record", {
		ajax: "true",
		"slug": selected_record_slug,
	},"json");
	
	posting.done(function(data){
		if (data.success == true){
			$("#records_table").bootstrapTable('refresh');
		
			}
		else {
			alert("del error");
		};
		
		
	});
	
	
	
}


$(document).ready(function(){
	init_RecordMenu();
	//$("#records_table").on("contextmenu", "td", function(e) {
	//	alert($(this).parent().children("td:first").text());
				//$("#dlg_add_MW").modal("show");
	//	});
	
	$( "#create_record" ).click(function() {
		add_new_record();
		});
			
	});