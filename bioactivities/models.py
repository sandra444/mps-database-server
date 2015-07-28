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
        from bioservices import ChEMBL as ChEMBLdb

        CHEMBL = ChEMBLdb()

    data = CHEMBL.get_target_by_chemblId(str(chemblid))['target']

    return {FIELDS[key]: value for key, value in data.items()
            if key in FIELDS}


def chembl_assay(chemblid):
    global CHEMBL
    if CHEMBL is None:
        from bioservices import ChEMBL as ChEMBLdb

        CHEMBL = ChEMBLdb()

    data = CHEMBL.get_assays_by_chemblId(str(chemblid))['assay']

    return {FIELDS[key]: value for key, value in data.items()
            if key in FIELDS}


class Target(LockableModel):
    # compound_id = AutoField(primary_key=True)
    name = models.TextField(default='', help_text="Preferred target name.")
    synonyms = models.TextField(default='')

    # external identifiers, not unique because does go with null on SQL server
    chemblid = models.TextField('ChEMBL ID',
                                default='',
                                help_text="Enter a ChEMBL id, e.g. CHEMBL260, "
                                          "and click Retrieve to get target "
                                          "information automatically.")

    description = models.TextField(default='')

    gene_names = models.TextField(default='')

    organism = models.TextField(default='')

    uniprot_accession = models.TextField(default='')

    # Without a ChEMBL link, I think it is fair to assume the target_type is single protein
    target_type = models.TextField(default='')

    # NCBI identifier for protein/gene targets
    GI = models.TextField('NCBI GI',
                          default='')

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


ASSAYTYPES = (('B', 'Binding'), ('F', 'Functional'), ('A', 'ADMET'), ('P', 'Physicochemical'), ('U', 'Unknown'))

class Assay(LockableModel):
    # external identifiers, not unique because does go with null on SQL server
    chemblid = models.TextField('ChEMBL ID',
                                default='',
                                help_text="Enter a ChEMBL id, e.g. "
                                          "CHEMBL1217643, and click Retrieve "
                                          "to get target information "
                                          "automatically.")

    description = models.TextField(default='')
    organism = models.TextField(default='')
    assay_type = models.CharField(max_length=1, default='U', choices=ASSAYTYPES)
    journal = models.TextField(default='')
    strain = models.TextField(default='')

    pubchem_id = models.TextField('PubChem ID', default='')
    source = models.TextField(default='')
    source_id = models.TextField(default='')
    name = models.TextField(default='', verbose_name="Assay Name")

    target = models.ForeignKey('Target', default=None, verbose_name="Target", null=True, blank=True)

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
        ordering = ('compound', 'bioactivity_type',)

    assay = models.ForeignKey(Assay)
    compound = models.ForeignKey('compounds.Compound',
                                 related_name='bioactivity_compound')
    parent_compound = models.ForeignKey('compounds.Compound',
                                        related_name='bioactivity_parent')

    # Target is slated to be added to assay instead
    target = models.ForeignKey(Target)
    target_confidence = models.IntegerField(blank=True, null=True)

    bioactivity_type = models.TextField(verbose_name="name", default='')

    standard_name = models.TextField(default='')
    operator = models.TextField(default='')

    units = models.TextField(default='')
    value = models.FloatField(blank=True, null=True)

    standardized_units = models.TextField(verbose_name="std units",
                                          default='')
    standardized_value = models.FloatField(verbose_name="std vals",
                                           blank=True,
                                           null=True)

    activity_comment = models.TextField(default='')
    reference = models.TextField(default='')
    name_in_reference = models.TextField(default='')

    # Use ChEMBL Assay Type to clarify unclear names like "Activity"
    # Removed for now
    # chembl_assay_type = models.TextField(blank=True, null=True, default='')

    def organism(self):
        return self.target.organism

    def __unicode__(self):
        return u'{}: {} {}'.format(
            self.compound,
            self.bioactivity_type,
            self.target.name
        )


class BioactivityType(LockableModel):
    class Meta(object):
        ordering = ('chembl_bioactivity','chembl_unit', )
    chembl_bioactivity = models.TextField(default='')
    chembl_unit = models.TextField(default='')
    scale_factor = models.FloatField(default=1,blank=True, null=True)
    mass_flag = models.CharField(max_length=8,default='N',choices=(('Y', 'Yes'),
                                                        ('N', 'No')))
    standard_name = models.TextField(default='')
    description = models.TextField(default='')
    standard_unit = models.TextField(default='')

    def __unicode__(self):
        return unicode(self.standard_name)


class PubChemBioactivity(LockableModel):
    # TextFields and CharFields have no performace benefits over eachother, but may want to use CharFields for clarity
    assay = models.ForeignKey('Assay', blank=True, null=True)

    # It makes sense just to add the PubChem CID to the compound then just use a FK
    #compound_id = models.TextField(verbose_name="Compound ID")
    compound = models.ForeignKey('compounds.Compound')

    # Target is slated to be added to assay instead
    target = models.ForeignKey('Target', default=None, verbose_name="Target", null=True, blank=True)

    # Value is required
    value = models.FloatField(verbose_name="Value (uM)")

    # Not required?
    # TODO Consider making this a FK to bioactivity types
    # TODO Or, perhaps we should make another table for PubChem types?
    activity_name = models.TextField(default='', verbose_name="Activity Name")

    # Normalized value for visualization and so on
    # Be sure to normalize on bioactivity-target pair across the entire database
    normalized_value = models.FloatField(blank=True,
                                        null=True,
                                        verbose_name="Value (uM)")


# TODO PubChem Bioactivity Type? and PubChem targets
# To following table may eventually be merged into the existing bioactivty type table
# Deliberating, is it really worthwhile to make a model with only one field?
#class PubChemBioactivityType(LockableModel):
#    name = models.TextField(default='')


# TODO PubChemTarget model is slated for removal
class PubChemTarget(LockableModel):
    name = models.TextField(default='', help_text="Preferred target name.")

    # May be difficult to acquire
    #synonyms = models.TextField(null=True, blank=True)

    # The GI is what is given by a PubChem assay
    # Optional, not all targets will have this
    GI = models.TextField('NCBI GI',
                          null=True,
                          blank=True)

    # Target type is not always listed: not required
    target_type = models.TextField(default='')

    # Organism is not always listed: not required
    organism = models.TextField(default='')

    def __unicode__(self):
        return unicode(self.name)


# TODO PubChemAssay model is slated for removal
class PubChemAssay(LockableModel):
    # Source is an optional field showing where PubChem pulled their data
    source = models.TextField(default='')

    source_id = models.TextField(default='')

    # PubChem ID
    aid = models.TextField(verbose_name="Assay ID")

    # Not required?
    name = models.TextField(default='', verbose_name="Assay Name")

    description = models.TextField(default='')

    def __unicode__(self):
        return unicode(self.aid)
