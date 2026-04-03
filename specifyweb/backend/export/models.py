from django.db import models
from django.utils import timezone


class SchemaMapping(models.Model):
    # ID Field
    id = models.AutoField(primary_key=True, db_column='SchemaMappingID')

    # Fields
    mappingtype = models.CharField(
        max_length=16, db_column='MappingType',
        choices=[('Core', 'Core'), ('Extension', 'Extension')],
    )
    name = models.CharField(max_length=256, db_column='Name')
    isdefault = models.BooleanField(default=False, db_column='IsDefault')
    timestampcreated = models.DateTimeField(db_column='TimestampCreated', default=timezone.now)
    timestampmodified = models.DateTimeField(db_column='TimestampModified', default=timezone.now)
    version = models.IntegerField(default=0, db_column='Version')

    # Relationships
    query = models.OneToOneField(
        'specify.Spquery', db_column='SpQueryID',
        on_delete=models.CASCADE, related_name='schemamapping',
    )
    createdbyagent = models.ForeignKey(
        'specify.Agent', db_column='CreatedByAgentID',
        related_name='+', null=True, on_delete=models.SET_NULL,
    )
    modifiedbyagent = models.ForeignKey(
        'specify.Agent', db_column='ModifiedByAgentID',
        related_name='+', null=True, on_delete=models.SET_NULL,
    )

    class Meta:
        db_table = 'schemamapping'
