let all_switch = document.getElementById('all_papers_switch')
let switch_container = $('#edit_checkpoint_switch_container')
all_switch.addEventListener('change', function() {
    switch_container.find('input').each(function () {
      let paper_switch = $(this).get(0)
      paper_switch.checked = all_switch.checked
    })
  }
);

function get_paper_switches(container){
  let switches = []
  container.find('input').each(function(){
    let paper_switch = $(this).get(0)
    if (paper_switch.id != 'all_papers_switch') {
      switches.push(paper_switch)
    }
  })
  return switches
}

paper_switch_list = get_paper_switches(switch_container)
for (let i = 0; i < paper_switch_list.length; i++) {
  paper_switch_list[i].addEventListener('change', function() {
    let all_checked = true
    switches = get_paper_switches(switch_container)
    for (let i = 0; i < paper_switch_list.length; i++) {
      if (!switches[i].checked) {
        all_checked = false
      }
    }
    all_switch.checked = all_checked
  })
}

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
  let set_all_switch = true
  switch_container.find('input').each(function () {
    let paper_switch = $(this)
    if (paper_switch.get(0).id != "all_papers_switch") {
      let switch_id = paper_switch.attr('data-alchemy_paper_id')
      if (paper_id_list.includes(parseInt(switch_id))) {
        paper_switch.get(0).checked = true
      }
      else {
        paper_switch.get(0).checked = false
        set_all_switch = false
      }
    }
  })
  all_switch.checked = set_all_switch
}
