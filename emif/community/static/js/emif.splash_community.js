$(function(){

    $('.community-lock').tooltip({
        container: 'body',
        placement: 'left',
    });

    var desc = $('.desc_clicker');
    
    desc.click(function(){
        var status = parseInt($(this).data('status'));
        var cont = $(this).parent().parent().parent().find('.desc_container');
        var shower = $(this).parent().parent().parent().find('.desc_shower');

        if(status == 0){
            $(this).data('status', '1');
            $(this).text('Less');
            cont.css("height", 'auto');
            shower.css({
                "background-image": "none"
            });

        } else {
            $(this).data('status', '0');
            $(this).text('More');
            cont.css("height", "220px");
            shower.css({
                "background-image": "linear-gradient(to bottom, transparent, white)"
            });
        }

    });


});

function changeToHeader(name, element){
    elemParent = element.parentElement;
    elemParent.innerHTML = " <h3 class='no-margn'><strong>"+name+"</strong></h3>"
}

function favouriteCheckBoxChange(checkbox, community_slug){
    if (checkbox.checked){
        $.get('community/favorite/'+community_slug).done(function(data){
            if(data.success)
                location.reload();
            else
                bootbox.alert('It was not possible at the moment to favorite this community, if the problem persists, please contact the administrator.');
        }).fail(function(data){
            bootbox.alert('It was not possible at the moment to favorite this community, if the problem persists, please contact the administrator.');

        });
        return false;
    } else {
        $.get('community/unfavorite/'+community_slug).done(function(data){
            if(data.success)
                location.reload();
            else
                bootbox.alert('It was not possible at the moment to unfavorite this community, if the problem persists, please contact the administrator.');
        }).fail(function(data){
            bootbox.alert('It was not possible at the moment to unfavorite this community, if the problem persists, please contact the administrator.');
    
        });
        return false;
    }
}

function addToWS(community_slug, community_name){
    var the_dialog = bootbox.dialog({title: 'Favourite '+community_name+'?', message:'Are you sure you want to add the community '+community_name+' to your Workspace?<br /><br />',
        buttons: {
            leaveCommunity: {
                label: 'Favourite Community',
                className: 'btn-default',
                callback: function() {
                    $.get('community/favorite/'+community_slug).done(function(data){
                        if(data.success)
                            location.reload();
                        else
                            bootbox.alert('It was not possible at the moment to favorite this community, if the problem persists, please contact the administrator.');
                    }).fail(function(data){
                        bootbox.alert('It was not possible at the moment to favorite this community, if the problem persists, please contact the administrator.');

                    });
                    return false;

                }
            },
            cancelCommunity: {
                label: 'Cancel',
                className: 'btn-primary',
                callback: function(){
                        the_dialog.modal('hide');
                }
            }
        }
        });
    
}

function removeFromWS(community_slug, community_name){
    var the_dialog = bootbox.dialog({title: 'Leave '+community_name+'?', message:'Are you sure you want to unfavourite the community '+community_name+'?<br /><br />\
        After unfavouriting the community, it will disappear from your workspace\
        ',
        buttons: {
            leaveCommunity: {
                label: 'Unfavourite Community',
                className: 'btn-default',
                callback: function() {
                    $.get('community/unfavorite/'+community_slug).done(function(data){
                        if(data.success)
                            location.reload();
                        else
                            bootbox.alert('It was not possible at the moment to unfavorite this community, if the problem persists, please contact the administrator.');
                    }).fail(function(data){
                        bootbox.alert('It was not possible at the moment to unfavorite this community, if the problem persists, please contact the administrator.');
                
                    });
                    return false;

                }
            },
            cancelCommunity: {
                label: 'Cancel',
                className: 'btn-primary',
                callback: function(){
                        the_dialog.modal('hide');
                }
            }
        }
        });
   
}

function leaveCommunity(community_slug, community_name){
    var the_dialog = bootbox.dialog({title: 'Leave '+community_name+'?', message:'Are you sure you want to leave the community '+community_name+'?<br /><br />\
        After leaving the community, you will have to be approved again by the community responsibles if you ever wish to return\
        to this community.\
        ',
        buttons: {
            leaveCommunity: {
                label: 'Leave Community',
                className: 'btn-default',
                callback: function() {
                    console.log('LEAVE COMMUNITY '+community_slug);

                    $.get('community/leave/'+community_slug).done(function(data){
                        if(data.success)
                            location.reload();
                        else
                            bootbox.alert('It was not possible at the moment to leave this community, if the problem persists, please contact the administrator.');
                    }).fail(function(data){
                        bootbox.alert('It was not possible at the moment to leave this community, if the problem persists, please contact the administrator.');

                    });
                    return false;
                }
            },
            cancelCommunity: {
                label: 'Cancel',
                className: 'btn-primary',
                callback: function(){
                        the_dialog.modal('hide');
                }
            }
        }
        });
}

$(document).bind('keydown', 'esc', function(){
    $('.bootbox').modal('hide');
});
