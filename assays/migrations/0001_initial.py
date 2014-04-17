# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AssayModelType'
        db.create_table(u'assays_assaymodeltype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaymodeltype_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaymodeltype_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('assay_type_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('assay_type_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'assays', ['AssayModelType'])

        # Adding model 'AssayModel'
        db.create_table(u'assays_assaymodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaymodel_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaymodel_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('assay_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('assay_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayModelType'])),
            ('version_number', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('assay_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('assay_protocol_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'assays', ['AssayModel'])

        # Adding model 'AssayLayoutFormat'
        db.create_table(u'assays_assaylayoutformat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaylayoutformat_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaylayoutformat_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('layout_format_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('number_of_rows', self.gf('django.db.models.fields.IntegerField')()),
            ('number_of_columns', self.gf('django.db.models.fields.IntegerField')()),
            ('row_labels', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('column_labels', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal(u'assays', ['AssayLayoutFormat'])

        # Adding model 'AssayBaseLayout'
        db.create_table(u'assays_assaybaselayout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaybaselayout_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaybaselayout_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('base_layout_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('layout_format', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayLayoutFormat'])),
        ))
        db.send_create_signal(u'assays', ['AssayBaseLayout'])

        # Adding model 'AssayWellType'
        db.create_table(u'assays_assaywelltype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaywelltype_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaywelltype_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('well_type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('well_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('background_color', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'assays', ['AssayWellType'])

        # Adding model 'AssayWell'
        db.create_table(u'assays_assaywell', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaywell_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaywell_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('base_layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayBaseLayout'])),
            ('well_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayWellType'])),
            ('row', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('column', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'assays', ['AssayWell'])

        # Adding unique constraint on 'AssayWell', fields ['base_layout', 'row', 'column']
        db.create_unique(u'assays_assaywell', ['base_layout_id', 'row', 'column'])

        # Adding model 'AssayLayout'
        db.create_table(u'assays_assaylayout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaylayout_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaylayout_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('layout_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('base_layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayBaseLayout'])),
        ))
        db.send_create_signal(u'assays', ['AssayLayout'])

        # Adding model 'AssayTimepoint'
        db.create_table(u'assays_assaytimepoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assay_layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayLayout'])),
            ('timepoint', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('row', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('column', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'assays', ['AssayTimepoint'])

        # Adding model 'AssayCompound'
        db.create_table(u'assays_assaycompound', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assay_layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayLayout'])),
            ('compound', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['compounds.Compound'])),
            ('concentration', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('concentration_unit', self.gf('django.db.models.fields.CharField')(default='\xce\xbcM', max_length=64)),
            ('row', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('column', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'assays', ['AssayCompound'])

        # Adding model 'AssayReadout'
        db.create_table(u'assays_assayreadout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assay_device_readout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayDeviceReadout'])),
            ('row', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('column', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'assays', ['AssayReadout'])

        # Adding model 'AssayDeviceReadout'
        db.create_table(u'assays_assaydevicereadout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaydevicereadout_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assaydevicereadout_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('assay_device_id', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('cell_sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cellsamples.CellSample'])),
            ('organ_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cellsamples.Organ'], null=True)),
            ('cellsample_density', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('cellsample_density_unit', self.gf('django.db.models.fields.CharField')(default='ML', max_length=8)),
            ('assay_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayModel'], null=True)),
            ('assay_layout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayLayout'])),
            ('microdevice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['microdevices.Microdevice'])),
            ('reader_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assays.AssayReader'])),
            ('readout_unit', self.gf('django.db.models.fields.CharField')(default='RFU', max_length=16)),
            ('readout_type', self.gf('django.db.models.fields.CharField')(default='E', max_length=2)),
            ('timeunit', self.gf('django.db.models.fields.CharField')(default='minutes', max_length=16)),
            ('treatment_time_length', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('timepoint', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('time_interval', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('assay_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('readout_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('notebook', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('notebook_page', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('scientist', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'assays', ['AssayDeviceReadout'])

        # Adding model 'AssayReader'
        db.create_table(u'assays_assayreader', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assayreader_created-by', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assayreader_modified-by', null=True, to=orm['auth.User'])),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reader_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('reader_type', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'assays', ['AssayReader'])


    def backwards(self, orm):
        # Removing unique constraint on 'AssayWell', fields ['base_layout', 'row', 'column']
        db.delete_unique(u'assays_assaywell', ['base_layout_id', 'row', 'column'])

        # Deleting model 'AssayModelType'
        db.delete_table(u'assays_assaymodeltype')

        # Deleting model 'AssayModel'
        db.delete_table(u'assays_assaymodel')

        # Deleting model 'AssayLayoutFormat'
        db.delete_table(u'assays_assaylayoutformat')

        # Deleting model 'AssayBaseLayout'
        db.delete_table(u'assays_assaybaselayout')

        # Deleting model 'AssayWellType'
        db.delete_table(u'assays_assaywelltype')

        # Deleting model 'AssayWell'
        db.delete_table(u'assays_assaywell')

        # Deleting model 'AssayLayout'
        db.delete_table(u'assays_assaylayout')

        # Deleting model 'AssayTimepoint'
        db.delete_table(u'assays_assaytimepoint')

        # Deleting model 'AssayCompound'
        db.delete_table(u'assays_assaycompound')

        # Deleting model 'AssayReadout'
        db.delete_table(u'assays_assayreadout')

        # Deleting model 'AssayDeviceReadout'
        db.delete_table(u'assays_assaydevicereadout')

        # Deleting model 'AssayReader'
        db.delete_table(u'assays_assayreader')


    models = {
        u'assays.assaybaselayout': {
            'Meta': {'object_name': 'AssayBaseLayout'},
            'base_layout_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaybaselayout_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout_format': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayLayoutFormat']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaybaselayout_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assays.assaycompound': {
            'Meta': {'object_name': 'AssayCompound'},
            'assay_layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayLayout']"}),
            'column': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'compound': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['compounds.Compound']"}),
            'concentration': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'concentration_unit': ('django.db.models.fields.CharField', [], {'default': "'\\xce\\xbcM'", 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'assays.assaydevicereadout': {
            'Meta': {'object_name': 'AssayDeviceReadout'},
            'assay_device_id': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'assay_layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayLayout']"}),
            'assay_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayModel']", 'null': 'True'}),
            'assay_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'cell_sample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.CellSample']"}),
            'cellsample_density': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cellsample_density_unit': ('django.db.models.fields.CharField', [], {'default': "'ML'", 'max_length': '8'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaydevicereadout_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'microdevice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['microdevices.Microdevice']"}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaydevicereadout_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'notebook': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'notebook_page': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'organ_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Organ']", 'null': 'True'}),
            'reader_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayReader']"}),
            'readout_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'readout_type': ('django.db.models.fields.CharField', [], {'default': "'E'", 'max_length': '2'}),
            'readout_unit': ('django.db.models.fields.CharField', [], {'default': "'RFU'", 'max_length': '16'}),
            'scientist': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'time_interval': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'timepoint': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'timeunit': ('django.db.models.fields.CharField', [], {'default': "'minutes'", 'max_length': '16'}),
            'treatment_time_length': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'assays.assaylayout': {
            'Meta': {'object_name': 'AssayLayout'},
            'base_layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayBaseLayout']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaylayout_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaylayout_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assays.assaylayoutformat': {
            'Meta': {'object_name': 'AssayLayoutFormat'},
            'column_labels': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaylayoutformat_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout_format_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaylayoutformat_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'number_of_columns': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_rows': ('django.db.models.fields.IntegerField', [], {}),
            'row_labels': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        u'assays.assaymodel': {
            'Meta': {'object_name': 'AssayModel'},
            'assay_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'assay_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'assay_protocol_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'assay_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayModelType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodel_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodel_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'version_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'assays.assaymodeltype': {
            'Meta': {'object_name': 'AssayModelType'},
            'assay_type_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'assay_type_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodeltype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaymodeltype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'assays.assayreader': {
            'Meta': {'object_name': 'AssayReader'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assayreader_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assayreader_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'reader_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reader_type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'assays.assayreadout': {
            'Meta': {'object_name': 'AssayReadout'},
            'assay_device_readout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayDeviceReadout']"}),
            'column': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'assays.assaytimepoint': {
            'Meta': {'object_name': 'AssayTimepoint'},
            'assay_layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayLayout']"}),
            'column': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'timepoint': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'assays.assaywell': {
            'Meta': {'unique_together': "[('base_layout', 'row', 'column')]", 'object_name': 'AssayWell'},
            'base_layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayBaseLayout']"}),
            'column': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaywell_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaywell_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'row': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'well_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assays.AssayWellType']"})
        },
        u'assays.assaywelltype': {
            'Meta': {'object_name': 'AssayWellType'},
            'background_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaywelltype_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assaywelltype_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'well_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'well_type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
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
        u'cellsamples.cellsample': {
            'Meta': {'object_name': 'CellSample'},
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cell_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cell_source': ('django.db.models.fields.CharField', [], {'default': "'Primary'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'cell_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.CellType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cellsample_created-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isolation_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'isolation_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'isolation_notes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cellsample_modified-by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'patient_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'patient_condition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'patient_gender': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1', 'blank': 'True'}),
            'percent_viability': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'product_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'receipt_date': ('django.db.models.fields.DateField', [], {}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cellsamples.Supplier']"}),
            'viable_count': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'viable_count_unit': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1', 'blank': 'True'})
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
        u'cellsamples.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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
        }
    }

    complete_apps = ['assays']