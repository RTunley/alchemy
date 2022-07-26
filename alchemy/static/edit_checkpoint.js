let all_switch = document.getElementById('all_papers_switch')
let switch_container = $('#edit_checkpoint_switch_container')
all_switch.addEventListener('change', function() {
    switch_container.find('input').each(function () {
      let paper_switch = $(this).get(0)
      paper_switch.checked = all_switch.checked
    })
  }
);

function get_paper_ids(course_id, checkpoint_id) {
  $.ajax({
    type: 'GET',
    url: '/course/' + course_id + '/get_checkpoint_paper_ids/' + checkpoint_id,
    contentType: 'application/json',
    dataType: 'json',
  }).done(function(data) {
    if (data) {
      initialize_switches(data.paper_ids_json)
    }
  });
}

function initialize_switches(paper_id_list){
  console.log(paper_id_list)
  let set_all_switch = true
  console.log(set_all_switch)
  switch_container.find('input').each(function () {
    let paper_switch = $(this)
    let switch_id = paper_switch.attr('data-alchemy_paper_id')
    console.log(paper_id_list.includes(switch_id))
    if (if paper_id_list.includes(switch_id)) {
      paper_switch.get(0).checked = true
    }
    else {
      paper_switch.get(0).checked = false
      set_all_switch = false
    }
  })
  all_switch.checked = set_all_switch
}


// switch_container.find('input').each(function () {
//   let paper_switch = $(this).get(0)
//   paper_switch.addEventListener('change', function() {
//     let all_checked = true
//     switch_container.find('input').each(function () {
//         let paper_switch_loop = $(this).get(0)
//         if (!paper_switch_loop.checked) {
//           all_checked = false
//         }
//     })
//     if (all_checked == true) {
//       all_switch.checked = true
//     }
//   })
// )}

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
