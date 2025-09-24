from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import json

class Study(models.Model):
    id = models.AutoField(primary_key=True)
    study_id = models.CharField(max_length=100, unique=True)
    data_layout = models.JSONField()
    variable_details = models.JSONField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['study_id']),
        ]

    def __str__(self):
        return self.study_id


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    id = models.AutoField(primary_key=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True, blank=True)
    user_id = models.CharField(max_length=100, unique=True, help_text="Legacy user identifier")
    last_accessed = models.DateTimeField(blank=True, null=True)
    cases_assigned = models.JSONField(default=list, help_text="List of assigned case IDs")
    cases_completed = models.JSONField(default=list, help_text="List of completed case IDs")

    # Override username field to use user_id
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        default='',
    )

    class Meta:
        indexes = [
            models.Index(fields=['study', 'user_id']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f"{self.study.study_id if self.study else 'No Study'}:{self.user_id}"

    def get_full_name(self):
        """Return the user's full name or username."""
        return super().get_full_name() or self.user_id

    def get_short_name(self):
        """Return the user's short name or username."""
        return super().get_short_name() or self.user_id

class Case(models.Model):
    id = models.AutoField(primary_key=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    case_id = models.CharField(max_length=100)
    demographics = models.JSONField()
    observations = models.JSONField()
    note_panel_data = models.JSONField()
    case_details = models.JSONField()

    class Meta:
        unique_together = ('study', 'case_id')
        indexes = [
            models.Index(fields=['study', 'case_id']),
        ]

    def __str__(self):
        return f"{self.study.study_id}:{self.case_id}"

class Medication(models.Model):
    id = models.AutoField(primary_key=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    medidx = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    original_name = models.TextField()
    med_route = models.CharField(max_length=100)

    class Meta:
        unique_together = ('study', 'medidx')
        indexes = [
            models.Index(fields=['study', 'medidx']),
        ]

    def __str__(self):
        return f"{self.study.study_id}:{self.medidx}"

class CaseMedication(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    med_data = models.JSONField()
    y_axis_ranges = models.JSONField()

    def __str__(self):
        return f"{self.case}:{self.medication.medidx}"

class StoredResult(models.Model):
    id = models.AutoField(primary_key=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    case_id = models.CharField(max_length=100)
    selected_items = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=['study', 'user_id', 'case_id']),
        ]

    def __str__(self):
        return f"{self.study.study_id}:{self.user_id}:{self.case_id}"

class CaseSelection(models.Model):
    id = models.AutoField(primary_key=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    case_id = models.CharField(max_length=100)

    class Meta:
        unique_together = ('study', 'user_id', 'case_id')
        indexes = [
            models.Index(fields=['study', 'user_id', 'case_id']),
        ]

    def __str__(self):
        return f"{self.study.study_id}:{self.user_id}:{self.case_id}"