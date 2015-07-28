from django.db import models
from mps.base.models import LockableModel


CHEMBL = None

def get_chembl_handle():

    from bioservices import ChEMBL as ChEMBLdb
    global CHEMBL
    if CHEMBL is None:
        CHEMBL = ChEMBLdb()
    return CHEMBL


FIELDS = {
    'acdAcidicPka': 'acidic_pka',
    'acdBasicPka': 'basic_pka',
    'acdLogd': 'logd',
    'acdLogp': 'logp',
    'alogp': 'alogp',
    'chemblId': 'chemblid',
    'knownDrug': 'known_drug',
    'medChemFriendly': 'medchem_friendly',
    'molecularFormula': 'molecular_formula',
    'molecularWeight': 'molecular_weight',
    'numRo5Violations': 'ro5_violations',
    'passesRuleOfThree': 'ro3_passes',
    'preferredCompoundName': 'name',
    'rotatableBonds': 'rotatable_bonds',
    'smiles': 'smiles',
    'species': 'species',
    'stdInChiKey': 'inchikey',
    'synonyms': 'synonyms'
}


def chembl_compound(chemblid):
    chembl = get_chembl_handle()
    data = chembl.get_compounds_by_chemblId(str(chemblid))['compound']
    return {
        FIELDS[key]: value for key, value in data.items()
        if key in FIELDS
    }


class Compound(LockableModel):

    #compound_id = AutoField(primary_key=True)
    # The name, rather than the chemblid and/or inchikey, is unique
    name = models.CharField(max_length=200, unique=True,
        help_text="Preferred compound name.")
    synonyms = models.TextField(max_length=4000, default='')
    tags = models.TextField(default='', help_text="Tags for the compound (EPA, NCATS, etc.)")

    # External identifiers are checked for uniqueness in form's clean
    # Not optimal, but other solutions did not seem to work (editing save, so on)
    chemblid = models.CharField('ChEMBL ID', max_length=20, default='',
        help_text="Enter a ChEMBL id, e.g. CHEMBL25, and click Retrieve to "
                  "get compound information automatically.")

    # Pubchem ID
    pubchemid = models.CharField(verbose_name='PubChem ID', max_length=40, null=True, blank=True)

    # standard names/identifiers
    inchikey = models.CharField('InChI key', max_length=27,
        default='',
        help_text="IUPAC standard InChI key for the compound")
    smiles = models.CharField(max_length=1000,
        default='',
        help_text="Canonical smiles, generated using pipeline pilot.")

    # molecular properties
    molecular_formula = models.CharField(max_length=40,
        default='',
        help_text="Molecular formula of compound.")
    molecular_weight = models.FloatField(
        null=True, blank=True,
        help_text="Molecular weight of the compound")
    rotatable_bonds = models.IntegerField(
        null=True, blank=True,
        help_text="Number of rotatable bonds.")

    # some calculated properties
    acidic_pka = models.FloatField("Acidic pKa",
        null=True, blank=True,
        help_text="The most acidic pKa calculated using ACDlabs.")
    basic_pka = models.FloatField("Basic pKa",
        null=True, blank=True,
        help_text="The most basic pKa calculated using ACDlabs.")
    logp = models.FloatField("LogP",
        null=True, blank=True,
        help_text="The calculated octanol/water partition coefficient using "
                  "ACDlabs")
    logd = models.FloatField("LogD",
        null=True, blank=True,
        help_text="The calculated octanol/water distribution "
                  "coefficient at pH7.4 using ACDlabs.")
    alogp = models.FloatField('ALogP',
        null=True, blank=True,
        help_text="Calculated ALogP.")

    # drug related properties
    known_drug = models.BooleanField('Known drug?',
        default=False)
    medchem_friendly = models.BooleanField('Med Chem friendly?',
        default=False)
    ro5_violations = models.IntegerField('Rule of 5 violations',
        null=True, blank=True,
        help_text="Number of properties defined in Lipinski's Rule of 5 (RO5) "
                  "that the compound fails.")
    ro3_passes = models.BooleanField('Passes rule of 3?',
        default=False,
        help_text="Rule of 3 passes.  It is suggested "
                  "that compounds that pass all these criteria are"
                  "more likely to be hits in fragment screening.")
    species = models.CharField('Molecular species', max_length=10,
        default='',
        help_text="A description of the predominant species occurring at pH "
                  "7.4 and can be acid, base, neutral or zwitterion.")


    last_update = models.DateField(blank=True, null=True,
        help_text="Last time when activities associated with the compound were"
                  " updated.")

    class Meta(object):
        ordering = ('name', )

    def __unicode__(self):

        return u'{0}'.format(self.name)

    def chembl_link(self):

        if self.chemblid:
            return (u'<a href="https://www.ebi.ac.uk/chembl/compound/inspect/'
                    '{0}" target="_blank">{0}</a>').format(self.chemblid)
        else:
            return u''

    chembl_link.allow_tags = True
    chembl_link.short_description = 'ChEMBL ID'

    def thumb_src(self):

        if self.chemblid:
            return (u'https://www.ebi.ac.uk/chembldb/compound/'
                    'displayimage/' + self.chemblid)
        else:
            return u''

    def thumb(self):

        url = self.thumb_src()
        if url:
            return (u'<img src="{}" />').format(url)
        else:
            return u''

    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'

    def image(self):

        url = self.image_src()
        if url:
            return (u'<img src="{}" />').format(url)
        else:
            return u''

    def image_src(self):

        if self.chemblid:
            return (u'https://www.ebi.ac.uk/chembldb/compound/'
                    'displayimage_large/' + self.chemblid)
        else:
            return u''

    image.allow_tags = True
    image.short_description = 'Image'

    def get_absolute_url(self):
        return "/compounds/"
