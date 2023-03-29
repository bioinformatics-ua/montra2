import { Controller } from "stimulus"

/**
 * Auxiliary function to show/hide Filters/OrderBy container
 */
function _triggerFilter($bool) {
  const elementsToTrigger = $([$('.cd-filter-trigger'), $('#cd-filter'), $('.cd-tab-filter'), $('.cd-gallery')]);
  elementsToTrigger.each(function(){
    $(this).toggleClass('filter-is-visible', $bool);
  });
}

/**
 * Handler to close the Filters/OrderBy container whenever the user clicks outside it
 */
function _close_on_click_outside(event) {
  const filters_sort_container = document.getElementById("cd-filter");
  if (!filters_sort_container.contains(event.target)) {
    _triggerFilter(false);
    document.removeEventListener("mousedown", _close_on_click_outside);
  }
}

export default class extends Controller {
  static targets = [
              "paginator", 
              "filter", 
              "activefilter", 
              "activesorter", 
              "clearFiltersOutside",
              "clearFiltersInside",
              "applyFilter",
              "min",
              "max", 
              "sorterSlug", 
              "sorterAscValue", 
              "sorterDescValue",
              "cdForm",

              "selectedDatabasesIndicator",
              "selectedDatabasesContainer",
              "selectedUnselectAll",
              "clearSelection",

              "pageRowsForm",
              "searchForm",
              "sForm",
              "dataViewForm",
              "pageForm"
            ]

  #default_sort_slug = "database_name";
  #default_sort_order_asc = true;

  /*====================================*/
  /*  Lifecycle methods                 */
  /*====================================*/

  connect() {
    this._initPaginator()

    if (
        this.sorterSlugTarget.value === this.#default_sort_slug &&
        this.sorterAscValueTarget.checked === this.#default_sort_order_asc &&
        this.activefilterTargets.length === 0
    ) {
      // if the default sorting is selected and there are no filters, hide the clear all button
      this.clearFiltersOutsideTarget.style.display = "none";
      this.clearFiltersInsideTarget.style.display = "none";

      // make the apply button take more space on the cd-fitter container
      this.applyFilterTarget.style.width = "100%";
    }
    else {
      this.clearFiltersOutsideTarget.style.display = "";
      this.clearFiltersInsideTarget.style.display = "";
    }

    this._updateSelectUnselectAllText();
  }

  /*====================================*/
  /*  Public methods                    */
  /*====================================*/

  onSelectUnselectAll() {
    const checked = $("input.chkbox[name^=chk_]:checked");
    if (checked.length < $("input.chkbox[name^=chk_]").length) {  // if some databases are not selected
      $("input.chkbox[name^=chk_]:not(:checked)").click()  // click on the non-selected ones
    }
    else {
      checked.click()  // click on the selected ones == all
    }
  }

  /**
   * Handler for clicks on table headers which should affect sorting
   * @param e event
   */
  onSwitchOrder(e) {
    const element = e.currentTarget;
    this.sorterSlugTarget.value = element.dataset.sortslug;
    this.sorterAscValueTarget.checked = element.dataset.sortorder === "asc";
    this.onFilter(undefined, true);
  }

  /**
   * Handler to open Filters/OrderBy container
   */
  onFilterShow() {
    _triggerFilter(true);
    document.addEventListener("mousedown", _close_on_click_outside);
  }

  /**
   * Handler to close Filters/OrderBy container
   */
  onFilterClose (){
    _triggerFilter(false);
    document.removeEventListener("mousedown", _close_on_click_outside);
  }

  onFilter(event, reset_form=false) {
    _triggerFilter(false);
    const iPageRows = this.pageRowsFormTarget.value
    const sSearch= this._getFilterQuery(reset_form);
    const iPage = 1;
    const sView = this.data.get('view');
    this._submitSearchForm(sSearch, iPage, sView, iPageRows);
  }

  onRemoveFilter(e) {
    const element = e.currentTarget;
    const slug = element.dataset.filterslug;

    this.cdFormTarget.reset();  // reset the form to its initial values before _removeFilter makes changes

    if(this._removeFilter(slug))
      this.onFilter()
  }

  onRemoveSorter(e) {
    this.cdFormTarget.reset();  // reste the form to its initial values before the next to changes

    this.sorterSlugTarget.value = this.#default_sort_slug;
    this.sorterAscValueTarget.checked = this.#default_sort_order_asc;

    this._hideActive(e.currentTarget);

    this.onFilter();
  }

  onRemoveAll() {
    const that = this;
    
    //hide all active sorters badges
    this.sorterSlugTarget.value = this.#default_sort_slug;
    this.sorterAscValueTarget.checked = this.#default_sort_order_asc;
    this.activesorterTargets
        .filter(e => e.dataset.filterslug !== this.#default_sort_slug)
        .forEach(e => {
            const slug = e.dataset.filterslug;
            that._hideActive(slug);
        })

    //hide all active filters badges
    this.activefilterTargets.forEach(function(e, i){
      const slug = e.dataset.filterslug;
      that._removeFilter(slug)
    })
    
    this.onFilter()
  }

  onTableView (){
    this.data.set('view', 'table');
    this.onFilter(undefined, true);
  }

  onListView() {
    this.data.set('view', 'list');
    this.onFilter(undefined, true);
  }

  onCardView() {
    this.data.set('view', 'card');
    this.onFilter(undefined, true);
  }

  onSelectDatabase(e) {
    let db_count;
    try{
      db_count = a.plugin.getExtraObjects().selectedList.length;
    }catch(err){
      db_count = 0;
    }

    this.selectedDatabasesIndicatorTarget.textContent = db_count;

    // hide both "Selected databases" indicator and "Clear selection" link if no databases are selected
    if (db_count === 0) {
      this.selectedDatabasesContainerTarget.style.display = "none";
      this.clearSelectionTarget.style.display = "none";
    }
    else {
      this.selectedDatabasesContainerTarget.style.display = "";
      this.clearSelectionTarget.style.display = "";
    }

    this._updateSelectUnselectAllText();
  }

  _updateSelectUnselectAllText() {
    if ($("input.chkbox[name^=chk_]:checked").length < $("input.chkbox[name^=chk_]").length) {
      this.selectedUnselectAllTarget.textContent = "Select all"
    }
    else {
      this.selectedUnselectAllTarget.textContent = "Unselect all"
    }
  }

  onPaginatorChange(e) {
    const iPageRows = e.currentTarget.value
    const sSearch= this._getFilterQuery(true);
    const iPage = 1;
    const sView = this.data.get('view');
    this._submitSearchForm(sSearch, iPage, sView, iPageRows);
  }

  /*====================================*/
  /*  Private methods                   */
  /*====================================*/

  _removeFilter(slug) {
    const index = this.filterTargets.findIndex(function(el) {
      return el.dataset.slug === slug;
    });
    if(index != -1){
      this._hideActive(slug);
      
      const type = this.filterTargets[index].dataset.type

      //clear radio buttons status
      if(type == 'choice-yesno'){
        this.minTargets[index].checked = false  //yes
        this.maxTargets[index].checked = false  //no
      }

      this.minTargets[index].value = '';
      this.maxTargets[index].value = '';
    }else{
      console.error("Couldn't find the required filter!");
      return false
    }
    return true
  }

  _hideActive(slug) {
    const index = this.activefilterTargets.findIndex(function(el) {
      return el.dataset.filterslug === slug;
    });
    $(this.activefilterTargets[index]).hide();
  }

  _getActiveFilters(){
    return this.activefilterTargets;
  }

  _getActiveSorters() {
    return this.activesorterTargets;
  }

  
  _buildFilter(){
    //add questionnaire filter by default
    const filterQuery = {
      'type_filter': this.data.get("questionnaire_slug")
    };

    //add sorter
    const sorterSlug = this.sorterSlugTarget.value;
    if (sorterSlug) {
      filterQuery[sorterSlug] = this.sorterAscValueTarget.checked ? 'asc' : 'desc';
    }

    //iterate over all filter of filter panel
    this.filterTargets.forEach((el, i) => {
      const filter = {}
      filter.slug = el.dataset.slug;
      filter.type = el.dataset.type;
      if(filter.type == 'choice-yesno'){
        if(this.minTargets[i].checked  && !this.maxTargets[i].checked ){
          filter.min = 'yes'
          filter.max = ''
        }
        if(!this.minTargets[i].checked && this.maxTargets[i].checked ){
          filter.min = 'no'
          filter.max = ''
        }
      }else{
        filter.min = this.minTargets[i].value.replace(/@/i, ' ');
        filter.max = this.maxTargets[i].value.replace(/@/i, ' ');
      }

      //validate if filter is valid
      if(this._isValid(filter)){
        this._addQueryFilter(filterQuery, filter);
      }
    })

    filterQuery["extraObjects"] = a.plugin.getExtraObjects();

    return filterQuery
  }

  _addQueryFilter(filterQuery, filter){
    if ( filter.type === 'numeric' ){
      const num_filter = this._numericFilter(filter.min, filter.max)
      filterQuery[filter.slug + '_filter'] = [ num_filter.min, num_filter.max ];
    }else if ( filter.type === 'datepicker' ){
      const date_filter = this._dateFilter(filter.min, filter.max)
      filterQuery[filter.slug + '_filter'] = [ date_filter.min, date_filter.max ];
    }else{
      filterQuery[filter.slug + '_filter'] = filter.min;
    }
  }

  _numericFilter(min, max){
    max = max ? max : '*';
    min = min ? min : '*';
    return { 'min': min, 'max': max}
  }

  _dateFilter(min, max){
    max = max ? ( max + 'T23:59:59.999Z' ) : '*';
    min = min ? ( min + 'T00:00:00.000Z' ) : '*';
    return { 'min': min, 'max': max}
  }

  _isValid(filter) {
    let bValid = false;

    switch (filter.type){
      case 'numeric':
        bValid = ( filter.max && filter.max != '') || (filter.min && filter.min != ''  ) ? true : false;
        break;
      case 'datepicker':
        bValid = ( filter.max && filter.max != '') || ( filter.min && filter.min != '') ? true : false;
        break;
      default:
        bValid = filter.min && filter.min != '' ? true : false;
    }
    return bValid;
  }

  /**
   * @param reset_form  if the unapplied changes to the search form should be discarded
   * @returns {string} filter string to send to the backend
   * @private
   */
  _getFilterQuery(reset_form=false) {
    if (reset_form) {
      this.cdFormTarget.reset();
    }
    return JSON.stringify(this._buildFilter());
  }

  _submitSearchForm(sSearch, iPage, sView, iPageRows){
    
    this.pageFormTarget.value = iPage;
    this.sFormTarget.value = sSearch;
    this.dataViewFormTarget.value = sView;
    this.pageRowsFormTarget.value = iPageRows;

    this.searchFormTarget.submit();
  }

  _initPaginator(){
    const that = this;

    //modify bootstrap-paginator a tags to disable the default behaviour
    //and execute a form post to get another page
    $("a", ".pagination").each(function() {
        $(this).click(function(e) {

            //disable pagination links
            const parent = $(this).parent("li");
            if(parent.hasClass("active") || parent.hasClass("disabled")){
                e.preventDefault();
                return false;
            }
            //set new links
            const href = $(this).attr("href");
            const patt = /\/(\d+)/g;
            const page = patt.exec(href);

            //update form
            if (page) {
              const sSearch= that._getFilterQuery(true);
              const iPage = page[1];
              const sView = that.data.get('view');
              const iPageRows = that.pageRowsFormTarget.value

              that._submitSearchForm(sSearch, iPage, sView, iPageRows);
            }
            
            e.preventDefault();
        });

    });
  }
}