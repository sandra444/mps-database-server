// This script allows previews to be shown for bulk uploads
// CURRENTLY ONLY CHIP PREVIEWS ARE SHOWN
// TODO CONSOLIDATE CODE WITH ASSAYSTUDY SUMMARY (DRY)
$(document).ready(function () {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
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

    window.CHARTS.call = 'validate_data_file';
    window.CHARTS.study_id = study_id;

    // PROCESS GET PARAMS INITIALLY
    window.GROUPING.process_get_params();

    // PROCESS GET PARAMS INITIALLY
    // window.GROUPING.process_get_params();
    // window.GROUPING.generate_get_params();

    // Not currently used
    function get_readouts() {
        var charts_name = 'current_charts';

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
                buildTableChips(MOUNTAINS);
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
            } else if (inputValue == "empty") {
                console.log("c", inputName)
                console.log("d", inputValue)
                $('.sample-times').addClass('hidden');
                $('.matrix-times').addClass('hidden');
                $('.empty-times').removeClass('hidden');
            } else {
                // matrix
                console.log("e", inputName);
                console.log("f", inputValue);
                $('.empty-times').addClass('hidden');
                $('.sample-times').addClass('hidden');
                $('.matrix-times').removeClass('hidden');
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


    function buildTableChips(data) {
        //var table = document.createElement("table");
        //table.className="gridtable";
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
            td.appendChild(document.createTextNode(el[o]))
            tr.appendChild(td);
          }
          tbody.appendChild(tr);
        });
        tablecellsselection.appendChild(tbody);
        return tablecellsselection;
    }



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

    $(".select-plate-size").change(function() {
        var inputValue = $(this).val()
        console.log("s", inputValue);
        $("input[name=testingme]:text").val(inputValue);

    });

});
