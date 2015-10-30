$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    function compound_finalizer(data) {

        $('#id_name').val(data.compound.preferredCompoundName);
        $('#id_inchikey').val(data.compound.stdInChiKey);
        $('#id_smiles').val(data.compound.smiles);
        // Note that the synonyms are modified so that there is a space after
        // Each comma. Replace can not be performed on undefined variables.
        if (data.compound.synonyms) {
            $('#id_synonyms').val(data.compound.synonyms.replace(/,/g, ', '));
        }
        $('#id_molecular_formula').val(data.compound.molecularFormula);
        $('#id_molecular_weight').val(data.compound.molecularWeight);
        $('#id_rotatable_bonds').val(data.compound.rotatableBonds);
        $('#id_acidic_pka').val(data.compound.acdAcidicPka);
        $('#id_basic_pka').val(data.compound.acdBasicPka);
        $('#id_logp').val(data.compound.acdLogp);
        $('#id_logd').val(data.compound.acdLogd);
        $('#id_alogp').val(data.compound.alogp);
        $('#id_ro5_violations').val(data.compound.numRo5Violations);
        $('#id_species').val(data.compound.species);

        if ("Yes" === data.compound.knownDrug) {
            $('#id_known_drug').prop('checked', true);
        } else {
            $('#id_known_drug').prop('checked', false);
        }

        if ("Yes" === data.compound.medChemFriendly) {
            $('#id_medchem_friendly').prop('checked', true);
        } else {
            $('#id_medchem_friendly').prop('checked', false);
        }

        if ("Yes" === data.compound.passesRuleOfThree) {
            $('#id_ro3_passes').prop('checked', true);
        } else {
            $('#id_ro3_passes').prop('checked', false);
        }

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
                    if ('compound' === selection) {
                        compound_finalizer(json);
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

                if ($('.compounds-compound').length) {
                    // If we are adding an assay, fetch CHEMBL assays
                    selection = 'compound';
                }

                caller(selection, chemblid, middleware_token);

            } else {
                alert("Please enter a ChEMBL id.");
            }
        });
    }
});
