function checkpoint_papers_all() {
  // Activate all tags
  checkpoint_papers_reset(true)

  // Update the displayed questions
  library_filter_tags_apply()
}

function checkpoint_papers_none() {
  // Deactivate all tags
  checkpoint_papers_reset(false)

  // Update the displayed questions
  library_filter_tags_apply()
}

function checkpoint_papers_reset(activate_papers) {
  // Reset the list of filtered tags
  var switch_container = $('#edit_checkpoint_switch_container')
  if (activate_papers || !window.question_tag_filter) {
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
