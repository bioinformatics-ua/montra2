
$(function(){

    $('#community-users').dataTable(
    {
        "pagingType": "simple",
        "oLanguage": { "sEmptyTable": "<center>No community users found</center>" },
        "aoColumnDefs" : [ { 'bSortable' : false, 'aTargets' : [1] } ],
        "order": [[ 0, "asc" ]],
    });

    $('#new-users').dataTable(
    {
        "pagingType": "simple",
        "oLanguage": { "sEmptyTable": "<center>No users waiting approval found</center>" },
        "aoColumnDefs" : [ { 'bSortable' : false, 'aTargets' : [1] } ],
        "order": [[ 4, "desc" ]],
    });

});
