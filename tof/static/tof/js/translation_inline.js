/*
* @Author: MaxST
* @Date:   2019-12-04 16:33:59
* @Last Modified by:   MaxST
* @Last Modified time: 2019-12-15 17:00:55
*/
(function ($) {
  "use strict";
  $(document).ready(function () {
    var fld = $(".field-field .admin-autocomplete").not("[name*=__prefix__]");
    fld.attr("readonly", true);
    fld.on("select2:opening", function (e) {
      if ($(this).attr("readonly") || $(this).is(":hidden")) {
        e.preventDefault();
      }
    });
    fld.each(function () {
      if ($(this).is("[readonly]")) {
        $(this)
          .closest(".form-group")
          .find("span.select2-selection__choice__remove")
          .first()
          .remove();
        $(this)
          .closest(".form-group")
          .find("li.select2-search")
          .first()
          .remove();
        $(this)
          .closest(".form-group")
          .find("span.select2-selection__clear")
          .first()
          .remove();
      }
    });
  });
}(jQuery));
