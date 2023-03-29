$(function(){
    $('#create_community').submit(function(event){
        event.preventDefault();
        event.stopPropagation();

        var button = $('#community-create-button');

        button.attr('disabled', true);

        var name = $('#name').val();
        var description = $('#description').val();
        var slug = $('#motivation').val();//.val().toLowerCase().replace(/[^a-z0-9]+/g, '');

        if(name.length < 4 || name.length > 70){
            bootbox.alert('The community name must be filled, and have between 4 and 70 characters.');
            button.removeAttr('disabled');

        } else if(description.length < 30 || description.length > 300){
            bootbox.alert('The community description must be filled, and have between 30 and 300 characters.');
            button.removeAttr('disabled');
        } else if(slug.length < 30 || slug.length > 300){
            bootbox.alert('The community motivation must be filled, and have between 30 and 300 characters.');
            button.removeAttr('disabled');
        } else {
            event.target.submit();
            /*$.get('api/free_slug/'+slug, function(data) {
                button.removeAttr('disabled');
                if(!data.free){
                    bootbox.alert('The community slug '+slug+' is already in use, please choose another slug.');
                } else {
                    event.target.submit();
                }
            });*/
        }
    });
});
