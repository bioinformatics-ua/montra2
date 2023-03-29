$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();

	$('.dropdown-toggle').dropdown();
	function getCookie(name){
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (i = 0; i < cookies.length; i++){
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
	var csrftoken = getCookie('csrftoken');
	window.datasourcepath = ENDPOINTS.datasource;

	$('.storeDSForm').submit(function(e){
		console.log('submit');
		e.preventDefault();
		return false;
	});

    function progress(e){

        if(e.lengthComputable){
            var max = e.total;
            var current = e.loaded;

            var Percentage = (current * 100)/max;
            $('.zipIndicator').text(Percentage+' %');
            $('.zipBar').css('width', Percentage+'%');

        }
     }

	$('.submitButton').click(function(event){
        $('.submitButton').attr('disabled', true);
        $('.zipProgress').show();
        $('.zipBar').css('width', '0%');
        $('.zipIndicator').text('0 %');

		var formData = new FormData();
		formData.append("ds_zip", $("#ds_zip")[0].files[0]);
		formData.append("ds_url", $("#ds_url")[0].value);

		$('.storeDSForm');
		var url = BASE_URL + $('.storeDSForm').attr("action");
		//$.each($('#storeDSForm').prototype.fileData, function(i, obj) { formData.append(i, obj.value.files[0]); });
        formData.append('action', 'upload');
        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            xhr: function() {
                    var myXhr = $.ajaxSettings.xhr();
                    if(myXhr.upload){
                        myXhr.upload.addEventListener('progress',progress, false);
                    }
                    return myXhr;
            },
            headers: { "X-CSRFToken":  csrftoken },
            enctype: 'multipart/form-data',
            processData: false,  // tell jQuery not to process the data
            contentType: false,   // tell jQuery not to set contentType
            mimeType: 'multipart/form-data'
            }).done( function(data) {
                console.log('done: ');
				console.log(data);
				setTimeout(function(){location.reload(true);}, 2000);
                $('.submitButton').removeAttr('disabled');
                $('.zipProgress').hide();


	           // $('#changeDatasourceModal').modal('hide');
            }).fail(function (data){
                console.log('fail: ');
                console.log(data);
                $('.submitButton').removeAttr('disabled');
                ('.zipProgress').hide();

            });

		}
	);
});

