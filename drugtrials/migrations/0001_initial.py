# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Species'
        db.create_table(u'drugtrials_species', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('species_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal(u'drugtrials', ['Species'])

        # Adding model 'TrialSource'
        db.create_table(u'drugtrials_trialsource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('source_website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['TrialSource'])

        # Adding model 'DrugTrial'
        db.create_table(u'drugtrials_drugtrial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='drugtrial_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='drugtrial_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.TrialSource'])),
            ('compound', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['compounds.Compound'])),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(default='1', to=orm['drugtrials.Species'], null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='U', max_length=1, null=True, blank=True)),
            ('population_size', self.gf('django.db.models.fields.CharField')(default='1', max_length=50, null=True, blank=True)),
            ('age_average', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('age_max', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('age_min', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('age_unit', self.gf('django.db.models.fields.CharField')(default='Y', max_length=1, null=True, blank=True)),
            ('weight_average', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('weight_max', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('weight_min', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('weight_unit', self.gf('django.db.models.fields.CharField')(default='L', max_length=1, null=True, blank=True)),
            ('trial_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('trial_sub_type', self.gf('django.db.models.fields.CharField')(default='C', max_length=1)),
            ('trial_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('source_link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('references', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['DrugTrial'])

        # Adding model 'TestType'
        db.create_table(u'drugtrials_testtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['TestType'])

        # Adding model 'Test'
        db.create_table(u'drugtrials_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='test_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='test_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('organ_model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['microdevices.OrganModel'], null=True, blank=True)),
            ('test_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.TestType'])),
            ('test_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('test_unit', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('organ', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cellsamples.Organ'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['Test'])

        # Adding unique constraint on 'Test', fields ['test_type', 'test_name']
        db.create_unique(u'drugtrials_test', ['test_type_id', 'test_name'])

        # Adding model 'FindingType'
        db.create_table(u'drugtrials_findingtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('finding_type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['FindingType'])

        # Adding model 'Finding'
        db.create_table(u'drugtrials_finding', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('finding_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.FindingType'], null=True, blank=True)),
            ('finding_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('finding_unit', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('organ', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cellsamples.Organ'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['Finding'])

        # Adding unique constraint on 'Finding', fields ['organ', 'finding_name']
        db.create_unique(u'drugtrials_finding', ['organ_id', 'finding_name'])

        # Adding model 'ResultDescriptor'
        db.create_table(u'drugtrials_resultdescriptor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result_descriptor', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal(u'drugtrials', ['ResultDescriptor'])

        # Adding model 'Units'
        db.create_table(u'drugtrials_units', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
        ))
        db.send_create_signal(u'drugtrials', ['Units'])

        # Adding model 'TestResult'
        db.create_table(u'drugtrials_testresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('drug_trial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.DrugTrial'])),
            ('test_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.Test'], null=True, blank=True)),
            ('test_time', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('time_units', self.gf('django.db.models.fields.CharField')(default='w', max_length=1)),
            ('result', self.gf('django.db.models.fields.CharField')(default='1', max_length=8, null=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.CharField')(default='-1', max_length=5, null=True, blank=True)),
            ('sub_participant_size', self.gf('django.db.models.fields.FloatField')(default=1, null=True, blank=True)),
            ('percent_max', self.gf('django.db.models.fields.FloatField')(default=1, null=True, blank=True)),
            ('descriptor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.ResultDescriptor'], null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('units', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.Units'], null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['TestResult'])

        # Adding model 'FindingResult'
        db.create_table(u'drugtrials_findingresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('drug_trial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.DrugTrial'])),
            ('finding_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.Finding'])),
            ('finding_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.FindingType'], null=True, blank=True)),
            ('finding_time', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('time_units', self.gf('django.db.models.fields.CharField')(default='w', max_length=1)),
            ('result', self.gf('django.db.models.fields.CharField')(default='1', max_length=8)),
            ('severity', self.gf('django.db.models.fields.CharField')(default='-1', max_length=5)),
            ('sub_participant_size', self.gf('django.db.models.fields.FloatField')(default=1, null=True, blank=True)),
            ('percent_max', self.gf('django.db.models.fields.FloatField')(default=1, null=True, blank=True)),
            ('descriptor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.ResultDescriptor'], null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'drugtrials', ['FindingResult'])


    def backwards(self, orm):
        # Removing unique constraint on 'Finding', fields ['organ', 'finding_name']
        db.delete_unique(u'drugtrials_finding', ['organ_id', 'finding_name'])

        # Removing unique constraint on 'Test', fields ['test_type', 'test_name']
        db.delete_unique(u'drugtrials_test', ['test_type_id', 'test_name'])

        # Deleting model 'Species'
        db.delete_table(u'drugtrials_species')

        # Deleting model 'TrialSource'
        db.delete_table(u'drugtrials_trialsource')

        # Deleting model 'DrugTrial'
        db.delete_table(u'drugtrials_drugtrial')

        # Deleting model 'TestType'
        db.delete_table(u'drugtrials_testtype')

        # Deleting model 'Test'
        db.delete_table(u'drugtrials_test')

        # Deleting model 'FindingType'
        db.delete_table(u'drugtrials_findingtype')

        # Deleting model 'Finding'
        db.delete_table(u'drugtrials_finding')

        # Deleting model 'ResultDescriptor'
        db.delete_table(u'drugtrials_resultdescriptor')

        # Deleting model 'Units'
        db.delete_table(u'drugtrials_units')

        # Deleting model 'TestResult'
        db.delete_table(u'drugtrials_testresult')

        # Deleting model 'FindingResult'
        db.delete_table(u'drugtrials_findingresult')


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
        u'cellsamples.cellsubtype': {
            'Meta': {'object_name': 'CellSubtype'},
            'cell_subtype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cellsamples.celltype': {
            'Meta': {'ordering': "('cell_type',)", 'object_name': 'CellType'},
            'cell_subtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.CellSubtype']"}),
            'cell_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"}),
            'species': ('django.db.models.fields.CharField', [], {'default': "'Human'", 'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'cellsamples.organ': {
            'Meta': {'ordering': "('organ_name',)", 'object_name': 'Organ'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organ_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
        },
        u'drugtrials.drugtrial': {
            'Meta': {'object_name': 'DrugTrial'},
            'age_average': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'age_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'age_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'age_unit': ('django.db.models.fields.CharField', [], {'default': "'Y'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'compound': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['compounds.Compound']"}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drugtrial_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drugtrial_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'population_size': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.TrialSource']"}),
            'source_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'default': "'1'", 'to': u"orm['drugtrials.Species']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'trial_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'trial_sub_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'trial_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'weight_average': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'weight_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'weight_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'weight_unit': ('django.db.models.fields.CharField', [], {'default': "'L'", 'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.finding': {
            'Meta': {'ordering': "('organ', 'finding_name')", 'unique_together': "[('organ', 'finding_name')]", 'object_name': 'Finding'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'finding_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'finding_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.FindingType']", 'null': 'True', 'blank': 'True'}),
            'finding_unit': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.findingresult': {
            'Meta': {'object_name': 'FindingResult'},
            'descriptor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.ResultDescriptor']", 'null': 'True', 'blank': 'True'}),
            'drug_trial': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.DrugTrial']"}),
            'finding_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.Finding']"}),
            'finding_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'finding_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.FindingType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_max': ('django.db.models.fields.FloatField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '8'}),
            'severity': ('django.db.models.fields.CharField', [], {'default': "'-1'", 'max_length': '5'}),
            'sub_participant_size': ('django.db.models.fields.FloatField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'time_units': ('django.db.models.fields.CharField', [], {'default': "'w'", 'max_length': '1'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.findingtype': {
            'Meta': {'ordering': "('finding_type',)", 'object_name': 'FindingType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'finding_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'drugtrials.resultdescriptor': {
            'Meta': {'object_name': 'ResultDescriptor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result_descriptor': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'drugtrials.species': {
            'Meta': {'object_name': 'Species'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'species_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'drugtrials.test': {
            'Meta': {'ordering': "('organ', 'test_name')", 'unique_together': "[('test_type', 'test_name')]", 'object_name': 'Test'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'test_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'test_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True', 'blank': 'True'}),
            'organ_model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.OrganModel']", 'null': 'True', 'blank': 'True'}),
            'test_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'test_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.TestType']"}),
            'test_unit': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.testresult': {
            'Meta': {'object_name': 'TestResult'},
            'descriptor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.ResultDescriptor']", 'null': 'True', 'blank': 'True'}),
            'drug_trial': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.DrugTrial']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_max': ('django.db.models.fields.FloatField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'default': "'-1'", 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sub_participant_size': ('django.db.models.fields.FloatField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'test_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.Test']", 'null': 'True', 'blank': 'True'}),
            'test_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_units': ('django.db.models.fields.CharField', [], {'default': "'w'", 'max_length': '1'}),
            'units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.Units']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.testtype': {
            'Meta': {'object_name': 'TestType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        },
        u'drugtrials.trialsource': {
            'Meta': {'object_name': 'TrialSource'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'source_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.units': {
            'Meta': {'object_name': 'Units'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'})
        },
        u'microdevices.manufacturer': {
            'Manufacturer_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Manufacturer'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microdevice': {
            'Meta': {'object_name': 'Microdevice'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'center': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.MicrophysiologyCenter']", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microdevice_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'device_cross_section_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_fluid_volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device_fluid_volume_unit': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'device_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'device_length': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'device_size_unit': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'device_thickness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device_width': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microdevice_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True', 'blank': 'True'}),
            'substrate_material': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'substrate_thickness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microphysiologycenter': {
            'Meta': {'object_name': 'MicrophysiologyCenter'},
            'center_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'center_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'microdevices.organmodel': {
            'Meta': {'object_name': 'OrganModel'},
            'cell_type': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'organmodels'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['cellsamples.CellType']"}),
            'center': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.MicrophysiologyCenter']", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organmodel_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.Microdevice']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organmodel_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"})
        }
    }

    complete_apps = ['drugtrials']