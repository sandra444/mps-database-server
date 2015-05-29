// This script porvides the means to make an assay layout
$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    // Build table
    function build_table(row_labels, column_labels) {
        // Remove old
        $('#layout_table').remove();

        // Choice of inserting after fieldset is contrived; for admin
        var table = $('<table>').css('width',
            '100%').addClass('layout-table').attr('id',
            'layout_table').insertAfter($('fieldset'));

        // make first row
        var row = $('<tr>');
        row.append($('<th>'));
        $.each(column_labels, function (index, value) {
            row.append($('<th>').text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(row_labels, function (row_index, row_value) {
            var row = $('<tr>');
            row.append($('<th>').text(row_value));
            // Note that the "lists" are added here
            $.each(column_labels, function (column_index, column_value) {
                row.append($('<td>')
                    .attr('id', row_value + '_' + column_value)
                    .append($('<div>')
                        .css('text-align','center')
                        .css('font-weight', 'bold')
                        .attr('id',row_value + '_' + column_value + '_type'))
                    .append($('<ul>')
                        .attr('id',
                        row_value + '_' + column_value + '_list')
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
            var select = $('<select>').attr('id', 'welltype').appendTo('#well_type_div')
                .append($('<option>')
                    .css('background-color','white')
                    .attr('value', '')
                    .text('---------'));

            $.each(data, function (id, name) {
                select.append($('<option>').attr('value', id).text(name));
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
                '<option value="label">Add label</option>' +
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

            controls.append('<div class="form-row field-label"> ' +
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
                base_layout_set_color_cb('white');

            }

            else {

                well_colortype = well_type.val();

                $.ajax({
                    url: "/assays_ajax",
                    type: "POST",
                    dataType: "json",
                    data: {
                        // Function to call within the view is defined by `call:`
                        call: 'fetch_well_type_color',

                        // First token is the var name within views.py
                        // Second token is the var name in this JS file
                        id: well_colortype,

                        // Always pass the CSRF middleware token with every AJAX call
                        csrfmiddlewaretoken: middleware_token
                    },
                    success: function (json) {
                        set_color(json);
                    },
                    error: function (xhr, errmsg, err) {
                        console.log(xhr.status + ": " + xhr.responseText);
                    }
                });

            }

            // for each selected cell/well
            // it updates the contents of the
            var value = well_type.val();
            var fs = $($('fieldset')[0]);

            $(".ui-selected", this).each(function () {
                tablecell = $(this);
                type_label = $('#' + tablecell.attr('id') + '_type');
                var wtid = 'wt_' + tablecell.attr('id');
                // removes hidden field
                $('#' + wtid).remove();
                // ---- means clear the cell
                if (text === '---------') {
                    type_label.text('');
                } else {
                    // creates a hidden input field for the well
                    // value is the type of well
                    type_label.text(text);
                    // TODO APPEND TO DIV IN LIEU OF fieldset
                    fs.append($('<input>').attr('type', 'hidden').attr('name',
                        wtid).attr('id', wtid).attr('value', value));
                }
            });

            // modifies cells selected in the layout
            function set_color(color) {
                $("#welltype option:selected").css('background-color', color);
                $(".ui-selected").css('background-color', color);
            }
        }

        else if (act === 'compound') {

            var compound_id = $('#id_compound').val();

            if (compound_id === '') {
                alert('Select a compound first.');
                return;
            }

            else {

                var compound_name = '';
                var current_object = this;

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

                function add_compound_name(current_object) {

                    $(".ui-selected", current_object).each(function (index, value) {
                        var tablecell = $(this);
                        var tablecellid = tablecell.attr('id');
                        var list = $('#' + tablecellid + '_list');

                        if (list.length) {

                            list.find('[compound=' + compound_id +
                                ']').remove();

                            var stamp = time + '_' + index;

                            var concentration = parseFloat(
                                $('#id_concentration').val()
                            );

                            var concentration_unit =
                                $('#id_concunit option:selected').text();

                            var incr = parseFloat($('#id_increment').val());

                            if ($('#id_howtoincr:checked').val() === 'add') {
                                concentration += index * incr;
                            } else {
                                concentration *= Math.pow(incr, index);
                            }

                            var text = compound_name + ' (' + concentration +
                                ' ' + concentration_unit + ')';

                            var li = $('<li>').text(text).attr('compound',
                                compound_id).click(function () {
                                    $(this).remove();
                                });

                            var info = 'well="' + tablecellid + '"' +
                                ',compound=' + compound_id + ',concentration=' +
                                concentration + ',concentration_unit="' +
                                concentration_unit + '"';

                            li.append($('<input>').attr('type',
                                'hidden').attr('name',
                                    'well_' + stamp).attr('value', info));
                            list.append(li);
                        }
                    });
                }
            }
        }
        else if (act === 'timepoint') {

            $(".ui-selected", this).each(function (index, value) {

                tablecell = $(this);
                tablecellid = tablecell.attr('id');

                var list = $('#' + tablecellid + '_list');
                if (list.length) {
                    var stamp = tablecellid + '_time';
                    $('#' + stamp).remove();
                    var tp = parseFloat($('#id_timepoint').val());
                    if (tp !== '') {
                        // Legacy code: apparently with the intention of converting to minutes
                        //var tpunit = parseFloat($('#id_timeunit').val());
                        var tptext = $('#id_timeunit option:selected').text();
                        var incr = parseFloat($('#id_tpincr').val());
                        if ($('#id_tphowtoincr:checked').val() === 'add') {
                            tp += index * incr;
                        } else {
                            tp *= Math.pow(incr, index);
                        }

                        var text = 'Time: ' + tp + ' ' + tptext;
                        var li = $('<li>').attr('id',
                            stamp).text(text).click(function () {
                                $(this).remove();
                            });

                        li.append($('<input>').attr('type',
                            'hidden').attr('name', stamp).attr('value',
                            tp));
                        list.prepend(li);
                    }
                }
            });
        }

        // TODO ADD LABEL
        else if (act == 'label') {
            $(".ui-selected", this).each(function (index, value) {

                tablecell = $(this);
                tablecellid = tablecell.attr('id');

                var list = $('#' + tablecellid + '_list');
                if (list.length) {
                    var stamp = tablecellid + '_label';
                    $('#' + stamp).remove();
                    var label = $('#id_label').val();
                    if (label) {

                        var li = $('<li>').attr('id',
                            stamp).text(label).click(function () {
                                $(this).remove();
                            });

                        li.append($('<input>').attr('type',
                            'hidden').attr('name', stamp).attr('value',
                            label));
                        list.append(li);
                    }
                }
            });
        }

        else if (act === 'clear') {
            $(".ui-selected", this).each(function () {
                tablecell = $(this);
                // Clear 'list' elements
                var list = $('#' + tablecell.attr('id') + '_list');
                if (list.length) {
                    list.empty();
                }
                // Clear well type
                // TODO TEST
                var type = $('#' + tablecell.attr('id') + '_type');
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

    // Fill table with values of preexisting assay layout

    // On device change, acquire labels and build table
    $('#id_device').change( function() {
        var device_id = $('#id_device').val();
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
    });

    // Add options if admin
    if ($('fieldset')[0]) {
        add_options();
    }

});
