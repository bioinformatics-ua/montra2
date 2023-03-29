
function CommunityQuestionnairesController(module) {
    Controller.call(this, module, new CommunityQuestionnairesView(this));
};

extend(CommunityQuestionnairesController, Controller);

CommunityQuestionnairesController.prototype.initialize = function ($container) {
    Controller.prototype.initialize.call(this, $container, null);
};

CommunityQuestionnairesController.prototype.init = function () {
    this.view.loadQuestionnaires(this.community)
};

// Destroy not needed component 
CommunityQuestionnairesController.prototype.destroy = function () {
    this.container = null;
    this.values = null;
};

