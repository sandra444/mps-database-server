$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    function assay_finalizer(data) {

        $('#id_description').val(data.assay.assayDescription);
        $('#id_assay_type').val(data.assay.assayType);
        $('#id_organism').val(data.assay.assayOrganism);
        $('#id_strain').val(data.assay.assayDescription);
        $('#id_journal').val(data.assay.journal);

        return $('#retrieve').removeAttr('disabled').val('Retrieve');
    }

    function target_finalizer(data) {

        $('#id_name').val(data.target.preferredName);
        $('#id_synonyms').val(data.target.synonyms);
        $('#id_description').val(data.target.description);
        $('#id_gene_names').val(data.target.geneNames);
        $('#id_organism').val(data.target.organism);
        $('#id_uniprot_accession').val(data.target.proteinAccession);
        $('#id_target_type').val(data.target.targetType);

        return $('#retrieve').removeAttr('disabled').val('Retrieve');
    }

    function caller(selection, chemblid, middleware_token) {

        return $.ajax({
            url: "/compounds_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_chemblid_data',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                chemblid: chemblid,

                // Select assay data return
                selector: selection,

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {

                if (json.error) {
                    alert(json.error);
                    $('#retrieve').removeAttr('disabled').val('Retrieve');
                } else {
                    if ('assay' === selection) {
                        assay_finalizer(json);
                    } else if ('target' === selection) {
                        target_finalizer(json);
                    }
                }

            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }


    if ($('.object-tools > li > .addlink').length) {
        $(".object-tools").append(
            '<li><a href="add_multi/" class="addlink">Add multiple</a></li>'
        );
    }

    if (!$('#id_locked').prop('checked')) {
        $('<input type="button" value="Retrieve" id="retrieve" name="_fetch">')
            .insertAfter('#id_chemblid');

        $('#retrieve').click(function () {
            var chemblid = $('#id_chemblid').val();

            if (chemblid.match("^CHEMBL")) {

                /* If we match CHEMBL, display the fact that we are in the
                 * process of retrieving data */
                $('#retrieve').val('Retrieving').attr('disabled', 'disabled');

                var selection = '';

                if ($('.bioactivities-assay').length) {
                    // If we are adding an assay, fetch CHEMBL assays
                    selection = 'assay';
                }

                if ($('.bioactivities-target').length) {
                    // If we are adding an assay, fetch CHEMBL targets
                    selection = 'target';
                }

                caller(selection, chemblid, middleware_token);

            } else {
                alert("Please enter a ChEMBL id.");
            }
        });
    }
});
