/*
 * delayKeyup
 * http://code.azerti.net/javascript/jquery/delaykeyup.htm
 * Inspired by CMS in this post : http://stackoverflow.com/questions/1909441/jquery-keyup-delay
 * Written by Gaten
 * Exemple : $("#input").delayKeyup(function(){ alert("5 secondes passed from the last event keyup."); }, 5000);
 */

(function($) {
    $.fn.delayKeyup = function(callback, ms) {
        var timer = 0;
        $(this).keyup(function() {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        });
        return $(this);
    };
})(jQuery);

function PaginatorSorter(tableID, fString, selName, selValue, xtraData, allFields) {
    
    this.innerTable = $("#" + tableID);

    this.filters = [];
    this.filters.push("database_name_filter"); // = $("#database_name_filter",this.innerTable);
    this.filters.push("last_update_filter"); // = $("#last_update_filter",this.innerTable);
    this.filters.push("type_filter"); // = $("#type_filter",this.innerTable);
    this.filters.push("institution_filter"); // = $("#type_filter",this.innerTable);
    this.filters.push("location_filter"); // = $("#type_filter",this.innerTable);
    this.filters.push("nrpatients_filter"); // = $("#type_filter",this.innerTable);

    for(var i =0;i<allFields.length;i++){
        this.filters.push(allFields[i]+'_filter');
    }

    this.selName = selName;
    this.selValue = selValue;
    if (xtraData != undefined) {
        try {
            this.extraData = $.parseJSON(xtraData);
        } catch (err) {
            console.log(err);
        }
    }
    this.plugin = undefined;

    this.bind();

    this.form = $("#send2");
    this.updateForm(this.getQueryString(selName, selValue));
    this.fString = fString;
}
PaginatorSorter.prototype = {
    atachPlugin: function(plg) {
        this.plugin = plg;
        plg.setData(this.extraData);

    },
    getQueryString: function(fieldType, value) {
        var json = "{";

        if (fieldType == undefined){
            json += '"' + this.selName + '": "' + this.selValue + '"';
        }
        else{
            json += '"' + fieldType + '": "' + value + '"';
        }   
            

        //console.log(json);
        for (var i = 0; i < this.filters.length; i++) { // in this.filters){
            try {
                var content = $("#" + this.filters[i], this.innerTable);
                json += ',"' + this.filters[i] + '": "' + encodeURI(content.val()) + '"';
            } catch (err) {
                console.log("Found filter that doesnt exist, ignoring.");
            }

        }

        if (this.plugin != undefined) {
            var x = this.plugin.getExtraObjects();
            if (x != undefined)
                json += ', "extraObjects":' + JSON.stringify(x);
        }

        json += "}";
        //console.log(json);
        return json;
    },
    onClick: function(fieldType, value) {

        var context = this;
        var data = [];

        //filter query
        var json = context.getQueryString(fieldType, value);
        console.log(json)

        var patt = /\/(\d+)/g;
        var page = patt.exec(window.location.href);
        if (page) {
            page = page[1];
        } else {
            page = 1;
        }

        var f = this.fString;

        var community = $('#communityindicator').val();

        if(community.length > 0)
            community = 'c/'+community+'/';

        $.ajax({
            type: "POST",
            dataType: "json",
            url: community+"query/" + page,
            data: {
                'csrfmiddlewaretoken': $.cookie('csrftoken'),
                "filter": f,
                "s": json
            },
            success: function(data) {
                //console.log(data);
                if (data.Hits != undefined && data.Hits > 0) {
                    context.selName = fieldType;
                    context.selValue = value;

                    //context.updateForm(json);

                    /*for(filter in context.filters){
						if(context.filters[filter].val().length > 0 ){
							var x = $("#"+filter+"_grp");
							x.removeClass("error");
						}
					}*/
                    console.log('SUCCESS');
                    context.submitthis();
                } else {
                    $("#table_content").html('<td colspan="9999"><center>No results to show</center></td>');
                    $(".pagination, .pagination-centered").html('');
                    //console.log('NOTSUCCESS');
                    /*
  					for(filter in context.filters){
						if(context.filters[filter].val().length > 0 ){
							var x = $("#"+filter+"_grp");
							x.removeClass("success");
            				x.addClass("error");
						}
					}
					*/

                }
            }
        });
    },
    bind: function() {

        var value = $("#type_filter", this.innerTable).attr("def_value");
        $("option[value=" + value + "]", $("#type_filter", this.innerTable)).attr("selected", "yes");

        var context = this;

        var funct_handler = function() {
            if (context.plugin != undefined) {
                context.plugin.clearSelection();
            }
            // Save focus so we can return it after post request
            if(supports_html5_storage()){
                localStorage.setItem('listing_focus', $(':focus').attr('id'));

                console.log($(':focus').attr('id'));
            }

            context.onClick(context.selName, context.selValue);
        };

        var timeout = 1000;

        var remove_focus = function(){
            if(supports_html5_storage()){
                localStorage.removeItem('listing_focus');
            }
        };

        for(var i=0;i<this.filters.length;i++){
            try {
                $("#"+this.filters[i], this.innerTable).delayKeyup(funct_handler, timeout);
                $("#"+this.filters[i], this.innerTable).blur(remove_focus);
            }
            catch(err) {
                console.error(err)
            }
        }

        $("#send2").submit(function() {
            context.updateForm();
        });

        var focus_saved = localStorage.getItem('listing_focus');

        if(focus_saved){
            var focus_saved = $('#'+focus_saved);
            if(focus_saved.length !== 0){
                focus_saved.focus();
                focus_saved.val(focus_saved.val());
            }
        }
    },
    updateForm: function(json) {
        //console.log("Setting Value!!!");
        //console.log(json);
        if (json == undefined)
            json = this.getQueryString();

        $("#s", $("#send2")).val(json);
    },
    submitthis: function() {

        //this.form.submit();
        //$("#send2").submit();
        $("#send2").trigger('submit');
        //$("#submit_simulate").click();

    }
}

//This plugin handles the select boxes for the SearchResultsPage
function SelectPaginatorPlugin() {
    this.selectedList = undefined;
    this.typedb = undefined;
}
SelectPaginatorPlugin.prototype = {
    getExtraObjects: function() {
        const self = this;
        let list;
        if (this.selectedList !== undefined) {
            const previous_selected = new Set(this.selectedList);

            $("input.chkbox[name^=chk_]").each(function(_, element) {
                const name = element.name.substring(4);

                if (element.checked) {
                    previous_selected.add(name);
                    self.typedb = element.typedb;
                }
                else {
                    previous_selected.delete(name);
                }
            });

            list = [...previous_selected];
        }
        else {
            list = [...$.map($("input.chkbox[name^=chk_]:checked"), (element, _) => element.name.substring(4))];
        }

        if (list.length > 0){
            if(self.typedb)
                return {
                    selectedList: list,
                    typedb: self.typedb
                };

            //else
            return {
                selectedList: list
            };
        }

        return undefined;
    },
    setData: function(data) {
        if (data !== undefined && data.selectedList !== undefined) {
            this.selectedList = data.selectedList;
            this.typedb = data.typedb;

            this.populateBoxes();
        }
    },
    populateBoxes: function() {
        if (this.selectedList !== undefined) {
            for (const db of this.selectedList) {
                const checkbox = $(`input.chkbox[name=chk_${db}]`);
                if (!checkbox.is(":checked")) {  // dont click on already checked boxes
                    checkbox.click();
                }
            }
        }
        if (this.typedb !== undefined) {
            $('input.chkbox:not([typedb="' + this.typedb + '"])').prop('disabled', true);
        }
    },
    clearSelection: function() {
        this.selectedList = [];
        this.populateBoxes();
        this.typedb = undefined;

        $("input.chkbox[name^=chk_]:checked").click();
    },
    onFiltering: function() {
        this.clearSelection();
    }
}

function paginator_via_post() {
    var rows = $("#paginator_rows").val();
    //console.log("Rows: "+rows);
    $("#page_rows").val(rows);

    $("#paginator_rows").change(function(){
        $("#page_rows").val($(this).val());
        $("#send2").submit();
    });

    $("a", ".pagination").each(function() {
        $(this).click(function(e) {
            var parent = $(this).parent("li");
            if(parent.hasClass("active") || parent.hasClass("disabled")){
                e.preventDefault();
                return false;
            }

            var href = $(this).attr("href");
            var patt = /\/(\d+)/g;
            var page = patt.exec(href);
            if (page) {
                page = page[1];
                var form = $("#send2");
                $("#page", form).val(page);

                form.submit();
            } else {
                page = "NULL";
            }
            e.preventDefault();
        });

    });
}
function supports_html5_storage() {
  try {
    return 'localStorage' in window && window['localStorage'] !== null;
  } catch (e) {
    return false;
  }
}
