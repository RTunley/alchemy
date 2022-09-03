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
