/*
* @Author: MaxST
* @Date:   2019-11-09 13:52:25
* @Last Modified by:   MaxST
* @Last Modified time: 2019-11-09 19:57:46
*/
$(document).ready(function () {
  var $ = django.jQuery;
  $('#id_field').change(function () {
    if (! $(this).val())
      return;

    $.get({
      url: '?field_id=' + $(this).val(),
      success: function (data, textStatus, jqXHR) {
        $('#id_content_type').val(data.content_type);
      },
      dataType: "json"
    });
  });
});
