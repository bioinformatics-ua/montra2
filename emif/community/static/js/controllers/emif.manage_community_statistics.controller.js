
function CommunityStatisticsController(module) {
    //this.container = $('.groups-plugins-container');
    //this.values = {};
    Controller.call(this, module, new CommunityStatisticsView(this));

};
extend(CommunityStatisticsController, Controller);

CommunityStatisticsController.prototype.initialize = function ($container) {
    Controller.prototype.initialize.call(this, $container);
    this.view.loadStatistics({test: 'vv'});

};

// Destroy not needed component 
CommunityStatisticsController.prototype.destroy = function () {
    this.container = null;
    this.values = null;
};

