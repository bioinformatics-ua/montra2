function CommunityFingerprintListingView(controller) {
    View.call(this, controller, '/static/components/community_fingerprint_listing/community_fingerprint_listing.handlebars');
}

extend(CommunityFingerprintListingView, View);

CommunityFingerprintListingView.prototype.initialize = function ($container) {
    View.prototype.initialize.call(this, $container, null, this.controller.onAfterTemplateLoading);
};

CommunityFingerprintListingView.prototype.render = function (data) {
    var self = this;
    
    console.log(data)
    var htmlContentProcessed = self.templateRaw(data);
    self.$container.html(htmlContentProcessed);
};