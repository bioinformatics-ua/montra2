function requestFile(filename, revision){
    $.post( "api/getcommunityfile", { filename: filename, revision: revision, security:false })
      .done(function(result) {
        console.log(result);
      })
      .fail(function() {
        console.log( "error getting file" );
      });


    var df = $('#downloadfile');
    $('[name="filename"]').val(filename);
    $('[name="revision"]').val(revision);
    df.submit();


}

function check_checked(community_slug, user){



   var title = document.getElementById("title").value;
   var deadline = document.getElementById("deadline").value;
   var question = document.getElementById("question").value;
   var position = document.getElementById("user_position").value;

if (title =="" || deadline =="" || question ==""){

    document.getElementById('submitForm').onsubmit= function(e){
     e.preventDefault();
}
return false
}

else{
    var type=[];
    $("input[name='chkname']:checked").each(function (i) {
                type[i] = $(this).val();
            });

   


   $.post( "studies/create_study/",
        {  
         database_names: JSON.stringify( type ),
         title: title,
         deadline: deadline,
         question: question,
         user_position: position,
         community_slug:community_slug,
         user:user,
        })

        
        
        .done(function( data ) {
        if(data.result == 1){ // meaning that everyhting went ok
                window.location.replace(data.url);
             }
             else{
                window.location.replace(data.url);
             }
         });

}
}

function checkAll(ele) {
     var checkboxes = document.getElementsByName('chkname');
     if (ele.checked) {
         for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].type == 'checkbox') {
                 checkboxes[i].checked = true;
             }
         }
     } else {
         for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].type == 'checkbox') {
                 checkboxes[i].checked = false;
             }
         }
     }
 }

function update_study_status(community_slug, study_id ){

study_status = $( "#study_status" ).val();

 $.post( "studies/update_study_status/",
        {   community_slug: community_slug,
            study_id: study_id,
            study_status: study_status,
        })
        
         .done(function( data ) {
        if(data.result == 1){ // meaning that everyhting went ok
                window.location.replace(data.url);
             }
             else{
                window.location.replace(data.url);
             }
  });

}


function showPopupRejection(){


    if (confirm("Are you sure you want to reject this request?") == true) {
        $("#popup_rejection").dialog();
        //$( "#"+popup_id ).dialog("option", "width", $(window).width()*0.6);
        $( "#popup_rejection").dialog("option", "title", "Please provide a short explanation for the rejection of this request.");
       
         

        

      /*   $.post( "studies/reject_study/"+ comm_slug + "/" + study_id + "/",
        { }); */ 

    } 
}





function showConfirmationPopup(comm_slug,study_id){


    if (confirm("Are you sure you want to reject this request?") == true) {

        var popup_id = study_id;
        $("#"+popup_id).dialog();
        //$( "#"+popup_id ).dialog("option", "width", $(window).width()*0.6);
        $( "#"+popup_id).dialog("option", "title", "Please provide a short explanation for the rejection of this request.");
       
         

        

      /*   $.post( "studies/reject_study/"+ comm_slug + "/" + study_id + "/",
        { }); */ 

    } 
}


function deleteConfirmationPopup(comm_slug,study_id){


    if (confirm("Are you sure you want to delete this request?") == true) 
    {    

         $.post( "studies/delete_study/"+ comm_slug + "/" + study_id + "/",
        { })

        .done(function( data ) {
        if(data.result == 1){ // meaning that everyhting went ok
                window.location.replace(data.url);
             }
             else{
                window.location.replace(data.url);
             }
  });

    
    } 
}





function displayPopupNewStudy(disabled) {

    $( "#newStudyPopup" ).dialog();
    $( "#newStudyPopup" ).dialog("option", "width", $(window).width()*0.6);
    $( "#newStudyPopup" ).dialog("option", "title", "Create New Study");

    /*$( "#newStudyPopup" ).dialog({
modal: true,
open: function (event, ui) {
 $('.ui-dialog').css('z-index',1003);
 $('.ui-widget-overlay').css('z-index',1002);
},
});*/
    

    $('#deadline').datepicker({dateFormat: "yy-mm-dd", minDate: 0});

    if (disabled){
         $("#newStudyPopup").find("*").prop('disabled', true);
    }

    $('#newStudyPopup').on('dialogclose', function(event) {
      /*  $("#newStudyPopup").find('input:text').val('');
       
        $("#newStudyPopup").find("*").prop('disabled', false); */

    document.getElementById("title").value = "";
    document.getElementById("deadline").value = "";
    document.getElementById("user_position").value ="";
    document.getElementById("question").value = "";

   var checkboxes = document.getElementsByName('chkname');
         for (var i = 0; i < checkboxes.length; i++) {
                 checkboxes[i].checked = false;
         }

 });
}

function closePopup()
{


    $( "#newStudyPopup" ).dialog('close');

    return false

}

function closeFeedbackPopup()
{


    $( "#popup_rejection" ).display.style="none";

    return false

}



function quitBox(cmd)
{   
    if (cmd=='quit')
    {
        open(location, '_self').close();
    }   
    return false;   
}

