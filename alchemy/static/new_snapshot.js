function validate_new_snapshot(school_id){
  var input_element = document.getElementById("snapshot_name_input")
  var snapshot_name = input_element.value
  $.ajax({
    type: 'POST',
    url: '/school/' + school_id + '/new_snapshot',
    data: JSON.stringify({
      school_id: school_id,
      snapshot_name: snapshot_name
    }),
    contentType: 'application/json',
  })
  document.getElementById('new-snapshot-form').submit();
  return true
}
