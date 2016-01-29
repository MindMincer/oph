horizon.addInitFunction(function() {
  var allPanelGroupBodies = $('.nav_accordion > dd > div > ul');
  // In case the event was generated by clicking any mouse button,
  // the normalized codes are matched according to http://api.jquery.com/event.which/
  var MOUSE_LBUTTON_CODE_NORMALIZED = 1;
  var MOUSE_WHEEL_CODE_NORMALIZED = 2;

  // mark the active panel group
  var activePanel = $('.nav_accordion > dd > div > ul > li > a.active');
  activePanel.closest('div').find('h4').addClass('active');

  // dashboard click
  $('.nav_accordion > dt').click(function() {
    var myDashHeader = $(this);
    var myDashWasActive = myDashHeader.hasClass("active");

    // mark the active dashboard
    var allDashboardHeaders = $('.nav_accordion > dt');
    allDashboardHeaders.removeClass("active");

    // collapse all dashboard contents
    var allDashboardBodies = $('.nav_accordion > dd');
    allDashboardBodies.slideUp();

    // if the current dashboard was active, leave it collapsed
    if(!myDashWasActive) {
      myDashHeader.addClass("active");

      // expand the active dashboard body
      var myDashBody = myDashHeader.next();
      myDashBody.slideDown();

      var activeDashPanel = myDashBody.find("div > ul > li > a.active");
      // if the active panel is not in the expanded dashboard
      if (activeDashPanel.length === 0) {
        // expand the active panel group
        var activePanel = myDashBody.find("div:first > ul");
        activePanel.removeClass('hidden').slideDown();
        activePanel.closest('div').find("h4").addClass("active");

        // collapse the inactive panel groups
        var nonActivePanels = myDashBody.find("div:not(:first) > ul");
        nonActivePanels.slideUp();
      }
      // the expanded dashboard contains the active panel
      else
      {
        // collapse the inactive panel groups
        activeDashPanel.closest('div').find("h4").addClass("active");
        activeDashPanel.closest('ul').removeClass('hidden').slideDown();
        allPanelGroupBodies.each(function(index, value) {
          var activePanels = $(value).find('li > a.active');
          if(activePanels.length === 0) {
            $(this).slideUp();
          }
        });
      }
    }
    return false;
  });

  // panel group click
  $('.nav_accordion > dd > div > h4').click(function() {
    var myPanelGroupHeader = $(this);
    myPanelGroupWasActive = myPanelGroupHeader.hasClass("active");

    // collapse all panel groups
    var allPanelGroupHeaders = $('.nav_accordion > dd > div > h4');
    allPanelGroupHeaders.removeClass("active");
    allPanelGroupBodies.slideUp();

    // expand the selected panel group if not already active
    if(!myPanelGroupWasActive) {
      myPanelGroupHeader.addClass("active");
      myPanelGroupHeader.closest('div').find('ul').removeClass('hidden')
        .slideDown();
    }
  });

  // panel selection
  $('.nav_accordion > dd > div > ul > li > a').click(function(ev) {
    // NOTE(tsufiev): prevent infinite 'Loading' spinner when opening link
    // in the other browser tab with mouse wheel or mouse lbutton + modifier
    if ( ev.which !== MOUSE_WHEEL_CODE_NORMALIZED &&
      !( ev.which === MOUSE_LBUTTON_CODE_NORMALIZED &&
            ( ev.shiftKey || ev.ctrlKey ) ) ) {
      horizon.modals.modal_spinner(gettext("Loading"));
    }
  });

});
