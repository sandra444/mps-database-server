# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FindingType.created_by'
        db.add_column(u'drugtrials_findingtype', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='findingtype_created-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'FindingType.created_on'
        db.add_column(u'drugtrials_findingtype', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'FindingType.modified_by'
        db.add_column(u'drugtrials_findingtype', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='findingtype_modified-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'FindingType.modified_on'
        db.add_column(u'drugtrials_findingtype', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'FindingType.signed_off_by'
        db.add_column(u'drugtrials_findingtype', 'signed_off_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='findingtype_signed_off_by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'FindingType.signed_off_date'
        db.add_column(u'drugtrials_findingtype', 'signed_off_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'FindingType.locked'
        db.add_column(u'drugtrials_findingtype', 'locked',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Species.created_by'
        db.add_column(u'drugtrials_species', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='species_created-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Species.created_on'
        db.add_column(u'drugtrials_species', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Species.modified_by'
        db.add_column(u'drugtrials_species', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='species_modified-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Species.modified_on'
        db.add_column(u'drugtrials_species', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Species.signed_off_by'
        db.add_column(u'drugtrials_species', 'signed_off_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='species_signed_off_by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Species.signed_off_date'
        db.add_column(u'drugtrials_species', 'signed_off_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Species.locked'
        db.add_column(u'drugtrials_species', 'locked',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'FindingResult.finding_type'
        db.delete_column(u'drugtrials_findingresult', 'finding_type_id')

        # Adding field 'TestType.created_by'
        db.add_column(u'drugtrials_testtype', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='testtype_created-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'TestType.created_on'
        db.add_column(u'drugtrials_testtype', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TestType.modified_by'
        db.add_column(u'drugtrials_testtype', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='testtype_modified-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'TestType.modified_on'
        db.add_column(u'drugtrials_testtype', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TestType.signed_off_by'
        db.add_column(u'drugtrials_testtype', 'signed_off_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='testtype_signed_off_by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'TestType.signed_off_date'
        db.add_column(u'drugtrials_testtype', 'signed_off_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'TestType.locked'
        db.add_column(u'drugtrials_testtype', 'locked',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ResultDescriptor.created_by'
        db.add_column(u'drugtrials_resultdescriptor', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resultdescriptor_created-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'ResultDescriptor.created_on'
        db.add_column(u'drugtrials_resultdescriptor', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ResultDescriptor.modified_by'
        db.add_column(u'drugtrials_resultdescriptor', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resultdescriptor_modified-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'ResultDescriptor.modified_on'
        db.add_column(u'drugtrials_resultdescriptor', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ResultDescriptor.signed_off_by'
        db.add_column(u'drugtrials_resultdescriptor', 'signed_off_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resultdescriptor_signed_off_by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'ResultDescriptor.signed_off_date'
        db.add_column(u'drugtrials_resultdescriptor', 'signed_off_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'ResultDescriptor.locked'
        db.add_column(u'drugtrials_resultdescriptor', 'locked',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'TrialSource.created_by'
        db.add_column(u'drugtrials_trialsource', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='trialsource_created-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'TrialSource.created_on'
        db.add_column(u'drugtrials_trialsource', 'created_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TrialSource.modified_by'
        db.add_column(u'drugtrials_trialsource', 'modified_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='trialsource_modified-by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'TrialSource.modified_on'
        db.add_column(u'drugtrials_trialsource', 'modified_on',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TrialSource.signed_off_by'
        db.add_column(u'drugtrials_trialsource', 'signed_off_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='trialsource_signed_off_by', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'TrialSource.signed_off_date'
        db.add_column(u'drugtrials_trialsource', 'signed_off_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'TrialSource.locked'
        db.add_column(u'drugtrials_trialsource', 'locked',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FindingType.created_by'
        db.delete_column(u'drugtrials_findingtype', 'created_by_id')

        # Deleting field 'FindingType.created_on'
        db.delete_column(u'drugtrials_findingtype', 'created_on')

        # Deleting field 'FindingType.modified_by'
        db.delete_column(u'drugtrials_findingtype', 'modified_by_id')

        # Deleting field 'FindingType.modified_on'
        db.delete_column(u'drugtrials_findingtype', 'modified_on')

        # Deleting field 'FindingType.signed_off_by'
        db.delete_column(u'drugtrials_findingtype', 'signed_off_by_id')

        # Deleting field 'FindingType.signed_off_date'
        db.delete_column(u'drugtrials_findingtype', 'signed_off_date')

        # Deleting field 'FindingType.locked'
        db.delete_column(u'drugtrials_findingtype', 'locked')

        # Deleting field 'Species.created_by'
        db.delete_column(u'drugtrials_species', 'created_by_id')

        # Deleting field 'Species.created_on'
        db.delete_column(u'drugtrials_species', 'created_on')

        # Deleting field 'Species.modified_by'
        db.delete_column(u'drugtrials_species', 'modified_by_id')

        # Deleting field 'Species.modified_on'
        db.delete_column(u'drugtrials_species', 'modified_on')

        # Deleting field 'Species.signed_off_by'
        db.delete_column(u'drugtrials_species', 'signed_off_by_id')

        # Deleting field 'Species.signed_off_date'
        db.delete_column(u'drugtrials_species', 'signed_off_date')

        # Deleting field 'Species.locked'
        db.delete_column(u'drugtrials_species', 'locked')

        # Adding field 'FindingResult.finding_type'
        db.add_column(u'drugtrials_findingresult', 'finding_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['drugtrials.FindingType'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'TestType.created_by'
        db.delete_column(u'drugtrials_testtype', 'created_by_id')

        # Deleting field 'TestType.created_on'
        db.delete_column(u'drugtrials_testtype', 'created_on')

        # Deleting field 'TestType.modified_by'
        db.delete_column(u'drugtrials_testtype', 'modified_by_id')

        # Deleting field 'TestType.modified_on'
        db.delete_column(u'drugtrials_testtype', 'modified_on')

        # Deleting field 'TestType.signed_off_by'
        db.delete_column(u'drugtrials_testtype', 'signed_off_by_id')

        # Deleting field 'TestType.signed_off_date'
        db.delete_column(u'drugtrials_testtype', 'signed_off_date')

        # Deleting field 'TestType.locked'
        db.delete_column(u'drugtrials_testtype', 'locked')

        # Deleting field 'ResultDescriptor.created_by'
        db.delete_column(u'drugtrials_resultdescriptor', 'created_by_id')

        # Deleting field 'ResultDescriptor.created_on'
        db.delete_column(u'drugtrials_resultdescriptor', 'created_on')

        # Deleting field 'ResultDescriptor.modified_by'
        db.delete_column(u'drugtrials_resultdescriptor', 'modified_by_id')

        # Deleting field 'ResultDescriptor.modified_on'
        db.delete_column(u'drugtrials_resultdescriptor', 'modified_on')

        # Deleting field 'ResultDescriptor.signed_off_by'
        db.delete_column(u'drugtrials_resultdescriptor', 'signed_off_by_id')

        # Deleting field 'ResultDescriptor.signed_off_date'
        db.delete_column(u'drugtrials_resultdescriptor', 'signed_off_date')

        # Deleting field 'ResultDescriptor.locked'
        db.delete_column(u'drugtrials_resultdescriptor', 'locked')

        # Deleting field 'TrialSource.created_by'
        db.delete_column(u'drugtrials_trialsource', 'created_by_id')

        # Deleting field 'TrialSource.created_on'
        db.delete_column(u'drugtrials_trialsource', 'created_on')

        # Deleting field 'TrialSource.modified_by'
        db.delete_column(u'drugtrials_trialsource', 'modified_by_id')

        # Deleting field 'TrialSource.modified_on'
        db.delete_column(u'drugtrials_trialsource', 'modified_on')

        # Deleting field 'TrialSource.signed_off_by'
        db.delete_column(u'drugtrials_trialsource', 'signed_off_by_id')

        # Deleting field 'TrialSource.signed_off_date'
        db.delete_column(u'drugtrials_trialsource', 'signed_off_date')

        # Deleting field 'TrialSource.locked'
        db.delete_column(u'drugtrials_trialsource', 'locked')


    models = {
        u'assays.physicalunits': {
            'Meta': {'ordering': "['unit_type', 'unit']", 'object_name': 'PhysicalUnits'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'physicalunits_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'physicalunits_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'physicalunits_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'unit_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '2'})
        },
        u'assays.timeunits': {
            'Meta': {'ordering': "['unit_order']", 'object_name': 'TimeUnits'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'timeunits_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'timeunits_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'timeunits_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'unit_order': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
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
            'Meta': {'ordering': "('cell_subtype',)", 'object_name': 'CellSubtype'},
            'cell_subtype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cellsubtype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cellsubtype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cellsubtype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'cellsamples.celltype': {
            'Meta': {'ordering': "('species', 'cell_type', 'cell_subtype')", 'unique_together': "[('cell_type', 'species', 'cell_subtype')]", 'object_name': 'CellType'},
            'cell_subtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.CellSubtype']"}),
            'cell_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'celltype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'celltype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'celltype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.CharField', [], {'default': "'Human'", 'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'cellsamples.organ': {
            'Meta': {'ordering': "('organ_name',)", 'object_name': 'Organ'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organ_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organ_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organ_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
        },
        u'drugtrials.drugtrial': {
            'Meta': {'ordering': "('compound', 'species')", 'object_name': 'DrugTrial'},
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
            'references': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drugtrial_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'Meta': {'ordering': "('organ', 'finding_type', 'finding_name')", 'unique_together': "[('organ', 'finding_name')]", 'object_name': 'Finding'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'finding_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'finding_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'finding_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.FindingType']", 'null': 'True', 'blank': 'True'}),
            'finding_unit': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'finding_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'finding_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.findingresult': {
            'Meta': {'object_name': 'FindingResult'},
            'descriptor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.ResultDescriptor']", 'null': 'True', 'blank': 'True'}),
            'drug_trial': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.DrugTrial']"}),
            'finding_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.Finding']"}),
            'finding_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'percent_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '8'}),
            'severity': ('django.db.models.fields.CharField', [], {'default': "'-1'", 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'time_units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.TimeUnits']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.PhysicalUnits']", 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.findingtype': {
            'Meta': {'ordering': "('finding_type',)", 'object_name': 'FindingType'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'findingtype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'finding_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'findingtype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'findingtype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.resultdescriptor': {
            'Meta': {'ordering': "('result_descriptor',)", 'object_name': 'ResultDescriptor'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resultdescriptor_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resultdescriptor_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'result_descriptor': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resultdescriptor_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.species': {
            'Meta': {'ordering': "('species_name',)", 'object_name': 'Species'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'species_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'species_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'species_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'species_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'drugtrials.test': {
            'Meta': {'ordering': "('test_name', 'organ', 'test_type')", 'unique_together': "[('test_type', 'test_name')]", 'object_name': 'Test'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'test_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'test_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True', 'blank': 'True'}),
            'organ_model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.OrganModel']", 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'test_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'test_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'test_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.TestType']"}),
            'test_unit': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.testresult': {
            'Meta': {'object_name': 'TestResult'},
            'descriptor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.ResultDescriptor']", 'null': 'True', 'blank': 'True'}),
            'drug_trial': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.DrugTrial']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'percent_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'default': "'-1'", 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'test_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['drugtrials.Test']", 'null': 'True', 'blank': 'True'}),
            'test_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.TimeUnits']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value_units': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.PhysicalUnits']", 'null': 'True', 'blank': 'True'})
        },
        u'drugtrials.testtype': {
            'Meta': {'ordering': "('test_type',)", 'object_name': 'TestType'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'testtype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'testtype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'testtype_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'test_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        },
        u'drugtrials.trialsource': {
            'Meta': {'ordering': "('source_name',)", 'object_name': 'TrialSource'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'trialsource_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'trialsource_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'trialsource_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'source_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'source_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'microdevices.manufacturer': {
            'Manufacturer_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "('manufacturer_name',)", 'object_name': 'Manufacturer'},
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manufacturer_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manufacturer_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microdevice': {
            'Meta': {'ordering': "('device_name', 'organ')", 'object_name': 'Microdevice'},
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
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microdevice_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'substrate_material': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'substrate_thickness': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.microphysiologycenter': {
            'Meta': {'ordering': "('center_name',)", 'object_name': 'MicrophysiologyCenter'},
            'center_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'center_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'microphysiologycenter_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'microdevices.organmodel': {
            'Meta': {'ordering': "('model_name', 'organ')", 'object_name': 'OrganModel'},
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
            'organ': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']"}),
            'signed_off_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organmodel_signed_off_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'signed_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['drugtrials']