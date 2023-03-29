confs = {
    extralibs: [
        "{% static 'js/vendor/iframeResizer.js' %}"
    ],
    name: 'Suitability J'
};

plugin = function(sdk){

    FingerprintProxy.getInstance().getFingerprintUID().then(function(data){
        console.log("Starting SuitabilityJ ")
        var extra = '';

        if(typeof(global_public_key) != 'undefined' && global_public_key.length > 0)
            extra='&publickey='+global_public_key;
        
        community_slug=data.community
        sdk.html('<iframe id="SuitabilityJIframe" style="width: 100%; min-height: 1350px; max-height: 2000px; border:0;" src="c/'+community_slug+'/fingerprint/'+(data.fingerprint.fingerprint_hash)+'/jerboa/'+globalPluginsIds['Suitability J']+'"></iframe>');
src="c/'+community_slug+'/fingerprint/'+(data.fingerprint.fingerprint_hash)+'/jerboa/'+globalPluginsIds['Suitability J']+'"
        sdk.refresh();

        $("#SuitabilityJIframe").iFrameResize({
                log: false
             });
    });
};