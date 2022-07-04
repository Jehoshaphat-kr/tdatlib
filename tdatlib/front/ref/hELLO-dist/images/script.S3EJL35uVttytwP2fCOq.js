/* Tistory Tooltip Layer */
$(document).ready(function() {
  var messages = {
    Request: H.skinOptions.messageRequest,
    Unheart: H.skinOptions.messageUnheart,
    Heart: H.skinOptions.messageHeart,
    Unsubscribe: H.skinOptions.messageUnsubscribe,
    Subscribe: H.skinOptions.messageSubscribe,
    Url: H.skinOptions.messageUrl
  };

  if (H.skinOptions.message) {
    h.tooltip(messages);
  }
});

/* TistoryToolbar */
$(document).ready(function() {
  $('.menu_toolbar > div[class=btn_tool]').appendTo('#__nav .right'); // Subscription

  $('.menu_toolbar > #menubar_wrapper > .header_layer').appendTo('#__sidebar .tistory'); // Tistory
});

/* Loader */
$(window).on('load', function() {
  return $('#__loader').fadeOut(500);
});

/* Category */
$(document).ready(function() {
  if (H.skinOptions.foldableCategory) {
    h.foldableCategory();
  }
});

/* Navigation */
$(document).ready(function() {
  var $heading = $('.permalink > header > .heading > *:not(.metainfo)');

  if ($heading.length) {
    $('#__nav > .center').empty().append($heading.clone());
  }
});

/* Permalink */
$(document).ready(function() {
  h.anchorHeadings('.permalink .contents_style', '> h2, > h3, > h4'); // Add 'a' tag into headings

  h.scrollspy({
    context: '.permalink .contents_style',
    spy: '#__spy ul',
    headings: '> h2, > h3'
  }); // Scrollspy

  h.alignImageCenter({
    imageSlideBlock: true,
    imageBlock: true,
    imageGridBlock: true
  }); // Media contents alignment

  h.hljs(H.skinOptions.hljsLight, H.skinOptions.hljsDark); // Highlight.js

  h.removeTextNode('.permalink .tags'); // Remove ',' text in Tags
});

$(document).ready(function() {
  h.styledHeading('.permalink', 'header > .img', H.skinOptions.articleMode, {
    controllable: true,
    modeHandsControlElement: '.permalink .contents_style > div.h[data-mode]'
  }); // Set styled heading

  $(window).on('scroll', h.sticky('#__nav', '.permalink .contents_style', 'sticky')); // Set sticky
});

/* Notification */
$(document).ready(function() {
  setTimeout(function() {
    h.notification('#next', '.thumbnail', 'bottom-right', 15000);
    h.notification('#prev', '.thumbnail', 'bottom-left', 15000);
  }, 3000);
});

/* List */
$(document).ready(function() {
  var $title = $('.list > header .title');
  $title.text($title.text() === '전체 글' ? T.config.BLOG.title : $title.text());
  h.liststyle('.list', '> ul');
});

$(document).ready(function() {
  h.styledHeading('.list', 'header > .img', H.skinOptions.listImageMode, {
    attr: 'data-image-mode'
  });
});

/* Footer */
$(document).ready(function() {
  $('#__footer .theme-btn').click(function() {
    h.switchTheme(H.skinOptions.lightTheme, H.skinOptions.darkTheme); // Switch Theme 'Light' <-> 'Dark'

    h.hljs(H.skinOptions.hljsLight, H.skinOptions.hljsDark); // Highlight.js
  });
});

/* Scoll Indicator */
$(document).ready(function() {
  $(window).on('scroll', function() {
    h.scrollIndicator('#scroll-indicator .progress-bar');
  });
});

