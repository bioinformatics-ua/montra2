$(function(){
    //$('#topnavigator').affix();
    //$('#summarynav').affix();
    $('.docmenu').affix({
    offset: {
      top: $('.docmenu').offset().top
    }
  });
})
