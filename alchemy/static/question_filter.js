function init_library_filter_properties(properties) {
  window.library_filter_properties = properties
}

function library_filter_tag_clicked(tag_id, button) {
  // Update the list of filtered tags
  if (!window.question_tag_filter) {
    window.question_tag_filter = {}
  }
  button.toggleClass('active')
  if (button.hasClass('active')) {
    delete window.question_tag_filter[tag_id]
  } else {
    window.question_tag_filter[tag_id] = true
  }

  // Ensure All|None buttons are enabled
  $('#library_question_filter_tags_none').attr('href', '#')
  $('#library_question_filter_tags_all').attr('href', '#')

  // Update the displayed questions
  library_filter_tags_apply()
}

function library_filter_tags_all() {
  // Activate all tags
  library_filter_tags_reset(true)

  // Update the displayed questions
  library_filter_tags_apply()
}

function library_filter_tags_none() {
  // Deactivate all tags
  library_filter_tags_reset(false)

  // Update the displayed questions
  library_filter_tags_apply()
}

function library_filter_tags_apply() {
  paper_filter_questions_by_tag(
      window.library_filter_properties.html_container_id, window.library_filter_properties.html_scroll_marker_id, window.library_filter_properties.course_id, window.library_filter_properties.paper_id,
      Object.keys(window.question_tag_filter))

  // When tag filtering is used, text search is ignored.
  // Clear the search text to make this obvious.
  var search_input = $('#library_question_search_input')
  search_input.val('')
  search_input.blur()
}

function library_filter_tags_reset(activate_tags) {
  // Reset the list of filtered tags
  var tag_container = $('#question_library_tag_filter_container')
  if (activate_tags || !window.question_tag_filter) {
    window.question_tag_filter = {}
  }

  // Reset the active state of all tag buttons
  tag_container.children('button').each(function () {
    var button = $(this)
    button.toggleClass('active', activate_tags)
    if (!activate_tags) {
      var tag_id = button.attr('data-alchemy_tag_id')
      window.question_tag_filter[tag_id] = true
    }
  })

  if (activate_tags) {
    $('#library_question_filter_tags_all').removeAttr('href')
    $('#library_question_filter_tags_none').attr('href', '#')
  } else {
    $('#library_question_filter_tags_all').attr('href', '#')
    $('#library_question_filter_tags_none').removeAttr('href')
  }
}

function library_filter_text_changed() {
  // Text searching excludes tag filter, so clear the tag filter to make this clear
  library_filter_tags_reset(true)

  paper_filter_questions_by_text(
      window.library_filter_properties.html_container_id, window.library_filter_properties.html_scroll_marker_id, window.library_filter_properties.course_id, window.library_filter_properties.paper_id,
      document.getElementById('library_question_search_input').value)
}

function paper_filter_questions_by_text(html_container_id, html_scroll_marker_id, course_id, paper_id, search_text) {
  $.getJSON('/course/' + course_id + '/paper/' + paper_id + '/filter_questions_by_text', {
    search_text: search_text,
  }, function(data) {
    $('#' + html_container_id).html(data.question_accordion_html)

    // Queue a re-run of MathJax over the updated question HTML
    MathJax.typesetPromise($('#' + html_container_id))
    init_page()

    // Scroll search results into view
    document.getElementById(html_scroll_marker_id).scrollIntoView()
  })
}

function paper_filter_questions_by_tag(html_container_id, html_scroll_marker_id, course_id, paper_id, tag_filter_list) {
  $.getJSON('/course/' + course_id + '/paper/' + paper_id + '/filter_questions_by_tag', {
    tag_filter: tag_filter_list.join(','),
  }, function(data) {
    $('#' + html_container_id).html(data.question_accordion_html)

    // Queue a re-run of MathJax over the updated question HTML
    MathJax.typesetPromise($('#' + html_container_id))
    init_page()

    // Scroll search results into view
    document.getElementById(html_scroll_marker_id).scrollIntoView()
  })
}
