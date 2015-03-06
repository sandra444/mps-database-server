// Adding this script will override enter such that it will display a modal confirmation
$(document).ready(function () {
    $("#content").append('<div hidden id="dialog-confirm" title="Submit this form?"><p><span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 20px 0;"></span>Are you sure you want to submit the form?</p></div>');

    var dialogConfirm = $("#dialog-confirm");

    dialogConfirm.dialog({
        height:200,
        modal: true,
        buttons: {
        Submit: function() {
            $("#submit").trigger("click");
            },
        Cancel: function() {
            $(this).dialog("close");
            }
        }
    });

    dialogConfirm.dialog('close');
    dialogConfirm.removeProp('hidden');

    $(window).keydown(function(event){
        if(event.keyCode == 13) {
          event.preventDefault();
          dialogConfirm.dialog('open');
          return false;
        }
    });
});
