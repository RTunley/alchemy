function validate_categories(course_id){
  console.log("Made it to validate_categories!")
  var category_ids = []
  var category_names = []
  var weightings = []
  var categories = []
  var i = 0
  $('#category-form-table').find('input').each(function(){
    if (i % 3 == 0) {
      category_ids.push(parseInt(this.value))
    } else if (i % 3 == 1) {
      category_names.push(this.value)
    } else {
      weightings.push(parseFloat(this.value))
    }
    categories.push(this.value)
    i++
  })
  for (i=0; i<category_names.length; i++){
    var cat_name_element = document.getElementById('category_'+ i)
    var weighting_element = document.getElementById('weighting_'+ i)
    cat_name_element.classList.remove('is-invalid')
    weighting_element.classList.remove('is-invalid')
  }
  if (!validate_form(category_names, weightings)) {
    return false
  }
  console.log(categories)
  $.ajax({
    type: 'POST',
    url: '/course/' + course_id + '/edit_categories',
    data: JSON.stringify({
      course_id: course_id,
      category_ids: category_ids,
      categories: categories,
    }),
    contentType: 'application/json',
  })
  return true
}

function validate_form(category_names, weightings){
  if (!check_valid_weightings(weightings)
      || !check_weightings_sum(weightings)
      || !no_double_names(category_names)) {
    return false
  }
  return true
}

function no_double_names(name_list){
  var map = {}
  for(var i=0; i<name_list.length; i++){
    if(map[name_list[i]]){
      var input = document.getElementById('category_'+ i)
      var feedback = document.getElementById('category_error_'+i)
      feedback.innerHTML = 'Assessment Categories must have distinct names.'
      input.classList.add('is-invalid')
      return false
    }
    map[name_list[i]] = true
  }
  return true
}

function check_weightings_sum(weightings_list){
  var i
  var weighting_sum = 0
  for (i=0; i<weightings_list.length; i++) {
    weighting_sum += weightings_list[i]
    if (weighting_sum > 100){
      var input = document.getElementById('weighting_'+i)
      console.log("Indexed Inputs: ", input)
      input.classList.add('is-invalid')
      var feedback = document.getElementById('weighting_error_'+i)
      feedback.innerHTML = 'Weightings must sum to 100%'
      return false
    }
  }
  if (weighting_sum <100){
    var input = document.getElementById('weighting_'+(weightings_list.length-1))
    input.classList.add('is-invalid')
    var feedback = document.getElementById('weighting_error_'+(weightings_list.length-1))
    feedback.innerHTML = 'Weightings must sum to 100%'
    return false
  }
  return true
}

function check_valid_weightings(weightings_list){
  var i
  for (i=0; i<weightings_list.length; i++) {
    if ( isNaN(weightings_list[i])){
      var input = document.getElementById('weighting_'+i)
      input.classList.add('is-invalid')
      var feedback = document.getElementById('weighting_error_'+i)
      feedback.innerHTML = 'Weightings must be a number.'
      return false
    }
  }
  return true
}

function new_hidden_id_field(){
  var id_field = document.createElement('INPUT')
  id_field.type = 'integer'
  id_field.value = 0
  return id_field
}

function new_category_field(){
  var grade_field = document.createElement('INPUT')
  grade_field.type = 'text'
  grade_field.className = 'form-control'
  grade_field.placeholder = 'Category'
  grade_field.setAttribute('required', '')
  return grade_field
}

function new_weighting_field(){
  var lb_field = document.createElement('INPUT')
  lb_field.type = 'float'
  lb_field.className = 'form-control'
  lb_field.placeholder = 'Weighting'
  lb_field.setAttribute('required', '')
  return lb_field
}

function new_delete_button(){
  var del_btn = document.createElement('A')
  del_btn.className = 'btn btn-link'
  del_btn.addEventListener('click', function() {
    remove_cat_field_row($(this))
  })
  del_btn.setAttribute('aria-label','Delete Category')
  return del_btn
}

function create_trash_icon(){
  var span = document.createElement('SPAN')
  span.setAttribute('data-feather', 'trash-2')
  return span
}

function insert_cat_field_row(){
  var table = document.getElementById('category-form-table')
  var row = table.insertRow(-1)
  var cell0 = row.insertCell(0)
  var cell1 = row.insertCell(1)
  var cell2 = row.insertCell(2)
  var cell3 = row.insertCell(3)
  cell0.appendChild(new_hidden_id_field())
  cell0.style = "display:none"
  cell1.appendChild(new_category_field())
  cell2.appendChild(new_weighting_field())
  var btn = new_delete_button()
  var span = create_trash_icon()
  cell3.appendChild(btn)
  btn.appendChild(span)
  feather.replace()
}

function remove_cat_field_row(del_btn){
  var table = document.getElementById('category-form-table')
  var index = del_btn.closest('tr').index()
  table.deleteRow(index)
}
