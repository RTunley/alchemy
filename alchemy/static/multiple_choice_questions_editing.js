function reload_multiple_choice_questions(form_prefix) {
  if (!window.multiple_choice_qs) {
    window.multiple_choice_qs = {}
  }

  var hidden_solution_choices = document.getElementById(form_prefix + 'hidden_solution_choices')
  var solution_choices = JSON.parse(hidden_solution_choices.value)

  var solution_choices_list_div = document.getElementById(form_prefix + 'solution_choices_list_div')

  var hidden_solution_correct_label = document.getElementById(form_prefix + 'hidden_solution_correct_label')
  var correct_solution_choice = document.getElementById(form_prefix + 'correct_solution_choice')
  correct_solution_choice.innerText = hidden_solution_correct_label.value

  for (var i = 0; i < solution_choices.length; ++i) {
    var choice_label = solution_choices[i].choice_label
    var choice_text = solution_choices[i].choice_text
    var selected = (choice_label == hidden_solution_correct_label.value)

    var new_element = new_multiple_choice_question_element(form_prefix, choice_label, choice_text, selected)
    solution_choices_list_div.appendChild(new_element)
  }

  window.multiple_choice_qs[form_prefix] = solution_choices

  // Render dynamically-created feather icons
  feather.replace()

  var submit_button = document.getElementById(form_prefix + 'submit')
  submit_button.addEventListener('click', function(event) {
    window.multiple_choice_qs[form_prefix] = get_current_solution_choices(form_prefix)
    hidden_solution_choices.value = JSON.stringify(window.multiple_choice_qs[form_prefix])
    hidden_solution_correct_label.value = correct_solution_choice.innerText
  })
}

function get_current_solution_choices(form_prefix) {
  var solution_choices_list_div = document.getElementById(form_prefix + 'solution_choices_list_div')
  var solution_choices = []
  var i

  var choice_label_divs = solution_choices_list_div.querySelectorAll('span.solution_choice_label');
  for (i = 0; i < choice_label_divs.length; ++i) {
      solution_choices.push({'choice_label': choice_label_divs[i].innerText.trim()})
  }

  var choice_text_divs = solution_choices_list_div.querySelectorAll('input.solution_choice_text');
  for (i = 0; i < choice_text_divs.length; ++i) {
      solution_choices[i].choice_text = choice_text_divs[i].value.trim()
  }

  return solution_choices
}

function new_multiple_choice_question_element(form_prefix, choice_label, choice_text, selected) {
  // Renders something like this:
  // <div class="input-group mb-1">
  //   <div class="input-group-prepend">
  //     <div class="input-group-text">
  //       {{ solution_choice_label }} &nbsp;<input type="radio" name="multiple_choice_radio_group"  onclick="getElementById('{{ form_prefix }}correct_solution_choice').innerText='{{ solution_choice_label }}';">
  //     </div>
  //   </div>
  //   <input type="text" class="form-control" placeholder="Option text" value="{{ solution_choice_text }}">
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
  input_group_text.className = 'solution_choice_label'
  input_group_text.innerHTML = choice_label + ' &nbsp;'
  input_group_text_div.appendChild(input_group_text)

  var radio_button = document.createElement('input')
  radio_button.type = 'radio'
  radio_button.name = 'multiple_choice_radio_group'
  radio_button.checked = selected
  radio_button.className = 'solution_choice_radio'
  radio_button.addEventListener('click', function(event) {
    update_correct_solution_choice(form_prefix, choice_label)
  })
  input_group_text_div.appendChild(radio_button)

  var solution_text_input = document.createElement('input')
  solution_text_input.type = 'text'
  solution_text_input.className = 'solution_choice_text form-control'
  solution_text_input.placeholder = 'Option text'
  solution_text_input.value = choice_text
  input_group.appendChild(solution_text_input)
  update_choice_label_color(solution_text_input, selected)

  var delete_button_div = document.createElement('div')
  delete_button_div.className = 'input-group-append'
  input_group.appendChild(delete_button_div)

  var delete_button = document.createElement('button')
  delete_button.type = 'button'
  delete_button.className = 'btn btn-outline-secondary'
  delete_button.addEventListener('click', function(event) {
    remove_multiple_choice_question(form_prefix, choice_label, input_group)
  })
  delete_button_div.appendChild(delete_button)

  var delete_button_icon = document.createElement('span')
  delete_button_icon.setAttribute('data-feather', 'trash-2')
  delete_button.appendChild(delete_button_icon)

  return input_group
}

function remove_multiple_choice_question(form_prefix, choice_label, choice_element) {
  var solution_choices_list_div = document.getElementById(form_prefix + 'solution_choices_list_div')
  solution_choices_list_div.removeChild(choice_element)

  var solution_choices = window.multiple_choice_qs[form_prefix]
  var i
  for (i = 0; i < solution_choices.length; ++i) {
    if (solution_choices[i].choice_label == choice_label) {
      window.multiple_choice_qs[form_prefix].splice(i, 1)
      break
    }
  }

  // If ordering of choics has changed, update the choice labels
  var choice_label_divs = document.getElementById(form_prefix + 'solution_choices_list_div').querySelectorAll('.solution_choice_label');
  for (i = 0; i < choice_label_divs.length; ++i) {
      choice_label_divs[i].innerHTML = solution_prefix(i) + ' &nbsp;'
  }

  // If the correct choice was removed, reset the correct choice label
  var correct_solution_choice = document.getElementById(form_prefix + 'correct_solution_choice')
  if (correct_solution_choice.innerText == choice_label) {
    correct_solution_choice.innerText = '(Not selected)'
  }
}

function update_correct_solution_choice(form_prefix, choice_label) {
  var correct_solution_choice = document.getElementById(form_prefix + 'correct_solution_choice')
  correct_solution_choice.innerText = choice_label

  var solution_choices_list_div = document.getElementById(form_prefix + 'solution_choices_list_div')
  var choice_radio_inputs = solution_choices_list_div.querySelectorAll('input.solution_choice_radio');
  var choice_text_inputs = solution_choices_list_div.querySelectorAll('input.solution_choice_text');

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

function add_multiple_choice_question(form_prefix, choice_text_input) {
  var curr_solution_choices = window.multiple_choice_qs[form_prefix]
  var new_solution_choice = {'choice_label': solution_prefix(curr_solution_choices.length), 'choice_text': choice_text_input.value}

  var new_element = new_multiple_choice_question_element(form_prefix, new_solution_choice.choice_label, new_solution_choice.choice_text)
  var solution_choices_list_div = document.getElementById(form_prefix + 'solution_choices_list_div')
  solution_choices_list_div.appendChild(new_element)

  choice_text_input.value = ''  // reset the input field for adding new options
  window.multiple_choice_qs[form_prefix].push(new_solution_choice)

  // Render dynamically-created feather icons
  feather.replace()
}

function solution_prefix(index) {
  var choice_labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  return choice_labels[index]
}
