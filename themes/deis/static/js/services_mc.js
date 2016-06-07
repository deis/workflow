/* Form submission functions for the MailChimp Widget */
;(function($){
  $(function($) {
    $('#mc_submit_type').val('js');

    $('#mc_signup_form').ajaxChimp({
      url: 'https://engineyard.us10.list-manage.com/subscribe/post?u=357ed40192fe99974e132c922&amp;id=afe7ebf4de',
      callback: callbackFunction
    });
  });

  function callbackFunction (resp) {
    $("#mce-EMAIL,#mce-NAME").removeClass('error');
    switch(resp.msg[0]) {
      case '0':
      $("#mce-EMAIL").addClass('error');
      break;
      case '1':
      $("#mce-NAME").addClass('error');
      break;
    }
  }

  function mc_beforeForm(){
      // Disable the submit button
      $('#mc_signup_submit').attr("disabled","disabled");
    }
    function mc_success(data){
      // Re-enable the submit button
      $('#mc_signup_submit').removeAttr("disabled");

      // Put the response in the message div
      $('#mc_message').html(data);

      // See if we're successful, if so, wipe the fields
      var reg = new RegExp("class='mc_success_msg'", 'i');
      if (reg.test(data)){
        $('#mc_signup_form').each(function(){
          this.reset();
        });
        $('#mc_submit_type').val('js');
      }
      $.scrollTo('#mc_signup', {offset: {top: -28}});
    }
  })(jQuery);

