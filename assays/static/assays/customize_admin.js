$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');



    $('#id_assay_layout').change( function () {
            if ($('#id_base_layout_name').val() === '') {
            } else {
                make_layout(base_layout.val());
            }

    });


    // ASSAY BASE LAYOUT

    // modifies cells selected in the layout
    function base_layout_alter_selection() {
        var wt = $("#welltype option:selected");
        var text = wt.text();
        if (text === '---------') {
            base_layout_set_color_cb('white');

        } else {

            well_colortype = wt.val();

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
                    base_layout_set_color_cb(json);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });

        }

        // for each selected cell/well
        // it updates the contents of the
        var value = wt.val();
        var fs = $($('fieldset')[0]);

        $(".ui-selected", this).each(function () {
            tablecell = $(this);
            var wtid = 'wt_' + tablecell.attr('id');
            // removes hidden field
            $('#' + wtid).remove();
            // ---- means clear the cell
            if (text === '---------') {
                tablecell.text('');
            } else {
                // creates a hidden input field for the well
                // value is the type of well
                tablecell.text(text);
                fs.append($('<input>').attr('type', 'hidden').attr('name',
                    wtid).attr('id', wtid).attr('value', value));
            }
        });
    }

    // modifies cells selected in the layout
    function base_layout_set_color_cb(color) {
        $("#welltype option:selected").css('background-color', color);
        $(".ui-selected").css('background-color', color);
    }


    // call back functions functions for creating selector and table
    function create_well_type_selector(data) {
        var cell = $($('#layout_table th')[0]);
        cell.empty();
        var select = $('<select>').attr('id', 'welltype').appendTo(cell);
        select.append($('<option>').css('background-color',
            'white').attr('value', '').text('---------'));

        // convert JSON string into a JavaScript Object
        var json = eval(data);

        $.each(data, function (i, v) {
            select.append($('<option>').attr('value', i).text(v));
        });

        // this is to add a new well type
        select.after($('<a href="/admin/assays/assaywelltype/add/" ' +
            'class="add-another" id="add_welltype" ' +
            'onclick="return showAddAnotherPopup(this);"> ' +
            '<img src="/static/admin/img/icon_addlink.gif" width="10" ' +
            'height="10" alt="Add Another"></a>'));
    }


    function create_base_layout_table(data) {

        var table = $('<table>').css('width',
                '100%').addClass('layout-table').attr('id',
                'layout_table').appendTo($('#layout_div'));

        // make first row
        var row = $('<tr>');
        row.append($('<th>'));
        var column_labels = data.column_labels;
        $.each(column_labels, function (index, value) {
            row.append($('<th>').text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(data.row_labels, function (r, rval) {
            var row = $('<tr>');
            row.append($('<th>').text(rval));
            $.each(column_labels, function (c, cval) {
                row.append($('<td>').attr('id', rval + '_' + cval));
            });
            table.append(row);

        });

        // make selectable
        if (!$('#id_locked').prop('checked')) {
            $('#layout_table').selectable({
                filter: "td",
                distance: 1,
                stop: base_layout_alter_selection,
                /*selecting: function() {
                 $(".ui-selecting", this).each(function() {
                 this.className = "ui-selecting";
                 });
                 },*/
            });
        }

        if (!$('#id_locked').prop('checked')) {
            // create selector

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


        }
    }


    function fill_base_layout(data) {
        // layout fill function
        // in addition to filling cells/wells, creates hidden inputs
        var fs = $($('fieldset')[0]);
        $.each(data, function (k, v) {
            var wtid = 'wt_' + k;
            $("#" + k).text(v[1]).css('background-color', v[2]);

            fs.append($('<input>').attr('type', 'hidden').attr('name',
                wtid).attr('id', wtid).attr('value', v[0]));
        });
    }

    function make_base_layout(format_id) {
        if (format_id.length) {
            $('#layout_div').remove();

            $('fieldset').after($('<div>').attr('id',
                'layout_div').addClass('module inline'));

            // create table
            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_layout_format_labels',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: format_id,

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    create_base_layout_table(json);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });

        } else {
            $('#layout_div').remove();
        }
    }


    layout_format = $('#id_layout_format');
    if (layout_format.length) {
        var format_id = layout_format.val();

        layout_format.change(function () {
            // Make sure ALL required input fields are full
            // if not layout will get lost when saving with empty required fields
            if ($('#id_base_layout_name').val() === '') {
                alert('Enter base layout name before designing a base layout.');
                layout_format.find('option:selected').removeAttr("selected");
            } else {
                make_base_layout(layout_format.val());
            }

        });

        // create layout for an existing Base Layout Object
        if ($('#id_layout_format option:selected').text() != '---------') {
            make_base_layout(layout_format.val());
            // get's the id of existing layout object from the delete link
            var blid = $($('.deletelink')[0]).attr('href').split('/')[4];

            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_base_layout_wells',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: blid,

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    fill_base_layout(json);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });

        }
    }

    // END BASE LAYOUT

    function fetch_compound_name(data) {
        return data.name;
    }

    function layout_add_content() {

        var act = $('#id_action').val();
        // using time to create a unique ID for a cell content
        var date = new Date();
        var time = date.getTime() % 1000000;


        if (act === 'compound') {

            var compound_id = $('#id_compound').val();

            if (compound_id === '') {
                alert('Select a compound first.');
                return;
            } else {

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
                        compound_name = fetch_compound_name(json);
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

        } else if (act === 'timepoint') {

            $(".ui-selected", this).each(function (index, value) {

                tablecell = $(this);
                tablecellid = tablecell.attr('id');

                var list = $('#' + tablecellid + '_list');
                if (list.length) {
                    var stamp = tablecellid + '_time';
                    $('#' + stamp).remove();
                    var tp = parseFloat($('#id_timepoint').val());
                    if (tp != 0) {
                        var tpunit = parseFloat($('#id_timeunit').val());
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

        } else if (act === 'clear') {

            $(".ui-selected", this).each(function () {
                tablecell = $(this);
                var list = $('#' + tablecell.attr('id') + '_list');
                if (list.length) {
                    list.empty();
                }

            });

        } else {
            alert('Select action.');
        }

    }

    function create_layout_table(data) {
        create_base_layout_table(data['format']);
        var legend = {};
        // color and label cells
        $.each(data['wells'], function (k, v) {
            $('#' + k).css('background-color',
                    v[1]).append($('<div>').css('text-align',
                    'center').append($('<b>').text(v[0]))).append($('<ul>').attr('id',
                    k + '_list').addClass('layout-list'));
        });

        if (!$('#id_locked').prop('checked')) {
            // add compound and cell sample search
            var controls = $('<div>').attr('id', 'controls');

            // action
            controls.append($('<div class="form-row field-action"><div>' +
                '<label for="id_action">Action:</label><select id="id_action" name="action">' +
                '<option value="" selected="selected">---------</option>' +
                '<option value="timepoint">Set time point</option>' +
                '<option value="compound">Add compound</option>' + /*'<option value="cellsample">Add cell sample</option>' +*/
                '<option value="clear">Clear contents</option>' +
                '</select></div></div>'));

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
                '<input class="vForeignKeyRawIdAdminField" id="id_compound" name="compound" type="text" value="" disabled="">' +
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

            $('fieldset').append(controls);

            // make table selectable
            $('#layout_table').selectable({
                filter: "td",
                distance: 1,
                stop: layout_add_content,
            });
        }

        // get's the id of existing layout object from the delete link
        if ($('.deletelink').length > 0) {
            var lid = $($('.deletelink')[0]).attr('href').split('/')[4];
            fill_layout(lid);
        }
    }

    function make_layout(base_id) {
        if (typeof(base_id) != "undefined" && base_id.length) {
            $('#layout_div').remove();
            $('#controls').remove();

            $('fieldset').after($('<div>').attr('id',
                'layout_div').addClass('module inline'));

            // create table

            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_base_layout_info',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: base_id,

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    create_layout_table(json);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });

        } else {
            $('#layout_div').remove();
            $('#controls').remove();
        }

    }

    function fill_layout(layout_id) {

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_assay_layout_content',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                assay_layout_id: layout_id,

                // Evil hack to get the CSRF middleware token
                // Always pass the CSRF middleware token with every AJAX call

                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fill_layout_content(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

    }

    function fill_layout_content(req) {

        var stamp_counter = 0;

        $.each(req, function (well, content) {

            var list = $('#' + well + '_list');

            $.each(content, function (index, data) {

                var stamp = well + '_time';
                var tp = data.timepoint;

                if (tp > 0 && $('#' + stamp).length === 0) {
                    var text = 'Time: ' + tp + ' min';
                    var li = $('<li>').attr('id',
                            stamp).text(text).click(function () {
                            $(this).remove();
                        });
                    li.append($('<input>').attr('type', 'hidden').attr('name',
                        stamp).attr('value', tp));
                    list.prepend(li);
                }

                if (data.compound) {

                    compound_id = data.compound;
                    concentration = data.concentration;
                    concentration_unit = data.concentration_unit;

                    var text = data.name + ' (' + concentration + ' ' +
                        concentration_unit + ')';

                    var li = $('<li>').text(text).attr('compound',
                            compound_id).click(function () {
                            $(this).remove();
                        });

                    var info = 'well="' + well + '"' + ',compound=' +
                        compound_id + ',concentration=' + concentration +
                        ',concentration_unit="' + concentration_unit + '"';

                    stamp_counter++;
                    li.append($('<input>').attr('type', 'hidden').attr('name',
                        'well_' + stamp_counter).attr('value', info));
                    list.append(li);

                }
            });
        });

    }

    // ASSAY LAYOUT

    base_layout = $('#id_base_layout');

    if (base_layout.length) {
        base_layout.change(function () {

            // Make sure ALL required input fields are full
            // if not layout will get lost when saving with empty required fields

            if ($('#id_layout_name').val() === '') {
                alert('Fill in layout name before designing a layout.');
                base_layout.find('option:selected').removeAttr("selected");
            } else {
                make_layout(base_layout.val());
            }

        });

        // create layout for an existing Base Layout Object
        if ($('#id_base_layout option:selected').text() != '---------') {
            make_layout(base_layout.val());


        }

    }

    // END ASSAY LAYOUT



});
