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

});