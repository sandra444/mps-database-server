$(document).ready(function () {
    // Load core chart package
    //-google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    // google.charts.setOnLoadCallback(get_readouts);

    window.GROUPING.refresh_function = refresh_current;

    function refresh_current() {
        // Not currently used
        // get_readouts();

        if ($('#id_bulk_file').val()) {
            validate_bulk_file();
        }
    }

    var study_id = Math.floor(window.location.href.split('/')[5]);

    //-window.CHARTS.call = 'validate_data_file';
    //-window.CHARTS.study_id = study_id;

    // PROCESS GET PARAMS INITIALLY
    window.GROUPING.process_get_params();

    // PROCESS GET PARAMS INITIALLY
    // window.GROUPING.process_get_params();
    // window.GROUPING.generate_get_params();

    // Not currently used
    function get_readouts() {

        var data = {
            call: 'fetch_data_points',
            study: study_id,
            criteria: JSON.stringify(window.GROUPING.group_criteria),
            post_filter: JSON.stringify(window.GROUPING.current_post_filter),
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        };

        window.CHARTS.global_options = window.CHARTS.prepare_chart_options();
        var options = window.CHARTS.global_options.ajax_data;

        data = $.extend(data, options);

        // Show spinner
        window.spinner.spin(
            document.getElementById("spinner")
        );

        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: data,
            success: function (json) {
                // Stop spinner
                window.spinner.stop();

                window.CHARTS.prepare_side_by_side_charts(json, charts_name);
                window.CHARTS.make_charts(json, charts_name);
            },
            error: function (xhr, errmsg, err) {
                // Stop spinner
                window.spinner.stop();

                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Please note that bulk upload does not currently allow changing QC or notes
    // Before permitting this, ensure that the update_number numbers are accurate!
    function validate_bulk_file() {
        // var charts_name = 'new_charts';
        var charts_name = 'charts';

        // var dynamic_quality = $.extend(true, {}, dynamic_quality_current, dynamic_quality_new);

        var data = {
            call: 'validate_data_file',
            study: study_id,
            criteria: JSON.stringify(window.GROUPING.group_criteria),
            post_filter: JSON.stringify(window.GROUPING.current_post_filter),
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        //    dynamic_quality: JSON.stringify(dynamic_quality),
        //    include_table: include_table
        };

        window.CHARTS.global_options = window.CHARTS.prepare_chart_options();
        var options = window.CHARTS.global_options.ajax_data;

        data = $.extend(data, options);

        var serializedData = $('form').serializeArray();
        var formData = new FormData();
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
        });
        formData.append('bulk_file', $('#id_bulk_file')[0].files[0]);

        $.each(data, function(index, contents) {
            formData.append(index, contents);
        });

        if ($("#id_bulk_file")[0].files[0]) {
            // Show spinner
            window.spinner.spin(
                document.getElementById("spinner")
            );

            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                cache: false,
                contentType: false,
                processData: false,
                data: formData,
                success: function (json) {
                    //sck
                    console.log(formData, json)
                    // Stop spinner
                    window.spinner.stop();

                    // console.log(json);
                    if (json.errors) {
                        // Display errors
                        alert(json.errors);
                        // Remove file selection
                        $('#id_bulk_file').val('');
                        // $('#new_charts').empty();
                        $('#charts').empty();
                    }
                    else {
                        // TODO TODO TODO ALERTS ARE EVIL
                        alert('Success! Please see "New Chip Data" below for preview.' +
                            '\n\nPlease note that changes will not be made until you press the "Submit" button at the bottom of the page.');

                        if (json.number_of_conflicting_entries) {
                            alert(
                                '***Submitting this file will replace ' + json.number_of_conflicting_entries + ' point(s).***' +
                                '\n\nPlease note that changes will not be made until you press the "Submit" button at the bottom of the page.');
                        }

                        window.CHARTS.prepare_side_by_side_charts(json.readout_data, charts_name);
                        window.CHARTS.make_charts(json.readout_data, charts_name);

                        // CRUDE: SIMPLY UNBIND ALL CHART CONTAINER EVENTS
                        $(document).off('.chart_context');
                    }
                },
                error: function (xhr, errmsg, err) {
                    // Stop spinner
                    window.spinner.stop();

                    alert('An unknown error has occurred. \nIf you have the file open, you may need to close it.');
                    console.log(xhr.status + ": " + xhr.responseText);
                    // Remove file selection
                    $('#id_bulk_file').val('');
                    //$('#new_charts').empty();
                    $('#charts').empty();
                }
            });
        }
    }

    // Validate file if file selected
    $('#id_bulk_file').change(function() {
        // sck for raw_plate
        if ($('input[name=upload_type]:checked').val() === "raw_plate") {
            // #TODO
            console.log("run the checks for the plate reader input...talk with Luke about approach so don't get crossed")
        } else {
            validate_bulk_file();
        }
    });

    // NOTE: FOR NOW FILTERING WILL BE FORBIDDEN
    // CRUDE: JUST DISABLE THE BUTTONS
    $('.post-filter-spawn').html('X').attr('disabled', 'disabled');

    // NOTE MAGIC STRING HERE
    // Commented out for now, will just have preview (not current data to avoid ambiguity with only one sidebar)
/*
    $('#new_chartschart_options').find('input').change(function() {
        validate_bulk_file();
    });

    // NOTE MAGIC STRING HERE
    $('#current_chartschart_options').find('input').change(function() {
        get_readouts();
    });
*/

    //sck for raw_plate
    $('#matrix_items_table').DataTable({
        "iDisplayLength": 25,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[2, "asc"]],
    });
    // test data
    var MOUNTAINS = [
        {"1":"chip1","2":1,"3":"my treatment 1"},
        {"1":"chip2","2":2,"3":"my treatment 2"},
        {"1":"chip3","2":3,"3":"my treatment 3"}
    ];

    var HEADERMOUNTIANS = ["A","B","C"];

    $('input[type="radio"]').click(function() {
        var inputValue = $(this).attr("value");
        var inputName = $(this).attr("name");
        console.log("x", inputName);
        console.log("y", inputValue);
        if (inputName == "upload_type") {
            if (inputValue == "raw_plate") {
                $('.supporting-data').addClass('hidden');
                $('.mif-c').addClass('hidden');
                $('.raw-plate').removeClass('hidden');
                $('.sample-times').removeClass('hidden');
                //buildTableChips(MOUNTAINS);
                $('#tablecellsselection').empty();
                //providePlateOptions(standard_well_plates);
                //addFormFromForms(action);
                //set quirky defaults
                $('.new-plate-map').removeClass('hidden');
            } else if (inputValue == "supporting_data") {
                $('.mif-c').addClass('hidden');
                $('.raw-plate').addClass('hidden');
                $('.supporting-data').removeClass('hidden');
            } else {
                // mif_c
                $('.raw-plate').addClass('hidden');
                $('.supporting-data').addClass('hidden');
                $('.mif-c').removeClass('hidden');
            }
        } else if (inputName == "plate_map_type_option") {
            //console.log(inputName);
            //console.log(inputValue);
            //sample empty matrix
            if (inputValue == "sample") {
                console.log("a", inputName);
                console.log("b", inputValue);
                $('.matrix-times').addClass('hidden');
                $('.empty-times').addClass('hidden');
                $('.sample-times').removeClass('hidden');
                $('.overwrite-plate').removeClass('hidden');
            } else if (inputValue == "empty") {
                console.log("c", inputName)
                console.log("d", inputValue)
                $('.sample-times').addClass('hidden');
                $('.matrix-times').addClass('hidden');
                $('.empty-times').removeClass('hidden');
                $('.overwrite-plate').addClass('hidden');
            } else {
                // matrix
                console.log("e", inputName);
                console.log("f", inputValue);
                $('.empty-times').addClass('hidden');
                $('.sample-times').addClass('hidden');
                $('.matrix-times').removeClass('hidden');
                $('.overwrite-plate').addClass('hidden');
            }
        } else if (inputName == "plate_map_new_overwrite") {
            //console.log(inputValue);
            if (inputValue == "new_map") {
                $('.new-plate-map').removeClass('hidden');
            } else {
                $('.new-plate-map').addClass('hidden');
            }
        } else {
            var passme = true;

        }
    //console.log($('input[name=upload_type]:checked').val());
    });


/*    function buildTableChips(data) {
        //var table = document.createElement("table");
        //table.className="gridtable";
        $('#tablecellsselection').empty();
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        var headRow = document.createElement("tr");
        HEADERMOUNTIANS.forEach(function(el) {
          var th=document.createElement("th");
          th.appendChild(document.createTextNode(el));
          headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        tablecellsselection.appendChild(thead);
        data.forEach(function(el) {
            console.log(el)
          var tr = document.createElement("tr");
          for (var o in el) {
            var td = document.createElement("td");
            $(td).attr('data-test', o);
            td.appendChild(document.createTextNode(el[o]))
            tr.appendChild(td);
          }
          tbody.appendChild(tr);
        });
        tablecellsselection.appendChild(tbody);
        return tablecellsselection;
    }*/

    //var HEADERWELLS = ["A","B"];
    //var standard_well_plates = $('#standard_well_plates');
    //sck get plate info for basic plates
/*    function providePlateOptions(data) {
         console.log(data);
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        var headRow = document.createElement("tr");
        HEADERWELLS.forEach(function(el) {
          var th=document.createElement("th");
          th.appendChild(document.createTextNode(el));
          headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        tablestandardwellplates.appendChild(thead);
        //data.forEach(function(el) {
          var tr = document.createElement("tr");
        //  for (var o in el) {
            var td = document.createElement("td");
            td.appendChild(document.createTextNode(data)
            //td.appendChild(document.createTextNode(el[o]))
            tr.appendChild(td);
          }
          tbody.appendChild(tr);
        });
        tablestandardwellplates.appendChild(tbody);
        return tablestandardwellplates;
    }*/

    // note: form.well_plate_size referenced list this in js
    // this will only happen if the user selected to start from an empty plate and then picked the plate size
    $("#id_well_plate_size").change(function() {
        var inputValue = $(this).val()
        console.log("what input value top of plate size ", inputValue);
        $("input[name=selectedplatesize]:text").val(inputValue);
        // want to make an empty plate layout of the size selected
        var data_packed =[]
        var row_labels = []
        var col_labels = []
        var row_contents = []
        var row_labels_all = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
        var col_labels_all = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24']
        console.log("start of plate size ", inputValue);
        $("input[name=enteredplatename]:text").val(inputValue);

        if (inputValue == '24') {
            console.log("24 ", inputValue)
            row_labels = row_labels_all.slice(0,4) //['A','B','C','D']
            col_labels = col_labels_all.slice(0,6) //['1','2','3','4','5','6']
        } else if (inputValue == '96') {
            console.log("96 ", inputValue)
            row_labels = row_labels_all.slice(0,8) //['A','B','C','D','E','F','G','H']
            col_labels = col_labels_all.slice(0,12) //['1','2','3','4','5','6','7','8','9','10','11','12']
        } else {
            // '384'
            console.log("384 ", inputValue)
            row_labels = row_labels_all
            col_labels = col_labels_all
        }
        console.log(col_labels)
        console.log(row_labels)
        row_labels.forEach(function(rl) {
            var row_dict = {}
            // add for the row label
            row_dict['0'] = rl
            console.log(rl)
            col_labels.forEach(function(cl) {
                console.log("col ",cl)
                // this is working 20190917
                row_dict[cl] = rl + " " + cl
                console.log("row dict ", row_dict[cl])
            })
            console.log("row dict should be all ", row_dict)
            row_contents.push(row_dict);
        });

        console.log(row_contents)
        // add a label to the front of column labels to hold the row labels
        data_packed = [['Plate'].concat(col_labels), row_contents, row_labels]
        buildTableChips(data_packed)
        });

    function buildTableChips(data) {
        // col_labels, row_labels, row_contents
        console.log("data", data)
        $('#tablecellsselection').empty();
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        var headRow = document.createElement("tr");
        console.log("what's here")
        console.log("data0", data[0])
        console.log("data1", data[1])
        console.log("data2", data[2])
        // column headers
        data[0].forEach(function(el) {
            var th=document.createElement("th");
            th.appendChild(document.createTextNode(el));
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        tablecellsselection.appendChild(thead);
        // add the content, and add a place for sample location and sample time, with class for show/hide
        var idx = 0
        data[1].forEach(function(el) {
            var trc = document.createElement("tr");
            var trl = document.createElement("tr");
            var trt = document.createElement("tr");
            // build content row
            for (var o in el) {
                if (o == 0) {
                    //content
                    var tdc = document.createElement("th");
                    $(tdc).attr('data-col', o);
                    $(tdc).attr('data-row', el[0]);
                    $(tdc).addClass('plate-content');
                    tdc.appendChild(document.createTextNode(el[o]));
                    trc.appendChild(tdc);
                    // location
                    var tdl = document.createElement("th");
                    $(tdl).attr('data-col', o);
                    $(tdl).attr('data-row', el[0]);
                    $(tdl).addClass('plate-location hidden');
                    tdl.appendChild(document.createTextNode(el[o]+" (location)"));
                    trl.appendChild(tdl);
                    // time
                    var tdt = document.createElement("th");
                    $(tdt).attr('data-col', o);
                    $(tdt).attr('data-row', el[0]);
                    $(tdt).addClass('plate-time hidden');
                    tdt.appendChild(document.createTextNode(el[o]+" (time)"));
                    trt.appendChild(tdt);
                } else {
                    //content
                    var tdc = document.createElement("td");
                    $(tdc).attr('data-col', o);
                    $(tdc).attr('data-row', el[0]);
                    $(tdc).addClass('plate-content');
                    tdc.appendChild(document.createTextNode(""));
                    trc.appendChild(tdc);
                    // location
                    var tdl = document.createElement("td");
                    $(tdl).attr('data-col', o);
                    $(tdl).attr('data-row', el[0]);
                    $(tdl).addClass('plate-location hidden');
                    tdl.appendChild(document.createTextNode(""));
                    trl.appendChild(tdl);
                    // time
                    var tdt = document.createElement("td");
                    $(tdt).attr('data-col', o);
                    $(tdt).attr('data-row', el[0]);
                    $(tdt).addClass('plate-time hidden');
                    tdt.appendChild(document.createTextNode(""));
                    trt.appendChild(tdt);
                }
            }
            tbody.appendChild(trc);
            tbody.appendChild(trl);
            tbody.appendChild(trt);
        });
        tablecellsselection.appendChild(tbody);
        return tablecellsselection;
    }

   $('#show_on_plate_map1').change(function() {
       console.log("here1");
       if ($(this).is(':checked')) {
            $('.plate-content').removeClass('hidden');
       } else {
            $('.plate-content').addClass('hidden');
       }
   });
   $('#show_on_plate_map2').change(function() {
       console.log("here2");
       if ($(this).is(':checked')) {
            $('.plate-location').removeClass('hidden');
       } else {
            $('.plate-location').addClass('hidden');
       }
   });
   $('#show_on_plate_map3').change(function() {
       console.log("here3");
       if ($(this).is(':checked')) {
            $('.plate-time').removeClass('hidden');
       } else {
            $('.plate-time').addClass('hidden');
       }
   });


    $("#id_well_plate_new_name").focusout(function() {
        var inputValue = $(this).val()
        console.log("plate name ", inputValue);
        $("input[name=enteredplatename]:text").val(inputValue);
    });

    $("#id_well_plate_size").change(function() {
        var inputValue = $(this).val()
        console.log("what input value top of plate size ", inputValue);
    });

    $("#id_matrix_item_list").change(function() {
        var inputValue = $(this).text()
        console.log("what input matrix item ", inputValue);
    });

    $("#id_model_location_list").change(function() {
        var inputValue = $(this).text()
        console.log("what location ", inputValue);
    });

    $("#id_sample_time_entry").change(function() {
        var inputValue = $(this).val()
        console.log("on change ", inputValue);
    });
    $("#id_sample_time_entry").focusout(function() {
        var inputValue = $(this).val()
        console.log("on exit ", inputValue);
    });

    function changeSelected() {
        $('.ui-selected').each(function() {
            //<td data-col="4" data-row="A" class="plate-location ui-selectee">A 4 (location)</td>
            console.log($(this));
            console.log($(this).class);
            console.log($(this).text());
            console.log($(this).attr('data-col'));
            console.log($(this).attr('data-row'));
            //<td data-col="3" data-row="B" class="plate-location">B 3 (location)</td>
            if ($(this).hasClass("plate-content")) {
                console.log("content ",$("#id_matrix_item_list").text());
                //$(this).text = $("#id_matrix_item_list").text();
                //$("input[name=enteredplatename]:text").val(inputValue)
                //$(this).text("new content");
                $(this).text($("#id_matrix_item_list").text());
            } else if ($(this).hasClass("plate-location")) {
                console.log("location ",$("#id_model_location_list").text());
                //$(this).text = $("#id_model_location_list").text();
                //$(this).text("new location");
                $(this).text($("#id_model_location_list").text());
            } else {
                // plate-time
                console.log("time ",$("#id_sample_time_entry").val());
                //$(this).text = $("id_sample_time_entry").text();
                //$(this).text("new time");
                console.log($("#id_sample_time_entry").val());
                $(this).text($("#id_sample_time_entry").val());
            }
        });
    }

    $('#tablecellsselection').selectable({
        // SUBJECT TO CHANGE: WARNING!
        filter: 'td',
        distance: 1,
        stop: changeSelected
    });


});
