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

function question_form_load(course_id, question_id) {
  $('#question_edit_modal').modal('show')
  $.getJSON('/course/' + course_id + '/library/edit_question_render_form', {
    question_id: question_id,
  }, function(data) {
    $('#edit_question_area').html(data.edit_question_html)
    reload_question_tags('edit_question_')
    init_page()
  })
}
