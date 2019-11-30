$(document).ready(function () {
    // # id, . class
    let global_plate_study_id = parseInt(document.getElementById ("this_study_id").innerText.trim());
    //console.log("study ", global_plate_study_id)

    $('#id_plate_reader_file').change(function() {
        upload_plate_reader_file();
    });

    function upload_plate_reader_file() {
        // var charts_name = 'new_charts';
        // var charts_name = 'charts';

        // var dynamic_quality = $.extend(true, {}, dynamic_quality_current, dynamic_quality_new);
        let data = {
            // function in ajax file
            call: 'fetch_upload_plate_reader_data_file',
            study: global_plate_study_id,
            //criteria: JSON.stringify(window.GROUPING.group_criteria),
            //post_filter: JSON.stringify(window.GROUPING.current_post_filter),
            //csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        //    dynamic_quality: JSON.stringify(dynamic_quality),
        //    include_table: include_table
        };
        //console.log('data a ',data)
        //prints: {call: "fetch_upload_plate_reader_data_file", study: 293, csrfmiddlewaretoken: "iTSoDTCLTa9gBdDMHJEBCKZqWgUulA7uVN7SB3V3ykJ9b45svXunzX0IaSmw3izG"}

       // window.CHARTS.global_options = window.CHARTS.prepare_chart_options();
        //var options = window.CHARTS.global_options.ajax_data;

         //data = $.extend(data, options);

        var serializedData = $('form').serializeArray();
        //console.log("se ", serializedData)
        //print: se  (2) [{…}, {…}]
        var formData = new FormData();
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
            //console.log('name ', field.name, '  value ', field.value)
            //prints these:
            //name  csrfmiddlewaretoken   value  hGvYgNrnjQkbGwq3eA1T0WswGWs8bLCzUAKseXKFY0U4gnSJ2ORFX9tOUyUaTt4L
            //name  reason_for_flag   value
        });
        formData.append('plate_reader_file', $('#id_plate_reader_file')[0].files[0]);
        //console.log('formdata ', formData)
        // print: formdata FormData {}
        $.each(data, function(index, contents) {
            formData.append(index, contents);
            console.log('index, contents  ', index, ", ", contents)
            //print:
            // index, contents   call ,  fetch_upload_plate_reader_data_file
            // index, contents   study ,  293
            // index, contents   csrfmiddlewaretoken ,  iTSoDTCLTa9gBdDMHJEBCKZqWgUulA7uVN7SB3V3ykJ9b45svXunzX0IaSmw3izG
        });

        console.log("formData");
        for (var key of formData.keys()) {
            console.log("key: ", key)
        }
        for (var value of formData.values()) {
            console.log("value: ", value)
        }

        if ($("#id_plate_reader_file")[0].files[0]) {
            //console.log("files by name ", ($("#id_plate_reader_file")[0].files[0]))
            //print: files by name
            //       File {name: "test.txt", lastModified: 1573416658647, lastModifiedDate: Sun Nov 10 2019 15:10:58 GMT-0500 (Eastern Standard Time), webkitRelativePath: "", size: 71, …}
            // Show spinner
            // window.spinner.spin(
            //     document.getElementById("spinner")
            // );
            //console.log("formdata", formData)
            //print: formdata FormData {}
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",

                //one of these next three caused
                //"<p>CSRF verification failed. Request aborted.</p>"
                cache: false,
                contentType: false,
                processData: false,

                //Change these and an error results
                data: formData,
                // data: data,
                success: function (json) {
                    window.spinner.stop();
                    let exist = true;
                    process_data(json, exist);
                    //plateLabels("adding");
                    //console.log(json);
                    if (json.errors) {
                        // Display errors
                        alert(json.errors);
                        // Remove file selection
                        $('#id_plate_reader_file').val('');
                    }
                    else {
                        alert('Success!' +
                            '\n\nPlease note that changes will not be made until you press the "Submit" button at the bottom of the page.');
                    }
                },
                error: function (xhr, errmsg, err) {
                    window.spinner.stop();
                    alert('An unknown error has occurred. \nIf you have the file open, you may need to close it.');
                    console.log(xhr.status + ": " + xhr.responseText);
                    // Remove file selection
                    $('#id_plate_reader_file').val('');
                }
            });
        }
    }

    let process_data = function (json, exist) {
    // let mi_list = json.mi_list;
    // // make the parallel list for easy search and find
    // global_plate_imatrix_item_id = [];
    // global_plate_imatrix_item_name = [];
    // global_plate_imatrix_item_row_index = [];
    // global_plate_imatrix_item_column_index = [];
    // global_plate_imatrix_item_row_column_index = [];

    // $.each(mi_list, function(index, each) {
        //console.log("each ", each)
        // global_plate_imatrix_item_id.push(each.matrix_item_id);
        // global_plate_imatrix_item_name.push(each.matrix_item_name);
        // global_plate_imatrix_item_row_index.push(each.matrix_item_row_index);
        // global_plate_imatrix_item_column_index.push(each.matrix_item_column_index);
        // global_plate_imatrix_item_row_column_index.push(each.matrix_item_row_index.toString()+"-"+each.matrix_item_column_index.toString());
    //});
    //console.log("matrix items: ", global_plate_imatrix_item_row_column_index)
    };

});


