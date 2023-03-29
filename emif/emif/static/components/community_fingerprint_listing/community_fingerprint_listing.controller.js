
function CommunityFingerprintListingController(module) {
    Controller.call(this, module, new CommunityFingerprintListingView(this));
};

extend(CommunityFingerprintListingController, Controller);

CommunityFingerprintListingController.prototype.initialize = function ($container) {
    Controller.prototype.initialize.call(this, $container, null);
};

CommunityFingerprintListingController.prototype.init = function () {
    
    //call services here

    //render handlebars
    this.view.render(this.data)
};

// Destroy not needed component 
CommunityFingerprintListingController.prototype.destroy = function () {
    this.container = null;
    this.values = null;
};

