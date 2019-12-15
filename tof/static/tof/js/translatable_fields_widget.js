/*
* @Author: MaxST
* @Date:   2019-11-26 13:42:43
* @Last Modified by:   MaxST
* @Last Modified time: 2019-12-15 15:48:41
*/
(function ($) {
  "use strict";
  function dismissRelatedLookupPopupLang(win, chosenId) {
    $ = django.jQuery;
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem.className.indexOf("vManyToManyRawIdAdminField") !== -1 && elem.value) {
      elem.value += "," + chosenId;
    }
    if (elem.className.indexOf("itab") !== -1 && elem.value) {
      var newItab = $(".itab", $(elem.parentNode)).first().clone();
      var newLtab = $(".ltab", $(elem.parentNode)).first().clone();
      var newTab = $(".tab", $(elem.parentNode)).first().clone();
      var arrId = newItab.attr("id").split("_");
      arrId[0] = chosenId;
      arrId[arrId.length - 1] = chosenId;
      var additional_id = arrId.join("_");
      var oldLabel = $('.ltab[for="' + additional_id + '"]');
      if (oldLabel.length === 0) {
        newItab.attr("id", additional_id);
        newLtab.attr("for", additional_id);
        newLtab.text(chosenId);
        newTab.children().attr({id: arrId.slice(1).join('_'), name: arrId.slice(2).join('_'), value: '', lang: chosenId}).text('').val('');
        var destination = ".tabbed-area._" + newItab.attr("name") + " .add-tab";
        newItab.insertBefore(destination);
        newLtab.insertBefore(destination);
        newTab.insertBefore(destination);
        newLtab.click();
      } else {
        oldLabel.click();
      }
    } else {
      document.getElementById(name).value = chosenId;
    }
    win.close();
  }
  $(document).ready(function () {
    window.dismissRelatedLookupPopup = dismissRelatedLookupPopupLang;
  });
})(jQuery);
