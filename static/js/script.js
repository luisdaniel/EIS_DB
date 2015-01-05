$(document).ready(function() {

	$(function() {
    	$( "#filter-date-range-from" ).datepicker();
	});

	$(function() {
    	$( "#filter-date-range-to" ).datepicker();
	});

	$('#report-table').dataTable({
        "paging":   false,
        "info":     false,
        "filter": 	false
    });

    $('.report-filters').on('click', '#clear-filters', function() {
        window.location.replace("/");
    });
    console.log($(".filter-arrow").text())
    $('#accordion').find('.accordion-toggle').click(function(){

      //Expand or collapse this panel
      $(this).next().slideToggle('fast');
      if ($('.filter-arrow').text() == '▶') {
        $('.filter-arrow').text('▼');
      } else {
        $('.filter-arrow').text('▶');
      }
    });

});