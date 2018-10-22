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
    "use strict";
    // Alias for global variable
//    var data_map = window.COMPOUND_INSTANCES.data_map;
//    var instances = window.COMPOUND_INSTANCES.instances;
//    var suppliers = window.COMPOUND_INSTANCES.suppliers;
    var data_map = {};
    var instances = {};
    var suppliers = {};

    function autocomplete_search_this() {
        $(this).autocomplete('search', $(this).val());
    }

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
            function check_compound(obj) {
                // Somewhat sloppy solution
                if (!obj || obj.isTrigger || obj.eventPhase) obj = this;
                var current_supplier_text = $(obj)
                    .parent()
                    .parent()
                    .parent()
                    .parent()
                    .find('input[id$="supplier_text"]')
                    .first();

                if (current_supplier_text.attr('autocomplete')) {
                    current_supplier_text.autocomplete('destroy');
                }

                current_supplier_text.autocomplete({
                    // source: _.keys(data_map[$(obj).val()]),
                    source: _.sortBy(_.keys(suppliers)),
                    select: function (a, b) {
                        $(this).val(b.item.value);
                        $(this).trigger('change');
                    },
                    minLength: 0
                });

                // current_supplier_text.focus(function() {
                //     $(this).autocomplete('search', $(this).val());
                // });
                current_supplier_text.bind('focus', autocomplete_search_this);

                // Turn on autocomplete
                current_supplier_text.attr('autocomplete', 'off');

                check_supplier(current_supplier_text);
            }
            $(document).on('change', 'select.form-control[id$="compound"]', check_compound);

            // When a supplier is given
            // Sets lot based on given data
            function check_supplier(obj) {
                if (!obj || obj.isTrigger || obj.eventPhase) obj = this;
                var current_row = $(obj)
                    .parent()
                    .parent()
                    .parent();

                var current_compound_value = current_row
                    .find('select[id$="compound"]')
                    .first()
                    .val();

                var current_lot_text = current_row
                    .find('input[id$="lot_text"]')
                    .first();

                if (current_lot_text.attr('autocomplete')) {
                    current_lot_text.autocomplete('destroy');
                }

                if (data_map[current_compound_value] && $(obj).val()) {
                    current_lot_text.autocomplete({
                        source: _.keys(data_map[current_compound_value][$(obj).val()]),
                        select: function (a, b) {
                            $(this).val(b.item.value);
                            $(this).trigger('change');
                        },
                        minLength: 0
                    });

                    // current_lot_text.focus(function () {
                    //     $(this).autocomplete('search', $(this).val());
                    // });
                    current_lot_text.bind('focus', autocomplete_search_this);

                    // Turn on autocomplete
                    current_lot_text.attr('autocomplete', 'off');
                }

                check_lot(current_lot_text);
            }
            $(document).on('change', 'input.form-control[id$="supplier_text"]', check_supplier);

            // When a lot is given
            // Sets receipt date based on given data
            function check_lot(obj) {
                if (!obj || obj.isTrigger || obj.eventPhase) obj = this;
                var current_row = $(obj)
                    .parent()
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

                if (
                    current_receipt_date.attr('autocomplete') &&
                    !current_receipt_date.attr('autocomplete') === 'off'
                ) {
                    current_receipt_date.autocomplete('destroy');
                }

                if(data_map[current_compound_value] && data_map[current_compound_value][current_supplier_value] && $(obj).val()) {
                    current_receipt_date.autocomplete({
                        source: data_map[current_compound_value][current_supplier_value][$(obj).val()],
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
                    // current_receipt_date.click(function () {
                    //     $(this).autocomplete('search', $(this).val());
                    // });
                    current_receipt_date.bind('click', autocomplete_search_this);

                    // Turn on autocomplete
                    current_receipt_date.attr('autocomplete', 'off');
                }
                else {
                    current_receipt_date.unbind('click', autocomplete_search_this);
                }
            }
            $(document).on('change', 'input.form-control[id$="lot_text"]', check_lot);

            // Initially trigger whittling events above
            $('select.form-control[id$="compound"]').each(function() {
                check_compound(this);
            });
            $('input.form-control[id$="supplier_text"]').each(function() {
                check_supplier(this);
            });
            $('input.form-control[id$="lot_text"]').each(function() {
                check_lot(this);
            });
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});
