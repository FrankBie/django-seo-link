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

        # Adding model 'OperatingPath'
        db.create_table('seo_link_operatingpath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo_link.MatchType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pattern', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_include', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('seo_link', ['OperatingPath'])

        # Adding unique constraint on 'OperatingPath', fields ['type', 'pattern']
        db.create_unique('seo_link_operatingpath', ['type_id', 'pattern'])

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

        # Adding M2M table for field operating_path on 'Term'
        db.create_table('seo_link_term_operating_path', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('term', models.ForeignKey(orm['seo_link.term'], null=False)),
            ('operatingpath', models.ForeignKey(orm['seo_link.operatingpath'], null=False))
        ))
        db.create_unique('seo_link_term_operating_path', ['term_id', 'operatingpath_id'])

        # Adding model 'TestUrl'
        db.create_table('seo_link_testurl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('tested_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('seo_link', ['TestUrl'])

        # Adding model 'TestResult'
        db.create_table('seo_link_testresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page_url', self.gf('django.db.models.fields.related.ForeignKey')(related_name='test_urls', to=orm['seo_link.TestUrl'])),
            ('page_title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('link_url', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('link_text', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('is_injected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('seo_link', ['TestResult'])

        # Adding model 'CacheKey'
        db.create_table('seo_link_cachekey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('site', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('seo_link', ['CacheKey'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Term', fields ['words', 'word_count']
        db.delete_unique('seo_link_term', ['words', 'word_count'])

        # Removing unique constraint on 'OperatingPath', fields ['type', 'pattern']
        db.delete_unique('seo_link_operatingpath', ['type_id', 'pattern'])

        # Deleting model 'MatchType'
        db.delete_table('seo_link_matchtype')

        # Deleting model 'OperatingPath'
        db.delete_table('seo_link_operatingpath')

        # Deleting model 'ReplacementTemplate'
        db.delete_table('seo_link_replacementtemplate')

        # Deleting model 'TargetPath'
        db.delete_table('seo_link_targetpath')

        # Deleting model 'Term'
        db.delete_table('seo_link_term')

        # Removing M2M table for field operating_path on 'Term'
        db.delete_table('seo_link_term_operating_path')

        # Deleting model 'TestUrl'
        db.delete_table('seo_link_testurl')

        # Deleting model 'TestResult'
        db.delete_table('seo_link_testresult')

        # Deleting model 'CacheKey'
        db.delete_table('seo_link_cachekey')


    models = {
        'seo_link.cachekey': {
            'Meta': {'object_name': 'CacheKey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'seo_link.matchtype': {
            'Meta': {'object_name': 'MatchType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'seo_link.operatingpath': {
            'Meta': {'unique_together': "(('type', 'pattern'),)", 'object_name': 'OperatingPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.MatchType']"})
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_case_sensitive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'operating_path': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo_link.OperatingPath']", 'symmetrical': 'False', 'blank': 'True'}),
            'replacement_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.ReplacementTemplate']"}),
            'target_path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo_link.TargetPath']", 'null': 'True', 'blank': 'True'}),
            'word_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'words': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'seo_link.testresult': {
            'Meta': {'object_name': 'TestResult'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_injected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link_text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'link_url': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'page_title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'page_url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'test_urls'", 'to': "orm['seo_link.TestUrl']"})
        },
        'seo_link.testurl': {
            'Meta': {'object_name': 'TestUrl'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test_url': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'tested_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['seo_link']
