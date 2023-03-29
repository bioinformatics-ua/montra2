	var page_vm =  {};
	var report = 'dashboard';

	function Achilles(datasourceURL, containerName , urlDom, callback){
		this.datasource = datasourceURL;
		achilles_load = bootbox.dialog({
			message: '<h3>Loading, please wait.</h3>'}
			);

		$.ajax(urlDom).done(function(data){
			$(containerName).append(data);
			callback();
		});

	}

	function updateReport(value) {
		report = value;
		updateRoute();
	}

	function setDatasource(index) {
		page_vm.datasource(page_vm.datasources[index]);
		updateRoute();
	}
	var achilles_load;
	function updateRoute() {
		achilles_load = bootbox.dialog({
			message: '<center><h3>Loading, please wait.</h3></center>'}
			);
		$('.reportDrilldown').addClass('hidden');
		document.location = '#/' + page_vm.datasource().name + '/' + report;
	}


