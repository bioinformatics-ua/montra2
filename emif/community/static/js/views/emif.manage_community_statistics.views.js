function CommunityStatisticsView(controller) {
    View.call(this, controller, 'manage-statistics-view');
}
extend(CommunityStatisticsView, View);

CommunityStatisticsView.prototype.initialize = function ($container) {
    console.log("CommunityStatisticsView initialize ");
    console.log($container);
    View.prototype.initialize.call(this, $container);
};

CommunityStatisticsView.prototype.showLoader = function () {
    this.$elements.statistics.html(Urls['manage-statistics-view']());
};

CommunityStatisticsView.prototype.loadStatistics = function (statistics) {
    this._loadViewComponents();
    console.log(this);
    var self = this;
    setTimeout(function(){

        console.log("Statistics");
        console.log(statistics);

        var htmlContentProcessed = self.templateRaw(statistics);
        console.log("Raw");
        console.log(self.templateRaw);
        console.log("Processed");
        console.log(htmlContentProcessed);

        self.$container.html(htmlContentProcessed);
    },1000);
    
    
    
    
};