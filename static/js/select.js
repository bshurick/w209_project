
$(document).ready(function() {
	$('#survey_btn').hide();
	$('#video_box').click(function() { 
		if ($(this).prop('checked')==true) {
			$('#survey_btn').show();	
		} else if ($(this).prop('checked')==false) {
			$('#survey_btn').hide();	
		} 
	});
	$('#q1').show();
        $('#q2').hide();
        $('#q3').hide();
        $('#q4').hide();
        $('#q5').hide();
	$('#q1_select').click(function() {
		$('#q1').show();	
		$('#q2').hide();	
		$('#q3').hide();	
		$('#q4').hide();	
		$('#q5').hide();	
	});
	$('#q2_select').click(function() {
		$('#q1').hide();	
		$('#q2').show();	
		$('#q3').hide();	
		$('#q4').hide();	
		$('#q5').hide();	
	});
	$('#q3_select').click(function() {
		$('#q1').hide();	
		$('#q2').hide();	
		$('#q3').show();	
		$('#q4').hide();	
		$('#q5').hide();	
	});
	$('#q4_select').click(function() {
		$('#q1').hide();	
		$('#q2').hide();	
		$('#q3').hide();	
		$('#q4').show();	
		$('#q5').hide();	
	});
	$('#q5_select').click(function() {
		$('#q1').hide();	
		$('#q2').hide();	
		$('#q3').hide();	
		$('#q4').hide();	
		$('#q5').show();	
	});
});
