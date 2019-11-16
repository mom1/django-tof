/*
* @Author: MaxST
* @Date:   2019-11-09 13:52:25
* @Last Modified by:   MaxST
* @Last Modified time: 2019-11-12 21:09:24
*/
(function ($) {

  window.generic_view_json = function (fields, text) {
    var $drop = $('#id_name');
    var $select = $drop;
    var value = $drop.val();
    // var old_url = $drop.attr('data-ajax--url');

    if (!$select.parent().is(".related-widget-wrapper")) {
      $select = $('<div class="related-widget-wrapper"/>');
      $drop.replaceWith($select);
    } else {
      $select = $select.parent();
    }

    var sel = $('<select/>');
    sel.attr({
      'id': 'id_name',
      'name': 'name',
      'class': 'admin-autocomplete',
      'tabindex': -1,
      // 'aria-hidden': true,
      // 'data-ajax--cache': true,
      // 'data-ajax--delay': 250,
      // 'data-ajax--type': 'GET',
      // 'data-ajax--url': '',
      'data-allow-clear': false,
      'data-placeholder': '',
      'data-theme': 'admin-autocomplete'
    });

    // if (value && text) {
    //   sel.append('<option value="'+value+'" >'+text+'</option>');
    // }
    var data = [];
    $.each(fields, function (index, field) {
      var selected = '';
      if (field == value) {
        selected = 'selected';
      }
      sel.append('<option value="' + field + '" ' + selected + '>' + field + '</option>');

      data.push({id: index, text: field});
    });
    $select.html(sel);
    console.log(data);

    return $('#id_name').djangoAdminSelect2({
      ajax: {
                data: function(params) {
                    return {
                        term: params.term,
                        page: params.page
                    };
                }
            }
    });
  };

  $(document).ready(function () {
    $('#id_content_type').change();

    $('#id_content_type').change(function () {
      $('#id_name').removeAttr('readonly');

      if (!$(this).val()) {
        $('#id_name').attr('readonly', true);
        return;
      }
      var params = {
        'id_ct': $(this).val(),
      };
      // id_obj - текущий выбранный ответ
      // if ($('#id_name').is('input')) {
      //   params['id_obj'] = $('#id_name').val();
      // }
      var esc = encodeURIComponent;
      $.get({
        url: '?' + Object.keys(params).map(function (k) {
          return esc(k) + '=' + esc(params[k]);
        }).join('&'),
        success: function (data, textStatus, jqXHR) {
          $('#id_name').val(data.pk);
          generic_view_json(data.fields, data.text);
        },
        dataType: "json"
      });
    });
  });
}(jQuery));
