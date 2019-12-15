/*
* @Author: MaxST
* @Date:   2019-11-09 13:52:25
* @Last Modified by:   MaxST
* @Last Modified time: 2019-12-15 17:13:32
*/
(function ($) {
  "use strict";
  window.generic_view_json = function (fields, text) {
    var $drop = $("#id_name");
    var $select = $drop;
    var value = $drop.val();
    if (! $select.parent().is(".related-widget-wrapper")) {
      $select = $('<div class="related-widget-wrapper"/>');
      $drop.replaceWith($select);
    } else {
      $select = $select.parent();
    }
    var sel = $("<select/>");
    sel.attr({
      "id": "id_name",
      "name": "name",
      "class": "admin-autocomplete",
      "tabindex": -1,
      "data-allow-clear": false,
      "data-placeholder": "",
      "data-theme": "admin-autocomplete"
    });
    var data = [{id: "", text: ""}];
    sel.append('<option value="" ></option>');
    $.each(fields, function (index, field) {
      var selected = "";
      if (field === value) {
        selected = "selected";
      }
      sel.append('<option value="' + field + '" ' + selected + ">" + field + "</option>");
      data.push({id: field, text: field});
    });
    var commonData = data;
    $select.html(sel);
    $("#id_name").change(function () {
       var title = $(this).val();
       $("#id_title").val(title[0].toUpperCase() + title.slice(1));
     });
    return $("#id_name").djangoAdminSelect2({
      ajax: {
        data(requestData) {
          commonData = data.filter(function(item) {
            if (requestData.term) {
              return item.text.startsWith(requestData.term);
            }
            return true;
          });
        },
        processResults(getData, page) {
          return {results: commonData};
        }
      }
    });
  };
  $(document).ready(function () {
    $("#id_content_type").change();
    $("#id_content_type").change(function () {
      $("#id_name").removeAttr("readonly");
      if (!$(this).val()) {
        $("#id_name").attr("readonly", true);
        return;
      }
      $.get({
        url: "?id_ct=" + $(this).val(),
        success(data, textStatus, jqXHR) {
          if (data.errors) {
            return alert(data.errors);
          }
          generic_view_json(data.fields, data.text);
        },
        dataType: "json"
      });
    });
  });

}(jQuery));

