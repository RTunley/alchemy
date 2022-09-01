function validate_grade_levels(course_id){
  var lower_bounds = []
  var grades = []
  var grade_levels = []
  var i = 0
  $('#grade-form-table').find('input').each(function(){
    if (i % 2 == 0) {
      grades.push(this.value)
    } else {
      lower_bounds.push(parseInt(this.value))
    }
    grade_levels.push(this.value)
    i++
  })
  for (i=0; i<grades.length; i++){
    var grade_element = document.getElementById('grade_level_'+ i)
    var lower_bound_element = document.getElementById('lower_bound_'+ i)
    grade_element.classList.remove('is-invalid')
    lower_bound_element.classList.remove('is-invalid')
  }
  if (!validate_form_success(lower_bounds, grades)) {
    return false
  }
  $.ajax({
    type: 'POST',
    url: '/course/' + course_id + '/edit_grade_levels',
    data: JSON.stringify({
      course_id: course_id,
      grade_levels: grade_levels,
    }),
    contentType: 'application/json',
  })
  document.getElementById('grade-level-form').submit();
  return true
}

function validate_form_success(lower_bounds, grades){
  if ( !lower_bounds_ok(lower_bounds)
    || !highest_bound_ok(lower_bounds)
    || !lowest_bound_ok(lower_bounds)
    || !no_double_grades(grades)
    ){
      return false
    }
  return true
  }

function no_double_grades(grades_list){
  var map = {}
  for(var i=0; i<grades_list.length; i++){
    if(map[grades_list[i]]){
      var input = document.getElementById('grade_level_'+ i)
      var feedback = document.getElementById('grade-error-'+i)
      feedback.innerHTML = 'Grade levels must have distinct Grades.'
      input.classList.add('is-invalid')
      return false
    }
    map[grades_list[i]] = true
  }
  return true
}

function highest_bound_ok(lower_bounds){
  if (lower_bounds[0]>100){
    var input = document.getElementById('lower_bound_'+ 0)
    input.classList.add('is-invalid')
    var feedback = document.getElementById('bound-error-'+'0')
    feedback.innerHTML = 'Please provide a lower bound that is less than 100.'
    return false
  }
  return true
}

function lowest_bound_ok(lower_bounds){
  if (lower_bounds[lower_bounds.length - 1] != 0){
    var index = lower_bounds.length - 1
    var input = document.getElementById('lower_bound_'+index)
    input.classList.add('is-invalid')
    var feedback = document.getElementById('bound-error-'+index)
    feedback.innerHTML = 'The lower bound for the lowest grade must be 0.'
    return false
  }
  return true
}

function lower_bounds_ok(lower_bounds){
  var i
  for (i=0; i<lower_bounds.length; i++) {
    if (lower_bounds[i]<0 || lower_bounds[i] <= lower_bounds[i+1]){
      var input = document.getElementById('lower_bound_'+i)
      input.classList.add('is-invalid')
      var feedback = document.getElementById('bound-error-'+i)
      feedback.innerHTML = 'Please provide a lower bound that is higher than the next lower bound.'
      return false
    }
  }
  return true
}

function new_grade_field(){
  var grade_field = document.createElement('INPUT')
  grade_field.type = 'text'
  grade_field.className = 'form-control'
  grade_field.placeholder = 'Grade Level'
  grade_field.setAttribute('required', '')
  return grade_field
}

function new_lbound_field(){
  var lb_field = document.createElement('INPUT')
  lb_field.type = 'integer'
  lb_field.className = 'form-control'
  lb_field.placeholder = 'Lower Bound'
  lb_field.setAttribute('required', '')
  return lb_field
}

function new_delete_button(){
  var del_btn = document.createElement('A')
  del_btn.className = 'btn btn-link'
  del_btn.addEventListener('click', function() {
    remove_field_row($(this))
  })
  del_btn.setAttribute('aria-label','Delete Grade Level')
  return del_btn
}

function create_trash_icon(){
  var span = document.createElement('SPAN')
  span.setAttribute('data-feather', 'trash-2')
  return span
}

function insert_field_row(){
  var table = document.getElementById('grade-form-table')
  var row = table.insertRow(-1)
  var cell0 = row.insertCell(0)
  var cell1 = row.insertCell(1)
  var cell2 = row.insertCell(2)
  cell0.appendChild(new_grade_field())
  cell1.appendChild(new_lbound_field())
  var btn = new_delete_button()
  var span = create_trash_icon()
  cell2.appendChild(btn)
  btn.appendChild(span)
  feather.replace()
}

function remove_field_row(del_btn){
  var table = document.getElementById('grade-form-table')
  var index = del_btn.closest('tr').index()
  table.deleteRow(index)
}
