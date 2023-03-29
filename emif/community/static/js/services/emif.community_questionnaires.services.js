
function CommunityQuestionnaireService(community) {
    this.url = "/community/" + community + "/api/questionnaires";
};

// Initial all endpoints
CommunityQuestionnaireService.prototype.init = function (community) {
    this.url = "/community/" + community + "/api/questionnaires";
};

// Add the communications mechanisms to get community's questionnaires
CommunityQuestionnaireService.prototype.get = function (successFn, failFn) {
    $.ajax({
        url: this.url,
        type: "GET",
        dataType: "json"
    })
    .done(function (e) {
        successFn(e);
    })
    .fail(function (e) {
        failFn(e);
    })
};