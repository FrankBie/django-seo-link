# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MatchType'
        db.create_table('seo_link_matchtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('seo_link', ['MatchType'])

        # Adding model 'ExcludePath'
        db.create_table('seo_link_excludepath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo_link.MatchType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pattern', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_global', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('seo_link', ['ExcludePath'])

        # Adding unique constraint on 'ExcludePath', fields ['type', 'pattern']
        db.create_unique('seo_link_excludepath', ['type_id', 'pattern'])

        # Adding model 'ReplacementTemplate'
        db.create_table('seo_link_replacementtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template_filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('seo_link', ['ReplacementTemplate'])

        # Adding model 'TargetPath'
        db.create_table('seo_link_targetpath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('is_external', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('seo_link', ['TargetPath'])

        # Adding model 'Term'
        db.create_table('seo_link_term', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('words', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('word_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('replacement_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo_link.ReplacementTemplate'])),
            ('target_path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo_link.TargetPath'], null=True, blank=True)),
            ('is_case_sensitive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('seo_link', ['Term'])

        # Adding unique constraint on 'Term', fields ['words', 'word_count']
        db.create_unique('seo_link_term', ['words', 'word_count'])

        # Adding M2M table for field ignore_pattern on 'Term'
        db.create_table('seo_link_term_ignore_pattern', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('term', models.ForeignKey(orm['seo_link.term'], null=False)),
            ('excludepath', models.ForeignKey(orm['seo_link.excludepath'], null=False))
        ))
        db.create_unique('seo_link_term_ignore_pattern', ['term_id', 'excludepath_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Term', fields ['words', 'word_count']
        db.delete_unique('seo_link_term', ['words', 'word_count'])

        # Removing unique constraint on 'ExcludePath', fields ['type', 'pattern']
        db.delete_unique('seo_link_excludepath', ['type_id', 'pattern'])

        # Deleting model 'MatchType'
        db.delete_table('seo_link_matchtype')

        # Deleting model 'ExcludePath'
        db.delete_table('seo_link_excludepath')

        # Deleting model 'ReplacementTemplate'
        db.delete_table('seo_link_replacementtemplate')

        # Deleting model 'TargetPath'
        db.delete_table('seo_link_targetpath')

        # Deleting model 'Term'
        db.delete_table('seo_link_term')

        # Removing M2M table for field ignore_pattern on 'Term'
        db.delete_table('seo_link_term_ignore_pattern')


    models = {
        'seo_link.excludepath': {
            'Meta': {'unique_together': "(('type', 'pattern'),)", 'object_name': 'ExcludePath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.MatchType']"})
        },
        'seo_link.matchtype': {
            'Meta': {'object_name': 'MatchType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'seo_link.replacementtemplate': {
            'Meta': {'object_name': 'ReplacementTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'seo_link.targetpath': {
            'Meta': {'object_name': 'TargetPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'seo_link.term': {
            'Meta': {'unique_together': "(('words', 'word_count'),)", 'object_name': 'Term'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore_pattern': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo_link.ExcludePath']", 'symmetrical': 'False', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_case_sensitive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'replacement_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.ReplacementTemplate']"}),
            'target_path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.TargetPath']", 'null': 'True', 'blank': 'True'}),
            'word_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'words': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['seo_link']
