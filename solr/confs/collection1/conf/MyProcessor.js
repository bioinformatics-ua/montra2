/*# -*- coding: utf-8 -*-
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
#*/
//SLUG DEFINITION
var numberofpatientsslug = "number_active_patients_jan2012_d"
var numberofpatients_sort = "nrpatients_sort"

function parseDateString(str){
  if(str == null)
    return null;
  else{
    var date = new Date(str)
    if(isNaN(date.getTime())){
      return null;
    }else{
      return date;
    }
  }
}

function removeNumericFieldMask(numericString){
  var number = 0;
  if(numericString != undefined && numericString.length() > 0){
    //var r = /\./g
    //var nString = numericString.replace(r, '');
    var nString = numericString.split("'").join("");
    number = parseInt(nString);
    if(number == NaN)
      return 0
  }
  return number;
}

function populateNumberOfPatientsSort(doc){
  var n = parseInt(doc.getFieldValue(numberofpatientsslug));

  if(isNaN(n)){
    n=0;
  }
  logger.info("___TIAGO___#EXTRACTED NUMBER OF PATIENTS: "+doc.getFieldValue(numberofpatientsslug));
  logger.info("___TIAGO___#REPLACED NUMBER OF PATIENTS: "+n);
  doc.setField(numberofpatients_sort, n);
}

function processAdd(cmd) {
  doc = cmd.solrDoc;  // org.apache.solr.common.SolrInputDocument 2013-10-30 14:00:32.204662
  id = doc.getFieldValue("id");
  logger.info("MyProcessor#Processing Document: id=" + id);

  var created = doc.getFieldValue("created_dt");
  var date_last_mod = doc.getFieldValue("date_last_modification_dt");

  var createdDate = parseDateString(created);
  var last_modDate =parseDateString(date_last_mod );

  logger.info("__TIAGO__#ADDING STUF: created0="+createdDate);
  logger.info("__TIAGO__#ADDING STUF: created0="+last_modDate);

  populateNumberOfPatientsSort(doc);
// Set a field value:
//  doc.setField("foo_s", "whatever");

// Get a configuration parameter:
//  config_param = params.get('config_param');  // "params" only exists if processor configured with <lst name="params">

// Get a request parameter:
// some_param = req.getParams().get("some_param")
}

function processDelete(cmd) {
  // no-op
}

function processMergeIndexes(cmd) {
  // no-op
}

function processCommit(cmd) {
  // no-op
}

function processRollback(cmd) {
  // no-op
}

function finish() {
  // no-op
}

