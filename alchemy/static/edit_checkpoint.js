// Switch Management for edit_checkpoint macro

function init_checkpoint_paper_event_listeners(checkpoint_id) {
  console.log("2) Made it into init_checkpoint_paper_event_listeners!!")
  let all_switch = document.getElementById('all_papers_switch_' + checkpoint_id)
  if (!all_switch){
    return
  }
  let switch_container = $('#edit_checkpoint_switch_container_' + checkpoint_id)
  all_switch.addEventListener('change', function() {
      switch_container.find('input').each(function () {
        let paper_switch = $(this).get(0)
        paper_switch.checked = all_switch.checked
      })
    }
  );
  let paper_switch_list = get_paper_switches(switch_container, checkpoint_id)
  console.log("paper_switch_list!!")
  console.log(paper_switch_list)
  for (let i = 0; i < paper_switch_list.length; i++) {
    paper_switch_list[i].get(0).addEventListener('change', function() {
      let all_checked = true
      let paper_switch_container = $('#edit_checkpoint_switch_container_' + checkpoint_id)
      let switches = get_paper_switches(paper_switch_container, checkpoint_id)
      console.log("switches!!")
      console.log(switches)
      for (let j = 0; j < switches.length; j++) {
        if (!switches[j].get(0).checked) {
          all_checked = false
          console.log("all_checked: ")
          consolle.log(all_checked)
        }
      }
      all_switch.checked = all_checked
      console.log("all_switch is changed!!")
    })
  }
}

// Returns a list of jquery switches corresponding to individual papers - skips the 'All' switch.
function get_paper_switches(container, checkpoint_id){
  console.log("3) Made it into get_paper_switches!!")
  console.log("container: ")
  console.log(container)
  console.log("checkpoint_id: ")
  console.log(checkpoint_id)
  let switches = []
  container.find('input').each(function(){
    let paper_switch = $(this)
    if (paper_switch.get(0).id != 'all_papers_switch_' + checkpoint_id) {
      switches.push(paper_switch)
    }
  })
  return switches
}

function get_paper_ids(course_id, checkpoint_id) {
  $.ajax({
    type: 'GET',
    url: '/course/' + course_id + '/get_checkpoint_paper_ids/' + checkpoint_id,
    contentType: 'application/json',
    dataType: 'json',
  }).done(function(data) {
    if (data) {
      initialize_switches(data.paper_ids_json, checkpoint_id)
    }
  });
}

function initialize_switches(paper_id_list, checkpoint_id){
  console.log("1) Made it into initalize_switches!!")
  init_checkpoint_paper_event_listeners(checkpoint_id)
  let all_switch = document.getElementById('all_papers_switch_' + checkpoint_id)
  let switch_container = $('#edit_checkpoint_switch_container_' + checkpoint_id)
  all_switch.checked = true
  let set_all_switch = true
  paper_switches = get_paper_switches(switch_container, checkpoint_id)
  for (let i = 0; i < paper_switches.length; i++) {
    let switch_id = paper_switches[i].attr('data-alchemy_paper_id')
    if (paper_id_list.includes(parseInt(switch_id))) {
      paper_switches[i].get(0).checked = true
    }
    else {
      paper_switches[i].get(0).checked = false
      set_all_switch = false
    }
    all_switch.checked = set_all_switch
  }
}

// Submitting the changes to checkpoint.papers

function submit_edit_checkpoint (course_id, checkpoint_id) {
  let switch_container = $('#edit_checkpoint_switch_container_' + checkpoint_id)
  let switches = get_paper_switches(switch_container, checkpoint_id)
  let paper_id_list = []
  for (let i = 0; i < switches.length; i++) {
    if (switches[i].get(0).checked == true) {
      paper_id_list.push(switches[i].attr('data-alchemy_paper_id'))
    }
  }
  $.ajax({
    type: 'POST',
    url: '/course/' + course_id + '/edit_checkpoint/' + checkpoint_id,
    data: JSON.stringify({
      course_id: course_id,
      paper_ids: paper_id_list
    }),
    contentType: 'application/json',
  })
  document.getElementById('edit_checkpoint_form_' + checkpoint_id).submit();
  return true
}
