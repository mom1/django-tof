/*
* @Author: MaxST
* @Date:   2019-11-09 13:52:25
* @Last Modified by:   MaxST
* @Last Modified time: 2019-11-12 13:31:30
*/
(function($){

  window.generic_view_json = function(self,url,selector, content_type){
    var init = $(self).data("init");
    var contentID = self.id;
    var paramContenID = contentID.replace("id_","").replace("content_type","")
    var objectID = "id_" + paramContenID + selector;
    var id = self.value;

    var $drop = $("#"+objectID);
    var value = null;
    if( init != null ){
      if( init['id'] == id ){
        value = init['value'];
      }
    } else {
      value = $drop.val();
      $(self).data("init",{id:id,value:value});
    }

    var $select = $drop;

    if( !$select.is("select")){
      $select = $("<select/>").attr({
        id : objectID,
        name : $drop.attr('name')
      }).addClass("rel-generic");
      $drop.replaceWith($select);
    }

    $select.html('<option value="">---------</option>');
    if( id != "" ){
      var path = url + "&id=" + id;
      $.getJSON(path,function(data){
        for( var i=0; i<data.length;++i){
          var item = data[i];
          var val = item['pk'];
          var title = item['text'];
          var option = $("<option/>").val(val).text(title);
          if( value == val ){
            option.attr('selected','selected');
          }
          $select.append(option);
        }
        $select.parents("fieldset:first").trigger("generickey_update");
      });
    }
  };

  $(document).ready(function(){
    generic_view_json(document.querySelector('#id_content_type'),'?get_objs=1','object_id','content_type');

    $('#id_field').change(function () {
      $('#id_object_id').removeAttr('readonly');
      if (! $(this).val()) {
        $('#id_object_id').attr('readonly', true);
        return;
      }
      $.get({
        url: '?field_id=' + $(this).val(),
        success: function (data, textStatus, jqXHR) {
          $('#id_content_type').val(data.content_type);
          generic_view_json(document.querySelector('#id_content_type'),'?get_objs=1','object_id','content_type');
        },
        dataType: "json"
      });
    });
  });
})(jQuery);
