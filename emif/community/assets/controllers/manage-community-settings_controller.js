import { Controller } from "stimulus";
import MontraAxios from "../../../api/assets/montra-axios";

export default class extends Controller {
  static targets = [
    "field_container_table_0",
    "field_selector_table_0",
    "field_container_list_0",
    "field_selector_list_0",
    "field_container_list_1",
    "field_selector_list_1",
    "field_container_card_0",
    "field_selector_card_0",
    "field_container_card_1",
    "field_selector_card_1",
    "field_container_card_2",
    "field_selector_card_2",
    "adv_tree"
  ];

  /*====================================*/
  /*  Lifecycle methods                 */
  /*====================================*/

  connect() {
    this._loadData();
  }

  /*====================================*/
  /*  Public methods                    */
  /*====================================*/

  /*====================================*/
  /*  Private methods                   */
  /*====================================*/

  _sortFunction(a, b) {
    return a.sortid - b.sortid;
  }

  _loadData() {
    var that = this;
    var community = this.data.get("community");
    var questionnaire = this.data.get("questionnaire");

    MontraAxios({
      method: 'get',
      url: "/api/community/" + community + "/questionnaire/" + questionnaire + "/settings/",
    })
      .then(function (response) {
        that._initMultiselects(response.data.result);
        that._initJSTree(response.data.result.questionnaire.questionsets);
      })
      .catch(function (error) {
        console.error(error);
      });
  }

  _initMultiselects(data) {
    var that = this;

    //fields already selected
    var selected = this._getSelectedFields(data.comm_fields);
    //values available to be chosen
    var possible_fields = this._getPossibleFields(data.possible_fields, selected);

    var aMultiselectors = [];

    //table
    aMultiselectors.push({
      selector: this.field_selector_table_0Target,
      selected: selected.table.section_0,
      possible: possible_fields.table.section_0,
      container: this.field_container_table_0Target,
      showLabel: false,
      showIcon: false
    });

    //list
    aMultiselectors.push({
      selector: this.field_selector_list_0Target,
      selected: selected.list.section_0,
      possible: possible_fields.list.section_0,
      container: this.field_container_list_0Target,
      showLabel: true,
      showIcon: false
    });
    aMultiselectors.push({
      selector: this.field_selector_list_1Target,
      selected: selected.list.section_1,
      possible: possible_fields.list.section_1,
      container: this.field_container_list_1Target,
      showLabel: true,
      showIcon: true
    });

    //card
    aMultiselectors.push({
      selector: this.field_selector_card_0Target,
      selected: selected.card.section_0,
      possible: possible_fields.card.section_0,
      container: this.field_container_card_0Target,
      showLabel: false,
      showIcon: true
    });
    aMultiselectors.push({
      selector: this.field_selector_card_1Target,
      selected: selected.card.section_1,
      possible: possible_fields.card.section_1,
      container: this.field_container_card_1Target,
      showLabel: false,
      showIcon: true
    });
    aMultiselectors.push({
      selector: this.field_selector_card_2Target,
      selected: selected.card.section_2,
      possible: possible_fields.card.section_2,
      container: this.field_container_card_2Target,
      showLabel: true,
      showIcon: false
    });

    //init all multiselectors
    aMultiselectors.forEach(element => {
      that._initMultiSelectInput(
        element.selector,
        element.selected,
        element.possible,
        element.container,
        element.showLabel,
        element.showIcon
      );
    });
  }

  _initMultiSelectInput(
    field_selector_el,
    from,
    to,
    field_container_el,
    bSelectShowLabel = false,
    bSelectIcon = false
  ) {
    var finput = $(field_container_el);
    var fselector = $(field_selector_el).orderablemultiselect({
      selectShowLabel: bSelectShowLabel,
      selectIcon: bSelectIcon,
      fromtext: "Selected Fields",
      totext: "Available Fields",
      from: from.sort(this.sortFunction),
      to: to.sort(this.sortFunction),
      change: function (data) {
        finput.val(JSON.stringify(data));
      }
    });

    finput.val(JSON.stringify(fselector.serialization()));
  }

  _getPossibleFields(possible_fields, selected) {

    var fields = {};

    fields.table = { section_0: [] };
    fields.list = { section_0: [], section_1: [] };
    fields.card = { section_0: [], section_1: [], section_2: [] };
    var used_ids = {
      table: {
        section_0: []
      },
      list: {
        section_0: [],
        section_1: []
      },
      card: {
        section_0: [],
        section_1: [],
        section_2: []
      }
    }

    //get used ids on each view
    selected.table.section_0.map(el => used_ids.table.section_0.push(el.id))
    selected.list.section_0.map(el => used_ids.list.section_0.push(el.id))
    selected.list.section_1.map(el => used_ids.list.section_1.push(el.id))
    selected.card.section_0.map(el => used_ids.card.section_0.push(el.id))
    selected.card.section_1.map(el => used_ids.card.section_1.push(el.id))
    selected.card.section_2.map(el => used_ids.card.section_2.push(el.id))

    possible_fields.forEach(field => {

      var entry = {
        id: field.id,
        name: field.number + " " + field.text,
        type: field.type,
        icon: false,
        label: false,
        formatting: true
      };

      //table
      if (!used_ids.table.section_0.includes(field.id)) {
        fields.table.section_0.push(entry);
      }

      //list
      if (!used_ids.list.section_0.includes(field.id)) {
        fields.list.section_0.push(entry);
      }
      if (!used_ids.list.section_1.includes(field.id)) {
        fields.list.section_1.push(entry);
      }

      //card
      if (!used_ids.card.section_0.includes(field.id)) {
        fields.card.section_0.push(entry);
      }
      if (!used_ids.card.section_1.includes(field.id)) {
        fields.card.section_1.push(entry);
      }
      if (!used_ids.card.section_2.includes(field.id)) {
        fields.card.section_2.push(entry);
      }

    });

    return fields;
  }

  _getSelectedFields(comm_fields) {
    var fields = {};
    var TABLE_VIEW = "TB",
      LIST_VIEW = "LT",
      CARD_VIEW = "CD";

    fields.table = { section_0: [] };
    fields.list = { section_0: [], section_1: [] };
    fields.card = { section_0: [], section_1: [], section_2: [] };

    //hardcoded fields
    fields.table.section_0.push({
      name: 'Database Acronym',
      disabled: true
    })
    fields.list.section_0.push({
      name: 'Database Acronym',
      disabled: true
    })
    fields.card.section_0.push({
      name: 'Database Acronym',
      disabled: true
    })

    comm_fields.forEach(field => {
      var entry = {
        id: field.field.id,
        name: field.field.number + " " + field.field.text,
        type: field.field.type,
        sortid: field.sortid,
        icon: field.icon,
        label: field.show_label,
        formatting: field.apply_formatting
      };
      //table
      if (field.view == TABLE_VIEW && field.section == 0)
        fields.table.section_0.push(entry);
      //list
      else if (field.view == LIST_VIEW && field.section == 0)
        fields.list.section_0.push(entry);
      else if (field.view == LIST_VIEW && field.section == 1)
        fields.list.section_1.push(entry);
      //card
      else if (field.view == CARD_VIEW && field.section == 0)
        fields.card.section_0.push(entry);
      else if (field.view == CARD_VIEW && field.section == 1)
        fields.card.section_1.push(entry);
      else if (field.view == CARD_VIEW && field.section == 2)
        fields.card.section_2.push(entry);
    });

    return fields;
  }

  _getJSTreeData(questionsets) {
    var data = [];
    questionsets.forEach((qset, i) => {
      var entry = {
        text: qset.sortid + " " + qset.text,
        id: "qs_" + qset.id,
        state: {
          opened: false
        },
        children: []
      };

      //add children
      qset.questions.forEach((question, i) => {
        entry.children.push({
          text: question.number + ". " + question.text,
          id: "q_" + question.id,
          icon: false,
          state: {
            selected: question.show_advanced
          }
        });
      });

      //add entry
      data.push(entry);
    });

    return data;
  }

  _initJSTree(questionset) {
    var that = this;
    $(that.adv_treeTarget)
      .jstree({
        checkbox: {
          keep_selected_style: false
        },
        plugins: ["checkbox"],
        core: {
          expand_selected_onload: false,
          data: that._getJSTreeData(questionset)
        }
      })
      .on("changed.jstree", function (e, data) {
        $("#adv_change").val(JSON.stringify(data.selected));
      });
  }
}
