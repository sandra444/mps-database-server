// This file tracks compound instances for Chip Setups and Assay Layouts
// TODO to be refactored

// IMPORTANT NOTE //
// Instances are placed in the dictionary using the following key:
// <compound_id>_<supplier_name>_<lot>_<receipt_date (as ISO [assumed])>

// Global variable for sharing data with other files
window.COMPOUND_INSTANCES = {
    'data_map': {},
    'instances': {},
    'suppliers': {}
};

$(document).ready(function() {
    // TODO REVISE ACQUISITION OF TOKEN
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');
    // Alias for global variable
    var data_map = window.COMPOUND_INSTANCES.data_map;
    var instances = window.COMPOUND_INSTANCES.instances;
    var suppliers = window.COMPOUND_INSTANCES.suppliers;

    $.ajax({
        url: "/compounds_ajax/",
        type: "POST",
        dataType: "json",
        data: {
            call: 'fetch_compound_instances',
            csrfmiddlewaretoken: middleware_token
        },
        success: function (json) {
            // *Unless something dynamic is being performed,this should just be in python!*
            $.each(json, function(index, compound_instance) {
                var compound_instance_id = compound_instance.id;
                var compound_id = compound_instance.compound_id;
                var supplier_name = compound_instance.supplier_name;
                var lot = compound_instance.lot;
                var receipt_date = compound_instance.receipt_date;

                // Add to instance
                instances[compound_instance_id] = compound_instance;

                // Add to suppliers
                suppliers[supplier_name] = supplier_name;

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
            $(document).on('change', 'input[id$="supplier_text"]', function() {
                var current_compound_value = $(this)
                    .parent()
                    .parent()
                    .find('select[id$="compound"]')
                    .first()
                    .val();

                var current_lot_text = $(this)
                    .parent()
                    .parent()
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
            $(document).on('change', 'input[id$="lot_text"]', function() {
                var current_compound_value = $(this)
                    .parent()
                    .parent()
                    .find('select[id$="compound"]')
                    .first()
                    .val();

                var current_supplier_value = $(this)
                    .parent()
                    .parent()
                    .find('input[id$="supplier_text"]')
                    .first()
                    .val();

                var current_receipt_date = $(this)
                    .parent()
                    .parent()
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

            // Initially trigger whittling events above
            $('select[id$="compound"]').trigger('change');
            $('input[id$="supplier_text"]').trigger('change');
            $('input[id$="lot_text"]').trigger('change');
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});
