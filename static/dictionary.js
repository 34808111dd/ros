		function init_ClientMenu(){
			//init client menu
				var $ClientMenu = $("#ClientMenu");
				$ClientMenu.hide();
								
				$("#cl_table").on("contextmenu", "td", function(e) {
					$ClientMenu.css({left: e.pageX, top: e.pageY, display:"block", position:"absolute"});
				  });
				$ClientMenu.on("click", "li", function() {
					  if ($(this).index()===0){
						  alert(0);
					  }
					  else if ($(this).index()===1){
						alert(1);
					  }
					  $ClientMenu.hide();
				  });
				
				$(document).click(function(){
					$ClientMenu.hide();
				});
			};
			
			
$(document).ready(function(){
init_ClientMenu();
});