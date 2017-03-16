$(document).ready(function() {

  // init foundation for offcanvas menu
  $(document).foundation();


  // custom theme js for sidebar links
  var allClosed;

  // close all accordions, besides the menu containing the page that you've clicked on.
  $('.toctree-l1').each(function(){
    if($(this).children('a').attr('state') == 'open') {
      $(this).children('ul').show();
      allClosed = false;
      return false;
    } else {
      allClosed = true;
    }
  });

  if (allClosed == true) { }

  // if menu is closed when clicked, expand it
  $('.toctree-l1 > a').click(function() {

    //Make the titles of open accordions dead links
    if ($(this).attr('state') == 'open') {return false;}

    //Clicking on a title of a closed accordion
    if($(this).attr('state') != 'open' && $(this).siblings().size() > 0) {
      $('.toctree-l1 > ul').hide();
      $('.toctree-l1 > a').attr('state', '');
      $(this).attr('state', 'open');
      $(this).next().slideDown(function(){});
      return false;
    }
  });


  // insert urls into markdown
  $(function(){
    $('a#AWS').attr('href', documentationBaseURL + '/quickstart/provider/aws/boot/')
    $('a#GKE').attr('href', documentationBaseURL + '/quickstart/provider/gke/boot/')
    $('a#Minikube').attr('href', documentationBaseURL + '/quickstart/provider/minikube/boot/')
    $('a#Azure').attr('href', documentationBaseURL + '/quickstart/provider/azure-acs/boot/')
  });

});


// use headroom.js for sticky topbar
(function() {
  var searchBar = document.querySelector(".top-bar");
  new Headroom(searchBar, {
    offset: 50,
    classes: {
      "initial": "headroom",
      "pinned": "headroom--pinned",
      "unpinned": "headroom--unpinned",
      "top" : "headroom--top",
      "notTop" : "headroom--not-top"
    }
  }).init();
}());
