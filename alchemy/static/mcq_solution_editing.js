function reload_mcq_solutions_tab(form_prefix) {
  if (!window.mcq_choices) {
    window.mcq_choices = {}
  }

  var hidden_mcq_choices = document.getElementById(form_prefix + 'hidden_mcq_choices')
  var mcq_choices = JSON.parse(hidden_mcq_choices.value)

  var mcq_choices_list_div = document.getElementById(form_prefix + 'mcq_choices_list_div')

  var hidden_correct_mcq_choice_label = document.getElementById(form_prefix + 'hidden_correct_mcq_choice_label')
  var correct_mcq_choice = document.getElementById(form_prefix + 'correct_mcq_choice')
  correct_mcq_choice.innerText = hidden_correct_mcq_choice_label.value

  for (var i = 0; i < mcq_choices.length; ++i) {
    var choice_label = mcq_choices[i].choice_label
    var choice_text = mcq_choices[i].choice_text
    var selected = (choice_label == hidden_correct_mcq_choice_label.value)

    var new_element = new_mcq_choice(form_prefix, choice_label, choice_text, selected)
    mcq_choices_list_div.appendChild(new_element)
  }

  window.mcq_choices[form_prefix] = mcq_choices

  // Render dynamically-created feather icons
  feather.replace()

  var submit_button = document.getElementById(form_prefix + 'submit')
  submit_button.addEventListener('click', function(event) {
    window.mcq_choices[form_prefix] = get_current_mcq_choices(form_prefix)
    hidden_mcq_choices.value = JSON.stringify(window.mcq_choices[form_prefix])
    hidden_correct_mcq_choice_label.value = correct_mcq_choice.innerText
  })

  // Select open-answer solution tab if this is a new question, or if editing a question that already has multiple choice solutions
  var solutionTabTarget = (form_prefix == 'new_question_' || mcq_choices.length <= 1)
      ? form_prefix + 'open_answer_tab'
      : form_prefix + 'mcq_choices_tab'
  $('#' + solutionTabTarget).tab('show')
}

function get_current_mcq_choices(form_prefix) {
  var mcq_choices_list_div = document.getElementById(form_prefix + 'mcq_choices_list_div')
  var mcq_choices = []
  var i

  var choice_label_divs = mcq_choices_list_div.querySelectorAll('span.mcq_choice_label');
  for (i = 0; i < choice_label_divs.length; ++i) {
      mcq_choices.push({'choice_label': choice_label_divs[i].innerText.trim()})
  }

  var choice_text_divs = mcq_choices_list_div.querySelectorAll('input.mcq_choice_text');
  for (i = 0; i < choice_text_divs.length; ++i) {
      mcq_choices[i].choice_text = choice_text_divs[i].value.trim()
  }

  return mcq_choices
}

function new_mcq_choice(form_prefix, choice_label, choice_text, selected) {
  // Renders something like this:
  // <div class="input-group mb-1">
  //   <div class="input-group-prepend">
  //     <div class="input-group-text">
  //       {{ mcq_choice_label }} &nbsp;<input type="radio" name="mcq_choice_radio_group"  onclick="getElementById('{{ form_prefix }}correct_mcq_choice').innerText='{{ mcq_choice_label }}';">
  //     </div>
  //   </div>
  //   <input type="text" class="form-control" placeholder="Option text" value="{{ mcq_choice_text }}">
  //   <div class="input-group-append">
  //     <button class="btn btn-outline-secondary" type="button"><span data-feather="trash-2"></span></button>
  //   </div>
  // </div>

  var input_group = document.createElement('div')
  input_group.className = 'input-group mb-1'

  var input_group_prepend = document.createElement('div')
  input_group_prepend.className = 'input-group-prepend'
  input_group.appendChild(input_group_prepend)

  var input_group_text_div = document.createElement('div')
  input_group_text_div.className = 'input-group-text'
  input_group_prepend.appendChild(input_group_text_div)

  var input_group_text = document.createElement('span')
  input_group_text.className = 'mcq_choice_label'
  input_group_text.innerHTML = choice_label + ' &nbsp;'
  input_group_text_div.appendChild(input_group_text)

  var radio_button = document.createElement('input')
  radio_button.type = 'radio'
  radio_button.name = 'mcq_choice_radio_group'
  radio_button.checked = selected
  radio_button.className = 'mcq_choice_radio'
  radio_button.addEventListener('click', function(event) {
    update_correct_mcq_choice(form_prefix, choice_label)
  })
  input_group_text_div.appendChild(radio_button)

  var choice_text_input = document.createElement('input')
  choice_text_input.type = 'text'
  choice_text_input.className = 'mcq_choice_text form-control'
  choice_text_input.placeholder = 'Option text'
  choice_text_input.value = choice_text
  input_group.appendChild(choice_text_input)
  update_choice_label_color(choice_text_input, selected)

  var delete_button_div = document.createElement('div')
  delete_button_div.className = 'input-group-append'
  input_group.appendChild(delete_button_div)

  var delete_button = document.createElement('button')
  delete_button.type = 'button'
  delete_button.className = 'btn btn-outline-secondary'
  delete_button.addEventListener('click', function(event) {
    remove_mcq_choice(form_prefix, choice_label, input_group)
  })
  delete_button_div.appendChild(delete_button)

  var delete_button_icon = document.createElement('span')
  delete_button_icon.setAttribute('data-feather', 'trash-2')
  delete_button.appendChild(delete_button_icon)

  return input_group
}

function remove_mcq_choice(form_prefix, choice_label, choice_element) {
  var mcq_choices_list_div = document.getElementById(form_prefix + 'mcq_choices_list_div')
  mcq_choices_list_div.removeChild(choice_element)

  var mcq_choices = window.mcq_choices[form_prefix]
  var i
  for (i = 0; i < mcq_choices.length; ++i) {
    if (mcq_choices[i].choice_label == choice_label) {
      window.mcq_choices[form_prefix].splice(i, 1)
      break
    }
  }

  // If ordering of choics has changed, update the choice labels
  var choice_label_divs = document.getElementById(form_prefix + 'mcq_choices_list_div').querySelectorAll('.mcq_choice_label');
  for (i = 0; i < choice_label_divs.length; ++i) {
      choice_label_divs[i].innerHTML = mcq_choice_prefix(i) + ' &nbsp;'
  }

  // If the correct choice was removed, reset the correct choice label
  var correct_mcq_choice = document.getElementById(form_prefix + 'correct_mcq_choice')
  if (correct_mcq_choice.innerText == choice_label) {
    correct_mcq_choice.innerText = '(Not selected)'
  }
}

function update_correct_mcq_choice(form_prefix, choice_label) {
  var correct_mcq_choice = document.getElementById(form_prefix + 'correct_mcq_choice')
  correct_mcq_choice.innerText = choice_label

  var mcq_choices_list_div = document.getElementById(form_prefix + 'mcq_choices_list_div')
  var choice_radio_inputs = mcq_choices_list_div.querySelectorAll('input.mcq_choice_radio');
  var choice_text_inputs = mcq_choices_list_div.querySelectorAll('input.mcq_choice_text');

  for (var i = 0; i < choice_radio_inputs.length; ++i) {
    var is_selected_choice = choice_radio_inputs[i].checked
    update_choice_label_color(choice_text_inputs[i], is_selected_choice)
  }
}

function update_choice_label_color(choice_label_div, selected) {
  if (selected) {
    choice_label_div.style.backgroundColor = 'green'
    choice_label_div.style.color = 'white'
  } else {
    choice_label_div.style.backgroundColor = 'transparent'
    choice_label_div.style.color = 'black'
  }
}

function add_mcq_choice(form_prefix, choice_text_input) {
  var curr_mcq_choices = window.mcq_choices[form_prefix]
  var new_mcq_choice_data = {'choice_label': mcq_choice_prefix(curr_mcq_choices.length), 'choice_text': choice_text_input.value}

  var new_element = new_mcq_choice(form_prefix, new_mcq_choice_data.choice_label, new_mcq_choice_data.choice_text)
  var mcq_choices_list_div = document.getElementById(form_prefix + 'mcq_choices_list_div')
  mcq_choices_list_div.appendChild(new_element)

  choice_text_input.value = ''  // reset the input field for adding new options
  window.mcq_choices[form_prefix].push(new_mcq_choice)

  // Render dynamically-created feather icons
  feather.replace()
}

function mcq_choice_prefix(index) {
  var choice_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  return choice_labels[index]
}
