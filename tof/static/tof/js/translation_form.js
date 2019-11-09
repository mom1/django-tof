/*
* @Author: MaxST
* @Date:   2019-11-09 13:52:25
* @Last Modified by:   MaxST
* @Last Modified time: 2019-11-09 20:51:02
*/
$(document).ready(function () {
  var $ = django.jQuery;
  $('#id_field').change(function () {
    $('#id_object_id').removeAttr('readonly');
    if (! $(this).val()){
      $('#id_object_id').attr('readonly', true);
      return;
    }

    $.get({
      url: '?field_id=' + $(this).val(),
      success: function (data, textStatus, jqXHR) {
        $('#id_content_type').val(data.content_type);
      },
      dataType: "json"
    });
  });
});
