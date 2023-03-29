import { Controller } from "stimulus"

export default class extends Controller {

    /*====================================*/
    /*  Lifecycle methods                 */
    /*====================================*/

    connect() {
        this._initPaginator();
    }

    /*====================================*/
    /*  Private methods                   */
    /*====================================*/

    _initPaginator(){
        var rows = $("#paginator_rows").val();
        $("#page_rows").val(rows);
    
        $("#paginator_rows").change(function(){
            $("#page_rows").val($(this).val());
            $("#send2").submit();
        });
    
        $("a", ".pagination").each(function() {
            $(this).click(function(e) {
  
                console.log("a click!")
                var parent = $(this).parent("li");
                if(parent.hasClass("active") || parent.hasClass("disabled")){
                    e.preventDefault();
                    return false;
                }
    
                var href = $(this).attr("href");
                var patt = /\/(\d+)/g;
                var page = patt.exec(href);
  
                console.log(page)
                if (page) {
                    page = page[1];
                    var form = $("#send2");
                    $("#page", form).val(page);
    
                    console.log('submit form!')
                    form.submit();
                } else {
                    page = "NULL";
                }
                e.preventDefault();
            });
    
        });
    }
  
    _updateFormPaginatorFilter(e) {
      var filterQuery = {};
      //build filter query
      this._buildFilter(filterQuery)
      //convert to string
      var filterQueryStr = JSON.stringify(filterQuery);
    }

    _getFilterString() {
        var filterController = this.application.getControllerForElementAndIdentifier(this, "community-fingerprint-listing")
        getFilterQuery
    }
}