# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Assay.chemblid'
        db.alter_column(u'bioactivities_assay', 'chemblid', self.gf('django.db.models.fields.TextField')(unique=True, null=True))

        # Changing field 'Assay.description'
        db.alter_column(u'bioactivities_assay', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Assay.journal'
        db.alter_column(u'bioactivities_assay', 'journal', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Assay.strain'
        db.alter_column(u'bioactivities_assay', 'strain', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Assay.organism'
        db.alter_column(u'bioactivities_assay', 'organism', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Target.chemblid'
        db.alter_column(u'bioactivities_target', 'chemblid', self.gf('django.db.models.fields.TextField')(unique=True, null=True))

        # Changing field 'Target.name'
        db.alter_column(u'bioactivities_target', 'name', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Target.gene_names'
        db.alter_column(u'bioactivities_target', 'gene_names', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Target.target_type'
        db.alter_column(u'bioactivities_target', 'target_type', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Target.uniprot_accession'
        db.alter_column(u'bioactivities_target', 'uniprot_accession', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Target.synonyms'
        db.alter_column(u'bioactivities_target', 'synonyms', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Target.organism'
        db.alter_column(u'bioactivities_target', 'organism', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Target.description'
        db.alter_column(u'bioactivities_target', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.reference'
        db.alter_column(u'bioactivities_bioactivity', 'reference', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.operator'
        db.alter_column(u'bioactivities_bioactivity', 'operator', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.units'
        db.alter_column(u'bioactivities_bioactivity', 'units', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.name_in_reference'
        db.alter_column(u'bioactivities_bioactivity', 'name_in_reference', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.bioactivity_type'
        db.alter_column(u'bioactivities_bioactivity', 'bioactivity_type', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.standardized_units'
        db.alter_column(u'bioactivities_bioactivity', 'standardized_units', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Bioactivity.activity_comment'
        db.alter_column(u'bioactivities_bioactivity', 'activity_comment', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Assay.chemblid'
        db.alter_column(u'bioactivities_assay', 'chemblid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20, null=True))

        # Changing field 'Assay.description'
        db.alter_column(u'bioactivities_assay', 'description', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True))

        # Changing field 'Assay.journal'
        db.alter_column(u'bioactivities_assay', 'journal', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Assay.strain'
        db.alter_column(u'bioactivities_assay', 'strain', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Assay.organism'
        db.alter_column(u'bioactivities_assay', 'organism', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Target.chemblid'
        db.alter_column(u'bioactivities_target', 'chemblid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20, null=True))

        # Changing field 'Target.name'
        db.alter_column(u'bioactivities_target', 'name', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'Target.gene_names'
        db.alter_column(u'bioactivities_target', 'gene_names', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

        # Changing field 'Target.target_type'
        db.alter_column(u'bioactivities_target', 'target_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Target.uniprot_accession'
        db.alter_column(u'bioactivities_target', 'uniprot_accession', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Target.synonyms'
        db.alter_column(u'bioactivities_target', 'synonyms', self.gf('django.db.models.fields.TextField')(max_length=4000, null=True))

        # Changing field 'Target.organism'
        db.alter_column(u'bioactivities_target', 'organism', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Target.description'
        db.alter_column(u'bioactivities_target', 'description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True))

        # Changing field 'Bioactivity.reference'
        db.alter_column(u'bioactivities_bioactivity', 'reference', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Bioactivity.operator'
        db.alter_column(u'bioactivities_bioactivity', 'operator', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Bioactivity.units'
        db.alter_column(u'bioactivities_bioactivity', 'units', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Bioactivity.name_in_reference'
        db.alter_column(u'bioactivities_bioactivity', 'name_in_reference', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Bioactivity.bioactivity_type'
        db.alter_column(u'bioactivities_bioactivity', 'bioactivity_type', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Bioactivity.standardized_units'
        db.alter_column(u'bioactivities_bioactivity', 'standardized_units', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Bioactivity.activity_comment'
        db.alter_column(u'bioactivities_bioactivity', 'activity_comment', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'bioactivities.assay': {
            'Meta': {'ordering': "('chemblid',)", 'object_name': 'Assay'},
            'assay_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'chemblid': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assay_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assay_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organism': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assay_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'strain': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'bioactivities.bioactivity': {
            'Meta': {'unique_together': "(('assay', 'target', 'compound'),)", 'object_name': 'Bioactivity'},
            'activity_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'assay': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bioactivities.Assay']"}),
            'bioactivity_type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'compound': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bioactivity_compound'", 'to': u"orm['compounds.Compound']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bioactivity_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bioactivity_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name_in_reference': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'operator': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'parent_compound': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bioactivity_parent'", 'to': u"orm['compounds.Compound']"}),
            'reference': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bioactivity_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'standardized_units': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'standardized_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bioactivities.Target']"}),
            'target_confidence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'units': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'bioactivities.target': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Target'},
            'chemblid': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gene_names': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'organism': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'synonyms': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'target_type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'uniprot_accession': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'compounds.compound': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Compound'},
            'acidic_pka': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'alogp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'basic_pka': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'chemblid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'compound_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inchikey': ('django.db.models.fields.CharField', [], {'max_length': '27', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'known_drug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_update': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'logd': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'logp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'medchem_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'compound_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'molecular_formula': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'molecular_weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ro3_passes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ro5_violations': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rotatable_bonds': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'compound_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'smiles': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'synonyms': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bioactivities']