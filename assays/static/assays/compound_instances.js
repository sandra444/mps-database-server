// This file tracks compound instances for Chip Setups and Assay Layouts
// TODO to be refactored

// IMPORTANT NOTE //
// Instances are placed in the dictionary using the following key:
// <compound_id>_<supplier_name>_<lot>_<receipt_date (as ISO [assumed])>

// Global variable for sharing data with other files
// NOT CURRENTLY USED
//window.COMPOUND_INSTANCES = {
//    'data_map': {},
//    'instances': {},
//    'suppliers': {}
//};

$(document).ready(function() {
    // Alias for global variable
//    var data_map = window.COMPOUND_INSTANCES.data_map;
//    var instances = window.COMPOUND_INSTANCES.instances;
//    var suppliers = window.COMPOUND_INSTANCES.suppliers;
    var data_map = {};
    var instances = {};
    var suppliers = {};

    $.ajax({
        url: "/compounds_ajax/",
        type: "POST",
        dataType: "json",
        data: {
            call: 'fetch_compound_instances',
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        },
        success: function (json) {
            var json_instances = json.instances;
            var json_suppliers = json.suppliers;

            // *Unless something dynamic is being performed,this should just be in python!*
            $.each(json_instances, function(index, compound_instance) {
                var compound_instance_id = compound_instance.id;
                var compound_id = compound_instance.compound_id;
                var supplier_name = compound_instance.supplier_name;
                var lot = compound_instance.lot;
                var receipt_date = compound_instance.receipt_date;

                // Add to instance
                // instances[compound_instance_id] = compound_instance;

                // Add to data map
                if(!data_map[compound_id]) {
                    data_map[compound_id] = {};
                }

                if(!data_map[compound_id][supplier_name]) {
                    data_map[compound_id][supplier_name] = {};
                }

                if(!data_map[compound_id][supplier_name][lot]) {
                    data_map[compound_id][supplier_name][lot] = [];
                }

                // Add the receipt date
                if(receipt_date) {
                    // Format the date
                    receipt_date = new Date(receipt_date * 1000).toISOString().split('T')[0];
                    data_map[compound_id][supplier_name][lot].push(receipt_date);
                }
                else {
                    data_map[compound_id][supplier_name][lot].push('');
                }

                // Add to instance
                instances[[compound_id, supplier_name, lot, receipt_date].join('_')] = compound_instance_id;
            });

            // Add suppliers
            $.each(json_suppliers, function(index, supplier) {
                var supplier_id = supplier.id;
                var supplier_name = supplier.name;
                // Add to suppliers
                suppliers[supplier_name] = supplier_name;
            });

            // Notice that all of this is in the AJAX success call
            // When a compound is selected
            // ALL SUPPLIERS ARE SHOWN INSTEAD NOW
            $(document).on('change', 'select[id$="compound"]', function() {
                var current_supplier_text = $(this)
                    .parent()
                    .parent()
                    .find('input[id$="supplier_text"]')
                    .first();

                if (current_supplier_text.data('autocomplete')) {
                    current_supplier_text.autocomplete('destroy');
                }

                current_supplier_text.autocomplete({
                    // source: _.keys(data_map[$(this).val()]),
                    source: _.sortBy(_.keys(suppliers)),
                    select: function (a, b) {
                        $(this).val(b.item.value);
                        $(this).trigger('change');
                    },
                    minLength: 0
                });

                current_supplier_text.focus(function() {
                    $(this).autocomplete('search', $(this).val());
                });

                // Turn on autocomplete
                current_supplier_text.attr('autocomplete', 'on');
            });

            // When a supplier is given
            // Sets lot based on given data
            $(document).on('change', 'input[id$="supplier_text"]', function() {
                var current_row = $(this)
                    .parent()
                    .parent();

                var current_compound_value = current_row
                    .find('select[id$="compound"]')
                    .first()
                    .val();

                var current_lot_text = current_row
                    .find('input[id$="lot_text"]')
                    .first();

                if (current_lot_text.data('autocomplete')) {
                    current_lot_text.autocomplete('destroy');
                }

                if(data_map[current_compound_value]) {
                    current_lot_text.autocomplete({
                        source: _.keys(data_map[current_compound_value][$(this).val()]),
                        select: function (a, b) {
                            $(this).val(b.item.value);
                            $(this).trigger('change');
                        },
                        minLength: 0
                    });

                    current_lot_text.focus(function() {
                        $(this).autocomplete('search', $(this).val());
                    });

                    // Turn on autocomplete
                    current_lot_text.attr('autocomplete', 'on');
                }
            });

            // When a lot is given
            // Sets receipt date based on given data
            $(document).on('change', 'input[id$="lot_text"]', function() {
                var current_row = $(this)
                    .parent()
                    .parent();

                var current_compound_value = current_row
                    .find('select[id$="compound"]')
                    .first()
                    .val();

                var current_supplier_value = current_row
                    .find('input[id$="supplier_text"]')
                    .first()
                    .val();

                var current_receipt_date = current_row
                    .find('input[id$="receipt_date"]')
                    .first();

                if (current_receipt_date.data('autocomplete')) {
                    current_receipt_date.autocomplete('destroy');
                }

                if(data_map[current_compound_value] && data_map[current_compound_value][current_supplier_value]) {
                    current_receipt_date.autocomplete({
                        source: data_map[current_compound_value][current_supplier_value][$(this).val()],
                        minLength: 0,
                        select: function (a, b) {
                            $(this).val(b.item.value);
                            $(this).trigger('change');
                        },
                        position: {
                            my: "left bottom",
                            at: "left top",
                            collision: "flipfit"
                        }
                    });

                    // Uses click instead of focus
                    current_receipt_date.click(function () {
                        $(this).autocomplete('search', $(this).val());
                    });

                    // Turn on autocomplete
                    current_receipt_date.attr('autocomplete', 'on');
                }
            });

//            // When a receipt date is given
//            // Sets compound_instance ID (for ease of detecting duplicates)
//            $(document).on('change', 'input[id$="receipt_date"]', function() {
//                var current_row = $(this)
//                    .parent()
//                    .parent();
//
//                var current_compound_instance = current_row
//                    .find('select[id$="compound_instance"]')
//                    .first();
//
//                if (current_compound_instance) {
//                    var current_compound_value = current_row
//                        .find('select[id$="compound"]')
//                        .first()
//                        .val();
//
//                    var current_supplier_value = current_row
//                        .find('input[id$="supplier_text"]')
//                        .first()
//                        .val();
//
//                    var current_lot_value = current_row
//                        .find('input[id$="lot_text"]')
//                        .first()
//                        .val();
//
//                    var current_receipt_date_value = $(this).val();
//
//                    var instance_key = [
//                        current_compound_value,
//                        current_supplier_value,
//                        current_lot_value,
//                        current_receipt_date_value
//                    ].join('_');
//
//                    // If there is an available instance, use it
//                    if (instances[instance_key]) {
//                        current_compound_instance.val(instances[instance_key]);
//                    }
//                    else {
//                        current_compound_instance.val('');
//                    }
//                    console.log(instances);
//                    console.log(instance_key);
//                    console.log(instances[instance_key]);
//                    console.log(current_compound_instance.val());
//                }
//            });
//
//            // TODO SECTION NOT VERY DRY
//            // Times in question
//            var time_conversions = {
//                'day': 1440,
//                'hour': 60,
//                'minute': 1
//            };
//
//            // Fill addition time and duration with converted values
//            // (THIS TOO IS FOR CONVENIENCE WHEN PROCESSING FORM)
//            $(document).on('change', 'input[id*="addition_time_"]', function() {
//                var current_row = $(this)
//                    .parent()
//                    .parent();
//
//                var current_addition_time = current_row
//                    .find('select[id$="addition_time"]')
//                    .first();
//
//                var new_addition_time = 0;
//
//                // Add times to info
//                $.each(time_conversions, function(unit, conversion) {
//                    var current_addition_time_x = current_addition_time.val();
//                    // Perform the conversion to minutes
//                    new_addition_time += current_addition_time_x * conversion;
//                });
//
//                current_addition_time.val(new_addition_time);
//                console.log(new_addition_time);
//            });
//
//            $(document).on('change', 'input[id="duration_"]', function() {
//                var current_row = $(this)
//                    .parent()
//                    .parent();
//
//                var current_duration = current_row
//                    .find('select[id$="duration"]')
//                    .first();
//
//                var new_duration = 0;
//
//                // Add times to info
//                $.each(time_conversions, function(unit, conversion) {
//                    var current_duration_x = current_duration.val();
//                    // Perform the conversion to minutes
//                    new_duration += current_duration_x * conversion;
//                });
//
//                current_duration.val(new_duration);
//                console.log(new_duration);
//            });

            // Initially trigger whittling events above
            $('select[id$="compound"]').trigger('change');
            $('input[id$="supplier_text"]').trigger('change');
            $('input[id$="lot_text"]').trigger('change');
//            $('input[id$="receipt_date"]').trigger('change');
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});
