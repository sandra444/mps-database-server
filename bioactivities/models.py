from django.db import models

from mps.base.models import LockableModel


CHEMBL = None
FIELDS = {
    'chemblId': 'chemblid',
    'description': 'description',
    'geneNames': 'gene_names',
    'preferredName': 'name',
    'proteinAccession': 'uniprot_accession',
    'organism': 'organism',
    'targetType': 'target_type',
    'synonyms': 'synonyms',
    'assayOrganism': 'organism',
    'assayStrain': 'strain',
    'assayType': 'assay_type',
    'journal': 'journal',
    'assayDescription': 'description',
}


def chembl_target(chemblid):
    global CHEMBL
    if CHEMBL is None:
        from bioservices import ChEMBLdb

        CHEMBL = ChEMBLdb()

    data = CHEMBL.get_target_by_chemblId(str(chemblid))['target']

    return {FIELDS[key]: value for key, value in data.items()
            if key in FIELDS}


def chembl_assay(chemblid):
    global CHEMBL
    if CHEMBL is None:
        from bioservices import ChEMBLdb

        CHEMBL = ChEMBLdb()

    data = CHEMBL.get_assay_by_chemblId(str(chemblid))['assay']

    return {FIELDS[key]: value for key, value in data.items()
            if key in FIELDS}


class Target(LockableModel):
    #compound_id = AutoField(primary_key=True)
    name = models.TextField(help_text="Preferred target name.")
    synonyms = models.TextField(null=True, blank=True)

    # external identifiers, not unique because does go with null on SQL server
    chemblid = models.TextField('ChEMBL ID',
                                null=True, blank=True, unique=True,
                                help_text="Enter a ChEMBL id, e.g. CHEMBL260, "
                                          "and click Retrieve to get target "
                                          "information automatically.")

    description = models.TextField(null=True, blank=True)

    gene_names = models.TextField(null=True, blank=True)

    organism = models.TextField(null=True, blank=True)

    uniprot_accession = models.TextField(null=True, blank=True)

    target_type = models.TextField(null=True, blank=True)

    last_update = models.DateField(blank=True, null=True,
                                   help_text="Last time when activities "
                                             "associated with the target "
                                             "were updated.")

    class Meta(object):
        ordering = ('name', )

    def __unicode__(self):

        return self.name

    def chembl_link(self):

        if self.chemblid:
            return (u'<a href="https://www.ebi.ac.uk/chembl/target/inspect/'
                    '{0}" target="_blank">{0}</a>').format(self.chemblid)
        else:
            return u''

    chembl_link.allow_tags = True
    chembl_link.short_description = 'ChEMBL ID'


ASSAYTYPES = (('B', 'Binding'), ('F', 'Functional'), ('A', 'ADMET'))


class Assay(LockableModel):
    # external identifiers, not unique because does go with null on SQL server
    chemblid = models.TextField('ChEMBL ID',
                                null=True, blank=True, unique=True,
                                help_text="Enter a ChEMBL id, e.g. "
                                          "CHEMBL1217643, and click Retrieve "
                                          "to get target information "
                                          "automatically.")

    description = models.TextField(blank=True, null=True)
    organism = models.TextField(blank=True, null=True)
    assay_type = models.CharField(max_length=1, choices=ASSAYTYPES)
    journal = models.TextField(blank=True, null=True)
    strain = models.TextField(blank=True, null=True)

    last_update = models.DateField(blank=True, null=True,
                                   help_text="Last time when activities "
                                             "associated with the assay were "
                                             "updated.")

    class Meta(object):
        ordering = ('chemblid', )

    def __unicode__(self):

        return self.chemblid

    def chembl_link(self):

        if self.chemblid:
            return (u'<a href="https://www.ebi.ac.uk/chembl/assay/inspect/'
                    '{0}" target="_blank">{0}</a>').format(self.chemblid)
        else:
            return u''

    chembl_link.allow_tags = True
    chembl_link.short_description = 'ChEMBL ID'


class Bioactivity(LockableModel):

    class Meta(object):
        verbose_name_plural = 'bioactivities'
        unique_together = ('assay', 'target', 'compound')

    assay = models.ForeignKey(Assay)
    compound = models.ForeignKey('compounds.Compound',
                                 related_name='bioactivity_compound')
    parent_compound = models.ForeignKey('compounds.Compound',
                                        related_name='bioactivity_parent')
    target = models.ForeignKey(Target)
    target_confidence = models.IntegerField(blank=True, null=True)

    bioactivity_type = models.TextField(blank=True, null=True)
    operator = models.TextField(blank=True, null=True)

    units = models.TextField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)

    standardized_units = models.TextField(verbose_name="std units",
                                          blank=True,
                                          null=True)
    standardized_value = models.FloatField(verbose_name="std vals",
                                           blank=True,
                                           null=True)

    activity_comment = models.TextField(blank=True, null=True)
    reference = models.TextField(blank=True, null=True)
    name_in_reference = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return (str(self.compound) + ': ' + self.bioactivity_type + ' of ' +
                self.target.name)


class BioactivityTypeTable(LockableModel):

    chembl_name = models.TextField(default='')

    standard_name = models.TextField(default='')

    description = models.TextField(default='')

    standard_unit = models.TextField(default='')

    def __unicode__(self):
        return str(self.standard_name)

