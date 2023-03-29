import { Controller } from "stimulus";
import * as template_list from '../templates/community_select_questionnaire_list.handlebars';
import * as template_card from '../templates/community_select_questionnaire_card.handlebars';
import MontraAxios from "../../../api/assets/montra-axios";

export default class extends Controller {
  static targets = [
    'content'
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

  _loadData() {
    var that = this;
    var community = this.data.get("community");
    var qview = this.data.get("community-qview");


    MontraAxios({
      method: 'get',
      url: "/api/community/" + community + "/questionnaires/",
    })
      .then(function (response) {
        that._render(response.data.result, community, qview);
      })
      .catch(function (error) {
        console.error(error);
      });
  }

  _render(questionnaires, community, qview) {
    var content = this.contentTarget;

    //set counters
    questionnaires.forEach(questionnaire => {
      questionnaire.questions_count = questionnaire.questionsets.reduce((acumulator, q) => acumulator + q.questions.length, 0);
      questionnaire.fingerprints_count = questionnaire.fingerprint_set.filter(({draft}) => draft === false).length;
      questionnaire.more_message = `\
<center><h3 class="no-margn"><strong>${questionnaire.name}</strong></h3></center>\
<div class="col-sm-12">\
<center><img src="${questionnaire.logo}" alt="" style="height:9em;padding:1em;"></center>\
</div>\
<hr />\
<center><strong>Questions in this community: ${questionnaire.questions_count}</strong></center>\
<center><strong>Databases in this community: ${questionnaire.fingerprints_count}</strong></center>\
<hr />\
<strong>Description:</strong><br />\
<div style="text-align: justify">\
${questionnaire.long_description}\
</div><br />\
      `
    });

    //set context data
    var context = {
      questionnaires: questionnaires,
      community: community
    }

    var html
    if (qview === "list")
        html = template_list(context);
    else
        html = template_card(context)

    //update html content
    content.innerHTML = html;
  }
}
