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
    name = models.CharField(max_length=200,
                            help_text="Preferred target name.")
    synonyms = models.TextField(max_length=4000,
                                null=True, blank=True)

    # external identifiers, not unique because does go with null on SQL server
    chemblid = models.CharField('ChEMBL ID', max_length=20,
                                null=True, blank=True, unique=True,
                                help_text="Enter a ChEMBL id, e.g. CHEMBL260, "
                                          "and click Retrieve to get target "
                                          "information automatically.")

    description = models.CharField(max_length=400,
                                   null=True, blank=True)
    gene_names = models.CharField(max_length=250,
                                  null=True, blank=True)
    organism = models.CharField(max_length=100,
                                null=True, blank=True)
    uniprot_accession = models.CharField(max_length=200,
                                         null=True, blank=True)
    target_type = models.CharField(max_length=100,
                                   null=True, blank=True)

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
    chemblid = models.CharField('ChEMBL ID', max_length=20,
                                null=True, blank=True, unique=True,
                                help_text="Enter a ChEMBL id, e.g. "
                                          "CHEMBL1217643, and click Retrieve "
                                          "to get target information "
                                          "automatically.")

    description = models.TextField(max_length=1000, blank=True, null=True)
    organism = models.CharField(max_length=100, blank=True, null=True)
    assay_type = models.CharField(max_length=1, choices=ASSAYTYPES)
    journal = models.CharField(max_length=100, blank=True, null=True)
    strain = models.CharField(max_length=100, blank=True, null=True)

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

    bioactivity_type = models.CharField(max_length=100)
    operator = models.CharField(max_length=20, blank=True, null=True)

    units = models.CharField(max_length=40, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)

    standardized_units = models.CharField(max_length=40,
                                          verbose_name="std units",
                                          blank=True,
                                          null=True)
    standardized_value = models.FloatField(verbose_name="std vals",
                                           blank=True,
                                           null=True)

    activity_comment = models.CharField(max_length=250, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    name_in_reference = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return (str(self.compound) + ': ' + self.bioactivity_type + ' of ' +
                self.target.name)
