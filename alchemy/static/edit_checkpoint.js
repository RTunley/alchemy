var all_switch = document.getElementById('all_papers_switch')
var switch_container = $('#edit_checkpoint_switch_container')
all_switch.addEventListener('change', function() {
    switch_container.find('input').each(function () {
      var paper_switch = $(this).get(0)
      paper_switch.checked = all_switch.checked
    })
  }
);

//
// function checkpoint_papers_all() {
//   // Activate all papers
//   checkpoint_papers_reset(true)
// }
//
// function checkpoint_papers_none() {
//   // Deactivate all papers
//   checkpoint_papers_reset(false)
// }
//
// function checkpoint_papers_reset(activate_papers) {
//   // Reset the list of papers
//   var switch_container = $('#edit_checkpoint_switch_container')
//   if (activate_papers || !window.checkpoint_paper_select) {
//     window.checkpoint_paper_select = {}
//   }
//
//   // Reset the active state of all paper switches
//   switch_container.children('input').each(function () {
//     var switch = $(this)
//     switch.toggleClass('active', activate_papers)
//     if (!activate_papers) {
//       var paper_id = button.attr('data-alchemy_paper_id')
//       window.checkpoint_paper_select[paper_id] = true
//     }
//   })
  //
  // if (activate_tags) {
  //   $('#library_question_filter_tags_all').removeAttr('href')
  //   $('#library_question_filter_tags_none').attr('href', '#')
  // } else {
  //   $('#library_question_filter_tags_all').attr('href', '#')
  //   $('#library_question_filter_tags_none').removeAttr('href')
  // }
// }
