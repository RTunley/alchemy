function mc_result_input_reload() {
    $('#mc_result_input_cancel').prop('disabled', false)
    $('#mc_result_input_save').prop('disabled', false)
    window.mc_result_selection = {}
}

function mc_result_input_select(selected_button) {
    let question_id = selected_button.attr('data-alchemy_mc_question_id')
    let selected_solution = selected_button.attr('data-alchemy_mc_solution_id')
    if (window.mc_result_selection[question_id] === selected_solution) {
        return
    }

    window.mc_result_selection[question_id] = selected_solution

    // Change the selected button in this row
    let got_correct_solution = false
    selected_button.parent().children('button').each(function() {
        let button = $(this)
        let solution = button.attr('data-alchemy_mc_solution_id')
        if (solution == selected_solution) {
            button.css('border', 'solid 5px orange')
            if (button.attr('data-alchemy_mc_solution_correct') == 'True') {
                got_correct_solution = true
            }
        } else {
            button.css('border', 'solid 5px transparent')
        }
    })

    // Show the 'check' icon if the correct solution was selected
    let mc_question_success = $('#mc_result_input_tick_' + question_id)
    if (got_correct_solution) {
        mc_question_success.css('visibility', 'visible')
    } else {
        mc_question_success.css('visibility', 'hidden')
    }
}

function mc_result_input_submit(course_id, clazz_id, paper_id, student_id) {
    $('#mc_result_input_cancel').prop('disabled', true)
    $('#mc_result_input_save').prop('disabled', true)

    $.ajax({
      type: 'POST',
      url: '/course/' + course_id + '/clazz/' + clazz_id + '/mc_result_input_submit',
      data: JSON.stringify({
        clazz_id: clazz_id,
        paper_id: paper_id,
        student_id: student_id,
        mc_result_selection: mc_result_selection,
      }),
      contentType: 'application/json',
      complete: function(jqXHR, textStatus) {
          mc_result_input_reload()
          window.location.reload()
      }
    })

    return false
}



function reload_question_tags(form_prefix){
  if (!window.question_tags) {
    window.question_tags = {}
  }
  if (!window.existing_tags) {
    window.existing_tags = {}
  }

  if (!window.question_tags[form_prefix]) {
    window.question_tags[form_prefix] = []
  }
  if (!window.existing_tags[form_prefix]) {
    window.existing_tags[form_prefix] = []
  }

  // Edit Question screen - Question already has some tags
  var hidden_question_tags = document.getElementById(form_prefix + 'hidden_question_tags')
  var i
  var len
  if (hidden_question_tags.value) {
    var question_tags_array = hidden_question_tags.value.split(',')
    window.question_tags[form_prefix] = question_tags_array
    for (i = 0, len = question_tags_array.length; i < len; i++){
      add_question_tag(form_prefix, question_tags_array[i])
    }
  }

  //Build Course tag buttons
  var course_tag_string = document.getElementById(form_prefix + 'hidden_course_tags').value
  var course_tags_array = course_tag_string.split(',')
  window.existing_tags[form_prefix] = course_tags_array
  for (i = 0, len = course_tags_array.length; i < len; i++){
    var tag_string = course_tags_array[i]
    if (!window.question_tags[form_prefix].includes(tag_string)){
      create_course_tag_button(form_prefix, tag_string)
    }
  }

  // Manage new tags
  var tag_field = document.getElementById(form_prefix + 'new_tag_field')
  var add_tag_button = document.getElementById(form_prefix + 'newTag')
  add_tag_button.addEventListener('click', function(){
    var new_tag_string = tag_field.value.trim()
    console.log('New Tag = ', new_tag_string)
    tag_field.value = ''
    if (new_tag_string.length > 0
        && !window.question_tags[form_prefix].includes(new_tag_string)){
      add_question_tag(form_prefix, new_tag_string)
    }
  })
  var submit_button = document.getElementById(form_prefix + 'submit')
  submit_button.addEventListener('click', function(event) {
    var tag_string = window.question_tags[form_prefix].join(',')
    hidden_question_tags.value = tag_string
  })
}

function add_question_tag(form_prefix, new_tag_string){
  var tag_array = window.question_tags[form_prefix]
  var newButton = create_button(new_tag_string)
  newButton.className = 'btn btn-outline-success btn-sm m-1'
  newButton.addEventListener('click', function(event) {
    remove_question_tag_button(form_prefix, event)
  })
  if (!tag_array.includes(new_tag_string)){
    tag_array.push(new_tag_string)
  }
  var tags_field = document.getElementById(form_prefix + 'question-tags')
  tags_field.appendChild(newButton)
}

// For tags already in the course
function create_course_tag_button(form_prefix, tag_string){
  var newButton = create_button(tag_string)
  newButton.className = 'course-tag-button btn btn-outline-info btn-sm m-1'
  newButton.addEventListener('click', function(e){
    add_question_tag(form_prefix, tag_string)
    e.currentTarget.remove()
  })
  var tags_field = document.getElementById(form_prefix + 'course_tags')
  tags_field.appendChild(newButton)
}

function remove_question_tag_button(form_prefix, e){
  e.currentTarget.remove()
  var tag_text = e.currentTarget.innerHTML
  if (window.existing_tags[form_prefix].includes(tag_text)){
    create_course_tag_button(form_prefix, tag_text)
  }
  const index = window.question_tags[form_prefix].indexOf(tag_text)
  if (index > -1){
    window.question_tags[form_prefix].splice(index,1)
    console.log('removed, now Question tags: ',window.question_tags[form_prefix])
  }
}

function create_button(tag_string){
  var newButton = document.createElement('BUTTON')
  newButton.innerHTML = tag_string
  newButton.type = 'button'
  newButton.id = tag_string + '-button'
  return newButton
}
