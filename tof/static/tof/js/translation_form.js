/*
* @Author: MaxST
* @Date:   2019-11-09 13:52:25
* @Last Modified by:   MaxST
* @Last Modified time: 2019-12-15 17:15:01
*/
(function ($) {
  "use strict";
  window.generic_view_json = function (url, text) {
    var $drop = $("#id_object_id");
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
      "id": "id_object_id",
      "name": "object_id",
      "class": "admin-autocomplete",
      "tabindex": -1,
      "aria-hidden": true,
      "data-ajax--cache": true,
      "data-ajax--delay": 250,
      "data-ajax--type": "GET",
      "data-ajax--url": url,
      "data-allow-clear": false,
      "data-placeholder": "",
      "data-theme": "admin-autocomplete"
    });
    if (value && text) {
      sel.append('<option value="' + value + '" >' + text + '</option>');
    }
    $select.html(sel);
    return $(".admin-autocomplete").not("[name*=__prefix__]").djangoAdminSelect2();
  };
  $(document).ready(function () {
    $("#id_field").change();
    $("#id_field").change(function () {
      $("#id_object_id").removeAttr("readonly");
      if (! $(this).val()) {
        $("#id_object_id").attr("readonly", true);
        return;
      }
      var params = {
        "field_id": $(this).val()
      };
      if ($("#id_object_id").is("input")) {
        params["id_obj"] = $("#id_object_id").val();
      }
      $.get({
        url: "",
        data: params,
        success(data, textStatus, jqXHR) {
          if (data.errors) {
            return alert(data.errors);
          }
          $("#id_content_type").val(data.pk);
          generic_view_json(data.url, data.text);
        },
        dataType: "json"
      });
    });
  });
}(jQuery));
