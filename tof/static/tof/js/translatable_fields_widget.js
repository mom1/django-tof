/*
* @Author: MaxST
* @Date:   2019-11-26 13:42:43
* @Last Modified by:   MaxST
* @Last Modified time: 2019-11-29 12:02:08
*/
(function ($) {
  'use strict';
  function dismissRelatedLookupPopupLang(win, chosenId) {
    $ = django.jQuery;
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem.className.indexOf('vManyToManyRawIdAdminField') !== -1 && elem.value) {
      elem.value += ',' + chosenId;
    } else if (elem.className.indexOf('itab') !== -1 && elem.value) {
      var new_itab = $('.itab', $(elem.parentNode)).first().clone();
      var new_ltab = $('.ltab', $(elem.parentNode)).first().clone();
      var new_tab = $('.tab', $(elem.parentNode)).first().clone();
      var arrId = new_itab.attr('id').split('_');
      arrId[0] = chosenId;
      arrId[arrId.length - 1] = chosenId;
      var additional_id = arrId.join('_');
      var old_label = $('.ltab[for="' + additional_id + '"]');
      if (old_label.length == 0) {
        new_itab.attr('id', additional_id);
        new_ltab.attr('for', additional_id);
        new_ltab.text(chosenId);
        new_tab.children().attr({id: arrId.slice(1).join('_'), name: arrId.slice(2).join('_'), value: '', lang: chosenId}).text('');
        var destination = '.tabbed-area._' + new_itab.attr('name') + ' .add-tab';
        new_itab.insertBefore(destination);
        new_ltab.insertBefore(destination);
        new_tab.insertBefore(destination);
        new_ltab.click();
      } else {
        old_label.click();
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
