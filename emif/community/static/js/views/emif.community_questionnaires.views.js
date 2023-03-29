function CommunityQuestionnairesView(controller) {
    View.call(this, controller, '/static/handlebars/community_select_questionnaire.handlebars');
}

extend(CommunityQuestionnairesView, View);

CommunityQuestionnairesView.prototype.initialize = function ($container) {
    View.prototype.initialize.call(this, $container, null, this.controller.onAfterTemplateLoading);
};

CommunityQuestionnairesView.prototype.loadQuestionnaires = function (community) {
    var self = this;

    var onSuccess = function(values){
        var model = {
            questionnaires: values.result,
            comm_slug: self.controller.community 
        };
        var htmlContentProcessed = self.templateRaw(model);
        self.$container.html(htmlContentProcessed);
    }

    var onFail = function(){
        console.log("Error while fetching community's questionnaires.")
    }

    var service = new CommunityQuestionnaireService(community);
    service.get(onSuccess, onFail);
};