/*
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
*/

var SubscribedWidget = function SubscribedWidget(widgetname, width, height, pos_x, pos_y){

    SubscribedWidget._base.apply(this, [widgetname, "Subscribed Databases", width, height, pos_x, pos_y]);

}.inherit(DashboardWidget).addToPrototype({
    __init : function(gridster, parent){
        var self = this;

        self.icon = '<i class="fas fa-fw fa-rss"></i>';

        self.content = "<center><h3>Loading...</h3></center>";

        SubscribedWidget._super.__init.apply(self, [gridster, parent]);

        var gp = GlobalProxy.getInstance();

        gp.getSubscribed(community).then(function(data) {
            self.content = '<table class="table">';
                if(data.fingerprints){
                    if(data.fingerprints.length == 0){
                        self.content+='<tr><td><center>Currently not subscribed to any databases</center></td></tr>'
                    }

                    for(var i=0;i<data.fingerprints.length;i++){
                        self.content +=
                        '<tr><td style="word-break: break-all;"><small><a href="c/'+document.getElementById("communityindicator").value+'/fingerprint/'+ data.fingerprints[i]['fingerprint_hash']+'/1">'+data.fingerprints[i].name+ "</a></small></td></tr>";
                    }
                }

                SubscribedWidget._super.__refresh.apply(self);

                $('.table', $('#'+self.widgetname)).parent().css('padding', '0px');
        }).catch(function(){
            self.content = ' Error loading User Statistics Widget';

            SubscribedWidget._super.__refresh.apply(self);
        });
    }
});
