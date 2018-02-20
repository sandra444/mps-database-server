// TODO This script does many things which will not be necessary on the frontend
// TODO Perhaps a separate script will be made for the front (to avoid AJAX and so on)
// This script provides the means to make an assay layout
// TODO NEEDS TO BE REFACTORED
$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');
    var device = $('#id_device');
    // Only valid on frontend
    var action = $('#id_action');

    // TODO REMOVE SOON: SLOPPY BUT EXPEDIENT WAY TO ADD CLIENT VALIDATION
    $('#id_layout_name').attr('required', true);
    device.attr('required', true);

    function get_well_type_selector() {
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_well_types',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
            },
            success: function (json) {
                create_well_type_selector(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

        function create_well_type_selector(data) {
            var select = $('<select>')
                .attr('id', 'welltype')
                .appendTo('#well_type_div')
                .append($('<option>')
                    .css('background-color','white')
                    .attr('value', '')
                    .text('---------'));

            $.each(data, function (id, dictionary) {
                var name = dictionary.name;
                var color = dictionary.color;
                select.append($('<option>')
                    .attr('value', id)
                    // Arbitrary attribute for color (avoid excessive AJAX CALL)
                    .attr('data-color', color)
                    .text(name)
                    .css('background-color', color));
            });

            // this is to add a new well type
    //        select.after($('<a href="/admin/assays/assaywelltype/add/" ' +
    //            'class="add-another" id="add_welltype" ' +
    //            'onclick="return showAddAnotherPopup(this);"> ' +
    //            '<img src="/static/admin/img/icon_addlink.gif" width="10" ' +
    //            'height="10" alt="Add Another"></a>'));
        }
    }


    // Add options for admin interface
    function add_options() {
        // WARNING WARNING COPY PASTED LEGACY CODE
        alert('Modifying assay layouts is not currently available in the admin, sorry.');
        return;

        if (!$('#id_locked').prop('checked')) {
            // add compound and cell sample search
            var controls = $('<div>').attr('id', 'controls');

            // action
            controls.append($('<div class="form-row field-action">' +
                '<label for="id_action">Action:</label><select id="id_action" name="action">' +
                '<option value="" selected="selected">---------</option>' +
                '<option value="type">Set well type</option>' +
                '<option value="timepoint">Set time point</option>' +
                '<option value="compound">Add compound</option>' +
                '<option value="add-label">Add label</option>' +
                '<option value="clear">Clear contents</option>' +
                '</select></div>'));

            // type
            controls.append($('<div id="well_type_div" class="form-row field-action">' +
                '<label for="id_type">Well Type:</label></div>'));

            // Well Types are collected using an AJAX call because they are subject to change
            // This particular call will tack it on to the id "well_type_div" (subject to change)
            get_well_type_selector();

            // timepoint
            controls.append($('<div class="form-row field-timepoint"><ul class="control_list">' +
                '<li><div class="field-box"><label for="timepoint">Timepoint:</label>' +
                '<input id="id_timepoint" maxlength="6" name="timepoint" type="number" step="any" value="0">' +
                '<select id="id_timeunit" name="concentration_unit">' +
                '<option value="1" selected="selected">min</option>' +
                '<option value="60">hour</option>' +
                '<option value="1440">days</option>' +
                '<option value="10080">weeks</option>' +
                '<option value="43800">months</option>' +
                '<option value="525600">years</option>' +
                '</select></div></li>' +
                '<li><div class="field-box"><label for="tpincr">Increment:</label><input id="id_tpincr" maxlength="6" name="tpincr" type="number" step="any" value="0"></div></li>' +
                '<li><input id="id_tphowtoincr" type="radio" name="tphowtoincr" value="add" checked="">     Add</li>' +
                '<li><input id="id_tphowtoincr" type="radio" name="tphowtoincr" value="multiply">     Multiply</li>' +
                '</ul></div>'));

            /*

             Compounds

             Option 1 is mM (millimolar)
             Option 2 is μM (micromolar)
             Option 3 is nM (nanomolar)

             */

            controls.append($('<div class="form-row field-compound"><ul class="control_list">' +
                '<li><div class="field-box"><label for="id_compound">Compound:</label>' +
                '<input class="vForeignKeyRawIdAdminField" id="id_compound" name="compound" type="text" value="">' +
                '<a href="/admin/compounds/compound/?t=id" class="related-lookup" id="lookup_id_compound" onclick="return showRelatedObjectLookupPopup(this);"> ' +
                '<img src="/static/admin/img/selector-search.gif" width="16" height="16" alt="Lookup"></a></div></li>' +
                '<li><div class="field-box"><label for="concentration">Concentration:</label>' +
                '<input id="id_concentration" maxlength="6" name="concentration" type="number" step="any" value="10">' +
                '<select id="id_concentration_unit" name="concentration_uit">' +
                '<option value="1">mM</option>' +
                '<option value="2" selected="selected">μM</option>' +
                '<option value="3">nM</option></select></div></li>' +
                '<li><div class="field-box"><label for="increment">Dilution Factor:</label>' +
                '<input id="id_increment" maxlength="6" name="increment" type="number" step="any" value="0"></div></li>' +
                '<li><input id="id_howtoincr" type="radio" name="howtoincr" value="add" checked="">     Add</li>' +
                '<li><input id="id_howtoincr" type="radio" name="howtoincr" value="multiply">     Multiply</li>' +
                '</ul></div>'));

            // Labels

            controls.append('<div class="form-row"> ' +
                '<label for="label">Label:</label><input id="id_label" name="label" size="150">' +
                '</div>');

            $('fieldset').first().append(controls);
        }
    }

    // Perform an action on the table
    window.LAYOUT.layout_add_content = function() {
        var act = $('#id_action').val();
        // using time to create a unique ID for a cell content
        var date = new Date();
        var time = date.getTime() % 1000000;

        // Avoid global variables like the plague
        var tablecell = undefined;
        var tablecellid = undefined;

        var type_label = undefined;

        if (act == 'type') {
            var well_type = $("#welltype option:selected");
            var text = well_type.text();

            if (text === '---------') {
                alert('Select a well type first.');
                return;
            }

            else {
                var color = well_type.attr('data-color');
                $(".ui-selected").css('background-color', color);
            }

            // for each selected cell/well
            // it updates the contents of the
            var value = well_type.val();
            // var fs = $($('fieldset')[0]);

            $(".ui-selected", this).each(function () {
                tablecell = $(this);
                tablecellid = tablecell.attr('id');
                type_label = $('#' + tablecellid + '_type');
                var wtid = tablecellid + '_type';
                // removes hidden field
                $('#' + wtid).empty();
                // ---- means clear the cell
                if (text === '---------') {
                    type_label.text('');
                }

                else {
                    // creates a hidden input field for the well
                    // value is the type of well
                    type_label.text(text);
                    // APPEND TO DIV IN LIEU OF fieldset
                    type_label.append($('<input>')
                        .attr('type', 'hidden')
                        .attr('name',wtid)
                        .attr('id', wtid)
                        .attr('value', value));
                }
            });

            // modifies cells selected in the layout
//            function set_color(color) {
//                $("#welltype option:selected").css('font-weight', 'bold');
//                $(".ui-selected").css('background-color', color);
//            }
        }

        // TODO NEEDS REFACTOR
        else if (act === 'compound') {
            var compound_id = $('#id_compound').val();

            var how_to_increment = $('#id_howtoincr:checked').val();

            var compound_direction = $('#id_compound_direction:checked').val();

            var concentration_value = parseFloat(
                $('#id_concentration').val()
            );

            var concentration_unit = $('#id_concentration_unit option:selected').text();
            var concentration_unit_id = $('#id_concentration_unit').val();

            var incr = parseFloat($('#id_increment').val());

            if (compound_id === '') {
                alert('Select a compound first.');
            }

            else if (isNaN(concentration_value) || isNaN(incr)) {
                alert('Make sure concentration and increment are valid numbers.')
            }

            else if (concentration_value < 0) {
                alert('Please specify a non-negative number for concentration.')
            }

            else if ((how_to_increment === 'multiply' || how_to_increment === 'divide') && incr < 0) {
                alert('Negative numbers are not permitted.')
            }

            else if (how_to_increment === 'divide' && incr === 0) {
                alert('Please refrain from dividing by zero.');
            }

            else {
                var compound_name = $('#id_compound :selected').text();
                var current_object = $(".ui-selected", this);

                if (compound_direction === 'right_left') {
                    current_object = $($(".ui-selected", this).get().reverse());
                }

                if (compound_name) {
                    current_object.each(function (index, value) {
                        var tablecell = $(this);
                        var tablecellid = tablecell.attr('id');
                        var list = $('#' + tablecellid + '_list');

                        if (list.length) {
                            // Do not remove old instances of this compound
                            // list.find('[compound=' + compound_id + ']').remove();

                            var stamp = time + '_' + index;

                            var result = 0;
                            var concentration = concentration_value;

                            // Add
                            if (how_to_increment === 'add') {
                                result = concentration + (index * incr);
                                if (result >= 0) {
                                    concentration = result;
                                }
                                else {
                                    concentration = 0;
                                }
                            }

                            // Divide
                            else if(how_to_increment === 'divide') {
                                result = concentration / Math.pow(incr, index);
                                if (isFinite(result) && result >= 0) {
                                    concentration = result;
                                }
                                else {
                                    concentration = 0;
                                }
                            }

                            // Subtract
                            else if(how_to_increment === 'subtract') {
                                result = concentration - (index * incr);
                                if (result >= 0) {
                                    concentration = result;
                                }
                                else {
                                    concentration = 0;
                                }
                            }

                            // Multiply
                            else {
                                result = concentration * Math.pow(incr, index);
                                if (result >= 0) {
                                    concentration = result;
                                }
                                else {
                                    concentration = 0;
                                }
                            }

                            var supplier_text = $('#id_supplier_text').val();
                            var lot_text = $('#id_lot_text').val();
                            var receipt_date = $('#id_receipt_date').val();

                            var info = {
                                'well': tablecellid,
                                'compound': compound_id,
                                'supplier_text': supplier_text,
                                'lot_text': lot_text,
                                'receipt_date': receipt_date,
                                'concentration': concentration,
                                'concentration_unit': concentration_unit_id,
                                'addition_time': 0,
                                'duration': 0
                            };

                            // Times in question
                            var time_conversions = {
                                'day': 1440,
                                'hour': 60,
                                'minute': 1
                            };

                            // Add times to info
                            $.each(time_conversions, function(unit, conversion) {
                                info['addition_time_'+unit] = $('#id_addition_time_' + unit).val();
                                info['duration_'+unit] = $('#id_duration_' + unit).val();
                                // Perform the conversion to minutes
                                info['addition_time'] += $('#id_addition_time_' + unit).val() * conversion;
                                info['duration'] += $('#id_duration_' + unit).val() * conversion;
                            });

                            var time_indicator = ' [ ' +
                            [info.addition_time_day, info.addition_time_hour, info.addition_time_minute].join('|') +
                            ' => ' +
                            [info.duration_day, info.duration_hour, info.duration_minute].join('|')
                            + '  ]';

                            var text = compound_name + ' (' + concentration +
                                ' ' + concentration_unit + ')' + time_indicator;

                            var li = $('<li>')
                                .text(text)
                                .attr('compound',compound_id)
                                .click(function () {
                                    if(confirm('Are you sure you want to remove this compound?\n' + $(this).text())) {
                                        $(this).remove();
                                    }
                                });

//                            var info = '{"well":"' + tablecellid + '"' +
//                                ',"compound":"' + compound_id + '","concentration":"' +
//                                concentration + '","concentration_unit":"' +
//                                concentration_unit_id + '"}';

                            info = JSON.stringify(info);

                            li.append($('<input>')
                                .attr('type','hidden')
                                .attr('name','well_' + stamp)
                                .attr('value', info));
                            list.append(li);
                        }
                    });
                }

                else {
                    alert('There was a problem processing the compound');
//                    $.ajax({
//                        url: "/compounds_ajax/",
//                        type: "POST",
//                        dataType: "json",
//                        data: {
//                            // Function to call within the view is defined by `call:`
//                            call: 'fetch_compound_name',
//
//                            // First token is the var name within views.py
//                            // Second token is the var name in this JS file
//                            compound_id: compound_id,
//
//                            // Always pass the CSRF middleware token with every AJAX call
//                            csrfmiddlewaretoken: middleware_token
//                        },
//                        success: function (json) {
//                            compound_name = json.name;
//                            add_compound_name(current_object, compound_id, time);
//
//                        },
//                        error: function (xhr, errmsg, err) {
//                            console.log(xhr.status + ": " + xhr.responseText);
//                        }
//                    });
                }
            }
        }

        // TODO needs refactor
        else if (act === 'timepoint') {
            // Legacy code: apparently with the intention of converting to minutes
            var tpunit = parseFloat($('#id_timeunit').val());
            var tptext = $('#id_timeunit option:selected').text();
            var incr = parseFloat($('#id_tpincr').val());

            var tp_value = parseFloat($('#id_timepoint').val());

            var time_how_to_increment = $('#id_tphowtoincr:checked').val();

            var time_direction = $('#id_time_direction:checked').val();

            if (tp_value < 0) {
                alert('Please specify a non-negative number for timepoint.')
            }

            else if (isNaN(tp_value) || isNaN(incr)) {
                alert('Make sure timepoint and increment are valid numbers.')
            }

            else if (time_how_to_increment === 'multiply' && incr < 0) {
                alert('Negative values are not permitted.');
            }

            else {
                var current_object = $(".ui-selected", this);

                if (time_direction === 'right_left') {
                    current_object = $($(".ui-selected", this).get().reverse());
                }

                current_object.each(function (index, value) {
                    tablecell = $(this);
                    tablecellid = tablecell.attr('id');

                    var list = $('#' + tablecellid + '_list');
                    if (list.length) {
                        var stamp = tablecellid + '_time';
                        $('#' + stamp).remove();
                        var tp = tp_value;
                        // Time point of zero allowed
                        if (tp !== '') {
                            if (time_how_to_increment === 'add') {
                                if ((tp + index * incr) >= 0) {
                                    tp += index * incr;
                                }
                                else {
                                    tp = 0;
                                }
                            }
                            else {
                                tp *= Math.pow(incr, index);
                            }

                            var text = 'Time: ' + tp + ' ' + tptext;
                            var li = $('<li>')
                                .attr('id', stamp)
                                .text(text)
                                .click(function () {
                                    if (confirm('Are you sure you want to remove this time point?\n' + $(this).text())) {
                                        $(this).remove();
                                    }
                                });

                            li.append($('<input>')
                                .attr('type', 'hidden')
                                .attr('name', stamp)
                                // Multiple by time point unit to get minutes
                                .attr('value', tp * tpunit));
                            list.prepend(li);
                        }
                    }
                });
            }
        }

        else if (act == 'add-label') {
            $(".ui-selected", this).each(function (index, value) {

                tablecell = $(this);
                tablecellid = tablecell.attr('id');

                var list = $('#' + tablecellid + '_list');
                if (list.length) {
                    var stamp = tablecellid + '_label';
                    $('#' + stamp).remove();
                    var label = $('#id_label').val();
                    if (label) {

                        var li = $('<li>')
                            .attr('id',stamp)
                            .text(label)
                            .click(function () {
                                if(confirm('Are you sure you want to remove this label?\n' + $(this).text())) {
                                    $(this).remove();
                                }
                            });

                        li.append($('<input>')
                            .attr('type','hidden')
                            .attr('name', stamp)
                            .attr('value',label));

                        list.append(li);
                    }
                }
            });
        }

        else if (act === 'clear') {
            var clear = $('#id_clear_type').val();

            $(".ui-selected", this).each(function () {
                tablecell = $(this);
                tablecellid = tablecell.attr('id');

                var list = $('#' + tablecellid + '_list');

                // Clear all 'list' elements
                if (clear == 'all') {
                    if (list.length) {
                        list.empty();
                    }
                }
                // Clear certain list elements
                else if (clear != 'type') {
                    if (list.length) {
                        if (clear === 'compound') {
                            $(this).find('li').each(function() {
                                if (this.getAttribute('compound')) {
                                    this.remove();
                                }
                            });
                        }
                        else if (clear === 'time') {
                            $(this).find('li').each(function() {
                                if (this.id.split('_')[2] === 'time') {
                                    this.remove();
                                }
                            });
                        }
                        else if (clear === 'label') {
                            $(this).find('li').each(function() {
                                if (this.id.split('_')[2] == 'label') {
                                    this.remove();
                                }
                            });
                        }
                    }
                }
                // Clear well type
                if (clear == 'all' || clear == 'type') {
                    var type = $('#' + tablecellid + '_type');
                    if (type.length) {
                        type.empty();
                        tablecell.css('background-color', 'white');
                    }
                }
            });
        }

        else {
            alert('Select action.');
        }
    };

    function clone_base_layout(layout_id, base_only) {
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_layout_format_labels',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: layout_id,

                model: 'assay_layout',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
            },
            success: function (json) {
                var row_labels = json.row_labels;
                var column_labels = json.column_labels;
                var id = json.id;
                device.val(id);
                if (row_labels && column_labels) {
                    // Build the table after setting attributes
                    window.LAYOUT.models['assay_layout'] = layout_id;
                    window.LAYOUT.base_only = base_only;
                    window.LAYOUT.is_input = true;
                    window.LAYOUT.row_labels = row_labels;
                    window.LAYOUT.column_labels = column_labels;
                    window.LAYOUT.build_table();
                }
                else {
                    alert('This device is not configured correctly.');
                }
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // On device change, acquire labels and build table
    device.change(function() {
        window.LAYOUT.get_device_layout(device.val(), 'device', true);
    });

    // Add options if admin
    if ($('fieldset')[0].innerHTML) {
        add_options();
    }
    else {
        get_well_type_selector();
    }

    // When the action changes, hide unrelated and show related class
    action.change(function() {
        var current_action =  action.val();
        $('.change-layout').hide('fast');
        if (current_action) {
            $('.' + current_action).show('fast');
        }
    });

    // Get the url for a clone
    try {
        var get_parameters = window.location.href.split('?')[1].split('=');
        var base_only = get_parameters[0] == 'base';
        var clone_id = get_parameters[1];
        clone_base_layout(clone_id, base_only);
    }
    // If nothing to clone
    catch (e) {
        // Fill table with values of preexisting assay layout
        // If a device is initially chosen
        // (implies the layout is saved)
        if (device.val()) {
            // gets the id of existing layout object from the delete link
            var delete_link = $('.deletelink');
            var layout_id = undefined;
            if (delete_link.length > 0) {
                layout_id = delete_link.first().attr('href').split('/')[4];
                window.LAYOUT.models['assay_layout'] = layout_id
            }
            else {
                layout_id = Math.floor(window.location.href.split('/')[5]);
                window.LAYOUT.models['assay_layout'] = layout_id
            }

            // Make sure all data is acquired
            window.LAYOUT.base_only = false;

            window.LAYOUT.get_device_layout(device.val(), 'device', true);
        }
    }
});
