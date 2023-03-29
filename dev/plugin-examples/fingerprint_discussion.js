confs = {
    icon: '<i class="fa fa-comment"></i>',
    name: "Discussion"
};
plugin = function(sdk) {
    sdk.html('Loading...');
    sdk.refresh();
    var context = sdk.container();
    var getComment = function(comment, can_moderate) {
        return '<div class="comment" id="comment_' + comment.id + '">\
            <blockquote>\
                <p style="font-size: 16px">' + comment.comment + '</p>\
                <small>' + comment['user_name'] + ' posted on ' + comment['submit_date'] + '</small>\
            </blockquote>' +
            (can_moderate ? '<button id="delete_comment_' + comment.id + '" class="btn btn-danger delete-button">Delete</button>' : '') +
        '</div>';
    };
    var base = function(data, can_moderate) {
        var tmp = '<div class="col-md-8 col-md-offset-2">';
        if (data.length == 0) {
            tmp += '<center><p>No comments yet.</p></center>';
        } else {
            tmp += '<center><span class="comments_total">' + data.length + '</span> comments</center>';
        }

        tmp += '<div class="clearfix col-md-12 comment_form">\
                    <fieldset>\
                        <textarea rows="5" name="comment" class="form-control id_comment col-md-12" placeholder="Insert your comment or question here..." autofocus></textarea>\
                        <button style="margin-left:0px;" class="submit_button col-md-12 btn btn-primary" type="submit"  data-loading-text="Sending comment...">Post comment</button>\
                    </fieldset>\
                </div>';

        tmp += '<div style="margin-top:10px" class="clearfix col-md-12"><div class="newComments"></div>';

        for (var i = 0; i < data.length; i++) {
            tmp += getComment(data[i], can_moderate);
        }

        tmp += '</div></div>';

        return tmp;
    };

    var fp = FingerprintProxy.getInstance();
    var store = fp.getStore();

    store.getComments().then(function(response) {
        sdk.html(base(response.comments, response.can_moderate));
        sdk.refresh();
        $('.submit_button', context).click(function() {
            var comment = $('.id_comment', context).val();

            if (comment && comment.trim().length > 20) {
                store.putComment({
                    comment: comment
                }).then(function(response) {
                    console.log(response);
                    console.log(getComment(response.comment, response.can_moderate));
                    $('.newComments', context).append(getComment(response.comment, response.can_moderate));
                }).catch(function(ex){
                    bootbox.alert("Unable to add new comment, please try again.");
                });
            } else {
                bootbox.alert("A comment must have more then 20 characters.");
            }

        });
        $('.delete-button', context).click(function(e) {
            var split = e.target.id.split('_');
            var id = split[split.length - 1];
            $('#comment_' + id).hide();
            $.ajax({
                url: '/developer/api/store/deleteComment/' + global_fingerprint_id + '/' + id,
                type: 'DELETE',
            });
        });
    });
};
