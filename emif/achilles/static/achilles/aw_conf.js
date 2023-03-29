confs = {
    extralibs: [
        "{% static 'js/vendor/iframeResizer.js' %}"
    ],
    name: 'Suitability A',
    icon : '<i class="fas fa-fw fa-pie-chart"></i>'
};

hasContent = function(sdk){
    var fp = FingerprintProxy.getInstance();
    var store = fp.getStore();
    return [];
};

plugin = function(sdk){
FingerprintProxy.getInstance().getFingerprintUID().then(function(data){
        console.log("Starting")
        sdk.html('<iframe id="achillesIframe" style="width: 100%; min-height: 500px; border:0;" src="achilles/home?fingerprint_id='+data.fingerprint.fingerprint_hash+'&plugin_id='+globalPluginsIds['Suitability A']+'"></iframe>');
		sdk.refresh();

		$("#achillesIframe").iFrameResize({
		        log: false
		     });
	});
};
