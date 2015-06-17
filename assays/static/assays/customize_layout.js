// TODO This script does many things which will not be necessary on the frontend
// TODO Perhaps a separate script will be made for the front (to avoid AJAX and so on)
// This script porvides the means to make an assay layout
$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');
    var device = $('#id_device');
    // Only valid on frontend
    var action = $('#id_action');

    // TODO REMOVE SOON: SLOPPY BUT EXPEDIENT WAY TO ADD CLIENT VALIDATION
    $('#id_layout_name').attr('required', true);
    device.attr('required', true);

    // Get layout
    function get_device_layout() {
        var device_id = device.val();
        if (device_id) {
            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_layout_format_labels',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: device_id,

                    model: 'device',

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    var row_labels = json.row_labels;
                    var column_labels = json.column_labels;
                    if (row_labels && column_labels) {
                        build_table(row_labels, column_labels);
                    }
                    else {
                        alert('This device is not configured correctly');
                    }
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else {
            // Remove when invalid/nonextant layout chosen
            $('#layout_table').remove();
        }
    }

    // Build table
    function build_table(row_labels, column_labels) {
        // Remove old
        $('#layout_table').remove();

        // Choice of inserting after fieldset is contrived; for admin
        var table = $('<table>')
            .css('width','100%')
            .addClass('layout-table')
            .attr('id','layout_table').insertAfter($('fieldset')[0]);

        // make first row
        var row = $('<tr>');
        row.append($('<th>'));
        $.each(column_labels, function (index, value) {
            row.append($('<th>')
                .text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(row_labels, function (row_index, row_value) {
            var row = $('<tr>');
            row.append($('<th>')
                .text(row_value));
            // Note that the "lists" are added here
            $.each(column_labels, function (column_index, column_value) {
                row.append($('<td>')
                    .attr('id', row_value + '_' + column_value)
                    .append($('<div>')
                        .css('text-align','center')
                        .css('font-weight', 'bold')
                        .attr('id',row_value + '_' + column_value + '_type'))
                    .append($('<ul>')
                        .attr('id',row_value + '_' + column_value + '_list')
                        .addClass('layout-list')));
            });
            table.append(row);
        });

        // make selectable
        if (!$('#id_locked').prop('checked')) {
            $('#layout_table').selectable({
                filter: "td",
                distance: 1,
                stop: layout_add_content
            });
        }
    }

    function get_layout_data(layout_id, clone) {
        clone = clone || false;

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_assay_layout_content',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: layout_id,

                model: 'assay_layout',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fill_layout(json, clone);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // TODO FILL_LAYOUT
    function fill_layout(layout_data, clone) {
        $.each(layout_data, function(well, data) {
            var list = $('#' + well + '_list');

            var stamp =  '';
            var text = '';
            var li = '';

            // Set type

            stamp = well + '_type';

            $('#' + stamp)
                .text(data.type)
                .append($('<input>')
                    .attr('type', 'hidden')
                    .attr('name', stamp)
                    .attr('id', stamp)
                    .attr('value', data.type_id));

            if (data.color) {
                $('#' + well).css('background-color', data.color);
            }


            // Only add times, compounds, and labels if this is not a clone
            if (!clone) {

                // Set time
                stamp = well + '_time';
                // Only display text if timepoint or compounds (timepoint of zero acceptable)
                if (data.timepoint !== undefined) {
                    // All times should be stored as minutes
                    text = 'Time: ' + data.timepoint + ' min';

                    // Be sure to add event when necessary
                    li = $('<li>')
                        .attr('id', stamp)
                        .text(text)
                        .click(function () {
                            $(this).remove();
                        })
                        .append($('<input>')
                            .attr('type', 'hidden')
                            .attr('name', stamp)
                            .attr('value', data.timepoint));

                    list.prepend(li);
                }

                // Set compounds
                if (data.compounds) {
                    $.each(data.compounds, function (index, compound) {

                        // BE CERTAIN THAT STAMPS DO NOT COLLIDE
                        stamp = well + '_' + index;

                        text = compound.name + ' (' + compound.concentration +
                            ' ' + compound.concentration_unit + ')';

                        li = $('<li>')
                            .text(text)
                            .attr('compound', compound.id)
                            .click(function () {
                                $(this).remove();
                            });

                        var info = '{"well":"' + well + '"' +
                            ',"compound":"' + compound.id + '","concentration":"' +
                            compound.concentration + '","concentration_unit":"' +
                            compound.concentration_unit + '"}';

                        li.append($('<input>')
                            .attr('type', 'hidden')
                            .attr('name', 'well_' + stamp)
                            .attr('value', info));

                        list.append(li);
                    });
                }

                // Set label
                stamp = well + '_label';
                if (data.label) {
                    // Be sure to add event when necessary
                    li = $('<li>')
                        .attr('id', stamp)
                        .text(data.label)
                        .click(function () {
                            $(this).remove();
                        })
                        .append($('<input>')
                            .attr('type', 'hidden')
                            .attr('name', stamp)
                            .attr('value', data.label));

                    list.append(li);
                }

            }
        });
    }

    function get_well_type_selector() {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_well_types',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
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
                '<select id="id_timeunit" name="concunit">' +
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
                '<select id="id_concunit" name="concunit">' +
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
    function layout_add_content() {

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

            if (compound_id === '') {
                alert('Select a compound first.');
            }

            else {

                var compound_name = $('#id_compound :selected').text();
                var current_object = this;

                if (compound_name) {
                    add_compound_name(current_object);
                }

                else {
                    $.ajax({
                        url: "/compounds_ajax",
                        type: "POST",
                        dataType: "json",
                        data: {
                            // Function to call within the view is defined by `call:`
                            call: 'fetch_compound_name',

                            // First token is the var name within views.py
                            // Second token is the var name in this JS file
                            compound_id: compound_id,

                            // Always pass the CSRF middleware token with every AJAX call
                            csrfmiddlewaretoken: middleware_token
                        },
                        success: function (json) {
                            compound_name = json.name;
                            add_compound_name(current_object);

                        },
                        error: function (xhr, errmsg, err) {
                            console.log(xhr.status + ": " + xhr.responseText);
                        }
                    });
                }

                // Encapsulated functions may seem somewhat strange,
                // but using functional calls is an expedient alternative to promises (apparently)
                function add_compound_name(current_object) {

                    $(".ui-selected", current_object).each(function (index, value) {
                        var tablecell = $(this);
                        var tablecellid = tablecell.attr('id');
                        var list = $('#' + tablecellid + '_list');

                        if (list.length) {

                            list.find('[compound=' + compound_id + ']').remove();

                            var stamp = time + '_' + index;

                            var concentration = parseFloat(
                                $('#id_concentration').val()
                            );

                            var concentration_unit = $('#id_concunit option:selected').text();

                            var incr = parseFloat($('#id_increment').val());

                            if ($('#id_howtoincr:checked').val() === 'add') {
                                concentration += index * incr;
                            }

                            else {
                                concentration *= Math.pow(incr, index);
                            }

                            var text = compound_name + ' (' + concentration +
                                ' ' + concentration_unit + ')';

                            var li = $('<li>')
                                .text(text)
                                .attr('compound',compound_id)
                                .click(function () {
                                    $(this).remove();
                                });

                            var info = '{"well":"' + tablecellid + '"' +
                                ',"compound":"' + compound_id + '","concentration":"' +
                                concentration + '","concentration_unit":"' +
                                concentration_unit + '"}';

                            li.append($('<input>')
                                .attr('type','hidden')
                                .attr('name','well_' + stamp)
                                .attr('value', info));
                            list.append(li);
                        }
                    });
                }
            }
        }

        // TODO needs refactor
        else if (act === 'timepoint') {

            $(".ui-selected", this).each(function (index, value) {

                tablecell = $(this);
                tablecellid = tablecell.attr('id');

                var list = $('#' + tablecellid + '_list');
                if (list.length) {
                    var stamp = tablecellid + '_time';
                    $('#' + stamp).remove();
                    var tp = parseFloat($('#id_timepoint').val());
                    // Time point of zero allowed
                    if (tp !== '') {
                        // Legacy code: apparently with the intention of converting to minutes
                        var tpunit = parseFloat($('#id_timeunit').val());
                        var tptext = $('#id_timeunit option:selected').text();
                        var incr = parseFloat($('#id_tpincr').val());

                        if ($('#id_tphowtoincr:checked').val() === 'add') {
                            tp += index * incr;
                        } else {
                            tp *= Math.pow(incr, index);
                        }

                        var text = 'Time: ' + tp + ' ' + tptext;
                        var li = $('<li>')
                            .attr('id',stamp)
                            .text(text)
                            .click(function () {
                                $(this).remove();
                            });

                        li.append($('<input>')
                            .attr('type','hidden')
                            .attr('name', stamp)
                            // Multiple by time point unit to get minutes
                            .attr('value',tp * tpunit));
                        list.prepend(li);
                    }
                }
            });
        }

        // TODO ADD LABEL
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
                                $(this).remove();
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
            $(".ui-selected", this).each(function () {
                tablecell = $(this);
                tablecellid = tablecell.attr('id');
                // Clear 'list' elements
                var list = $('#' + tablecellid + '_list');
                if (list.length) {
                    list.empty();
                }
                // Clear well type
                // TODO TEST
                var type = $('#' + tablecellid + '_type');
                if (type.length) {
                    type.empty();
                    tablecell.css('background-color', 'white');
                }
            });
        }

        else {
            alert('Select action.');
        }
    }

    function clone_base_layout(layout_id, base_only) {
        $.ajax({
            url: "/assays_ajax",
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
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                var row_labels = json.row_labels;
                var column_labels = json.column_labels;
                var id = json.id;
                device.val(id);
                if (row_labels && column_labels) {
                    $.when(build_table(row_labels, column_labels)).done(function() {
                        get_layout_data(layout_id, base_only);
                    });
                }
                else {
                    alert('This device is not configured correctly');
                }
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Fill table with values of preexisting assay layout

    // On device change, acquire labels and build table
    device.change( function() {
        get_device_layout();
    });

    // Add options if admin
    if ($('fieldset')[0].innerHTML) {
        add_options();
    }
    else {
        get_well_type_selector();
    }

    // If a device is initially chosen
    // (implies the layout is saved)
    if (device.val()) {
        get_device_layout();

        // gets the id of existing layout object from the delete link
        var delete_link = $('.deletelink');
        var layout_id = undefined;
        if (delete_link.length > 0) {
            layout_id = delete_link.first().attr('href').split('/')[4];
            get_layout_data(layout_id);
        }
        else{
            layout_id = Math.floor(window.location.href.split('/')[5]);
            get_layout_data(layout_id);
        }
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
    // No action taken if nothing to clone
    catch (e) {

    }

});
