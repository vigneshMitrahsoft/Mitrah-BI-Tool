from datetime import datetime
from django.db import models

class sources(models.Model):
    source_id = models.BigAutoField(primary_key=True)
    db_credential = models.CharField(max_length=200)
    selected_tables = models.CharField(max_length=100)
    user_id = models.IntegerField(null=True)
    ct_dt = models.DateTimeField(default = datetime.now)
    ct_id = models.IntegerField(default=1)
    ut_dt = models.DateTimeField(null=True)
    ut_id = models.IntegerField(null=True)

    class Meta:
        db_table = 'sources'
