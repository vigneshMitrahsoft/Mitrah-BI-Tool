from datetime import datetime
from django.db import models

class sources(models.Model):
	source_id = models.BigAutoField(primary_key=True)
	db_credential = models.TextField()
	selected_tables = models.TextField()
	user_id = models.IntegerField(null=True)
	ct_dt = models.DateTimeField(default = datetime.now)
	ct_id = models.IntegerField(default=1)
	ut_dt = models.DateTimeField(null=True)
	ut_id = models.IntegerField(null=True)

	class Meta:
		db_table = 'sources'

class reports(models.Model):
	report_id = models.BigAutoField(primary_key=True)
	report_name = models.CharField(max_length=100)
	source_id = models.IntegerField()
	chart_details = models.TextField()

	class Meta:
		db_table = 'reports'
