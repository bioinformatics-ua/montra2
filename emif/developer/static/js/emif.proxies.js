"use strict";
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
*/
var base = $('#base_link').attr('href');

var Requester = (
    function( window, undefined ) {
        var instance;
        var memoizer= {};
        var pk = undefined;

        var __init__ = function(){

            if(typeof(global_public_key) != 'undefined')
                pk =  global_public_key;

            var inCache = function(url){
                var cache = memoizer[url];
                if(cache)
                    return new Promise(function (fulfill, reject){
                        fulfill(cache);
                    });

                return undefined;
            };

            return {
                getRequest: function(url){

                    if(pk)
                        url = url + '?publickey='+pk;

                    var cache = inCache(url);
                        if(cache)
                            return cache;

                    return Promise.resolve($.get(url).done(
                        function(result){
                            memoizer[url] = result;
                            return result;
                        }).fail(function(ex){
                            return ex;
                        })
                    );
                },
                postRequest: function(url, data, dataType, files){
                    data = data || {};

                    var cache = inCache(url+JSON.stringify(data));
                        if(cache)
                            return cache;

                    if(typeof community != 'undefined'){
                        data['community'] = community;
                    }

                    data['publickey'] = pk;

                    var configs = {
                        url: url,
                        type: "POST",
                        data: data,
                        dataType: dataType || 'json',
                    };
                    if(dataType){
                        configs.dataType = dataType
                    }

                    if(files)
                        configs.fileInputs = files;
                    
                    data['csrfmiddlewaretoken'] = $.cookie('csrftoken');

                    return Promise.resolve($.ajax(configs).done(
                        function(result){
                            memoizer[url+JSON.stringify(data)] = result;
                            return result;
                        }).fail(function(ex){
                            return ex;
                        })
                    );
                }

            }
        }
        return {
            getInstance : function() {
                if( ! instance ) {
                    instance = new __init__();
                }
                return instance;
            }
        };
    }
)(window);

var GlobalProxy = (
    function( window, undefined ) {
        var instance;

        var __init__ = function() {
            var rq = Requester.getInstance();

            return {
                validateFingerprint: function(comm,fingerprint,valid){
                    if(valid) {
                         return rq.postRequest(`${base}community/manage/${comm}/drafts/accept/${fingerprint}`);
                    }
                    return rq.postRequest(`${base}community/manage/${comm}/drafts/deny/${fingerprint}`);
                },
                databaseSchemas : function(){
                    return rq.getRequest(base+'developer/api/databaseSchemas/');
                },
                getProfileInformation : function(){
                    return rq.getRequest(base+'developer/api/getProfileInformation/');
                },
                getFingerprints: function(schema){
                    schema = schema || '';

                    return rq.getRequest(base+'developer/api/getFingerprints/'+schema);
                },
                getFingerprintsOfCommunity: function(community){
                    community = community || '';

                    return rq.getRequest(base+'developer/api/getFingerprintsOfCommunity/'+community);
                },
                getSubscribed: function(community){
                    return rq.getRequest(base+'developer/api/getSubscribed/'+community);
                },
                getCommunityPlugins: function(community){
                    return rq.getRequest(base+'developer/api/getCommunityPlugins/'+community);
                },
                getCommunities: function(){
                    return rq.getRequest(base+'developer/api/getCommunities/');
                },
                query: function(options){
                    var settings = $.extend({
                        'search': '',
                        'rows': 10,
                        'offset': 0,
                        'sort_field': 'name',
                        'sort_order': 'asc',
                        'schema': null
                    }, options);

                    return rq.postRequest('/api/searchdatabases', settings);
                }/*,
                advancedQuery: function(query, schema){

                }*/
            };
        };

        return {
            getInstance : function() {
                if( ! instance ) {
                    instance = new __init__();
                }
                return instance;
            }
        };
    }
)(window);

var DataStore = (
    function( window, undefined ) {
        var instance = {};

        var __init__ = function(hash) {
            var rq = Requester.getInstance();

            return {
                hasDefaultContent: function(){
                    return [];
                },
                getExtra: function(){
                    return rq.getRequest(base+'developer/api/store/getExtra/'+hash)
                },
                hasExtra: function(){
                    return rq.getRequest(base+'developer/api/store/getExtra/'+hash)
                },
                putExtra: function(values){
                    var data = {
                        values: JSON.stringify(values || {}),
                        fingerprintID: hash
                    };

                    return rq.postRequest('/api/metadata', data)
                },
                getDocuments: function(){
                    return rq.getRequest(base+'developer/api/store/getDocuments/'+hash)
                },
                hasDocuments: function(){
                    return rq.getRequest(base+'developer/api/store/getDocuments/'+hash)
                },

                /* This doesnt make the document available for the plugin,
                only downloads the file for the user
                To be able to download the file, the file must respond as attachment.
                */
                downloadDocument: function(name, revision){
                        var df = $(
                            '<form style="display:none;" id="downloadfile" action="/api/getfile" method="post">\
                                <input name="filename" value="'+name+'"></input>\
                                <input name="revision" value="'+revision+'"></input>\
                                <input name="publickey" value=""></input>\
                                <input name="fingerprint" value="'+hash+'"></input>\
                                <input type="submit"></input>\
                            </form>').appendTo(document.body);

                        df.submit();

                        setTimeout(df.remove(), 1000);
                },
                /* To be able to upload files through ajax, we must have a formdata object.
                   This has to come from a real DOM file input element
                */
                putDocument: function(DOM_fileinput_id, options){
                    if(DOM_fileinput_id){

                        var data = {
                            'pc_name': options.name || '',
                            'pc_comments': options.description || ''
                        }
                        return rq.postRequest(base+'developer/api/store/putDocuments/'+hash+'?format=json',
                            data, 'iframe json', $('#'+DOM_fileinput_id).attr('name', 'file'))
                    }

                },
                getPublications: function(){
                    return rq.getRequest(base+'developer/api/store/getPublications/'+hash)
                },
                hasPublications: function(){
                    return rq.getRequest(base+'developer/api/store/getPublications/'+hash)
                },
                getComments: function(){
                    return rq.getRequest(base+'developer/api/store/getComments/'+hash)
                },
                hasComments: function(){
                    return rq.getRequest(base+'developer/api/store/getComments/'+hash)
                },
                putComment: function(options){
                    var data = {
                        comment: options.comment || ''
                    };

                    return rq.postRequest(base+'developer/api/store/putComment/'+hash, data)
                },
                setEmpty: function(plugin,bool){
                    var data = {
                        plugin: plugin,
                        empty: bool
                    };

                    return rq.postRequest('/developer/api/store/setEmpty/'+hash, data)
                }
            }
        }

        return {
            getInstance : function(hash) {
                if( ! instance[hash] ) {
                    instance[hash] = new __init__(hash);
                }
                return instance[hash];
            }
        };
    }
)(window);

var FingerprintProxy = (
    function( window, undefined ) {
        var instance = {};
        var __init__ = function(hash) {
            var rq = Requester.getInstance();

            return {
                getFingerprintUID: function(){
                    return rq.getRequest(base+'developer/api/getFingerprintUID/'+hash)
                },
                getAnswers: function(){
                    return rq.getRequest(base+'developer/api/getAnswers/'+hash)
                },
                getStore: function(){
                    return DataStore.getInstance(hash)
                }
            };
        };

        return {
            getInstance : function(hash) {
                if(typeof global_fingerprint_id !== undefined)
                    hash = hash || global_fingerprint_id;

                if( ! instance[hash] ) {
                    instance[hash] = new __init__(hash);
                }
                return instance[hash];
            }
        };
    }
)(window);
