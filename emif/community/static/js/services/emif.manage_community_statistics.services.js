
function CommunityStatisticsService(baseUrl) {
    this.url = baseUrl + "api/statistics";

};
// Initial all endpoints
CommunityStatisticsService.prototype.init = function (baseUrl) {
    this.url = baseUrl + "api/statistics";
};

// Add the communications mechanisms to submit new update values
CommunityStatisticsService.prototype.submit = function (values, successFn, failFn) {

    $.ajax({
        url: this.url,
        type: "POST",
        dataType: "json",
        data: values
    })
        .done(function (e) {
            successFn();
        })
        .fail(function (e) {
            failFn();
        });
};