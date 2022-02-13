from django.db import models


class ActionLog(models.Model):    
	created = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=200)
	msg  = models.CharField(max_length=200)
