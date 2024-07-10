"""
SEMRinterface/models.py
package github.com/ajk77/SimpleEMRSystem

This file is to assist with connecting to the databases specified in SEMRproject/setting.py. 

To connect to MIMIC, or any other database, replace the definitions below with definitions of the database you are connecting to. 

"""

# models for crisma server's learningemr
# notes are stored locally

from django.db import models


class a_ClinicalEvents(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.DateTimeField(null=True, db_column='EventDate', blank=True)
    rollname= models.CharField(max_length=30, db_column='RollupName',blank=True)
    rollval = models.FloatField(null=True, db_column='RollupVal', blank=True)
    rollunit = models.CharField(max_length=15, db_column='RollupUnit', blank=True)
    rollvaltext = models.CharField(max_length=50, db_column='RollupValText', blank=True)
    class Meta:
        db_table = u'a_ClinicalEvents'


class a_demographics(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    age = models.IntegerField(null=True, db_column='Age', blank=True)
    height = models.FloatField(null=True, db_column='Height', blank=True)
    weight = models.FloatField(null=True, db_column='Weight', blank=True)
    bmi = models.FloatField(null=True, db_column='BMI', blank=True)
    sex = models.CharField(max_length=1, db_column='Sex', blank=True)
    race = models.CharField(max_length=35, db_column='RaceComposite', blank=True)
    class Meta:
        db_table = u'a_demographics'


class a_HomeMeds(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.DateTimeField(null=True, db_column='ActionDate', blank=True)
    ordertype = models.CharField(max_length=20, db_column='OrderType', blank=True)
    genericname = models.CharField(max_length=50, db_column='GenericName', blank=True)
    frequency = models.CharField(max_length=35, db_column='Frequency', blank=True)
    route = models.CharField(max_length=35, db_column='Route', blank=True)
    dose = models.FloatField(db_column='Dose', blank=True)
    unit = models.CharField(max_length=15, db_column='DoseUnit', blank=True)
    ordername = models.CharField(max_length=80, db_column='OrderName', blank=True)
    class Meta:
        db_table = u'a_HomeMeds'


class a_ICDCPT(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.DateTimeField(null=True, db_column='EventDate', blank=True)
    IcdCpt = models.FloatField(db_column='IcdCpt', blank=True)
    text = models.CharField(max_length=125, db_column='Disp', blank=True)
    class Meta:
        db_table = u'a_ICDCPT'


class a_ICUpatients(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    admit = models.DateTimeField(null=True, db_column='AdmitDate', blank=True)
    discharge = models.DateTimeField(null=True, db_column='DischDate', blank=True)
    ICUadmit = models.DateTimeField(null=True, db_column='ICUadmit', blank=True)
    ICUdischarge = models.DateTimeField(null=True, db_column='ICUDisch', blank=True)
    unit = models.CharField(max_length=20, db_column='Unit', blank=True)
    class Meta:
        db_table = u'a_ICUpatients'


class a_IO(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    type = models.CharField(max_length=10, db_column='IOType', blank=True)
    name = models.CharField(max_length=40, db_column='IOName', blank=True)
    date = models.DateTimeField(null=True, db_column='IODate', blank=True)
    volume = models.FloatField(db_column='Volume', blank=True)
    unit = models.CharField(max_length=20, db_column='Unit', blank=True)
    category = models.IntegerField(db_column='Category', blank=True)
    class Meta:
        db_table = u'a_IO'


class a_Medication(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.DateTimeField(null=True, db_column='ChartDate', blank=True)
    name = models.CharField(max_length=45, db_column='CatalogDisp', blank=True)
    route = models.CharField(max_length=25, db_column='Route', blank=True)
    dose = models.FloatField(db_column='Dose', blank=True)
    unit = models.CharField(max_length=20, db_column='DoseUnit', blank=True)
    voldose = models.FloatField(db_column='VolumeDose', blank=True)
    voldoseunit = models.CharField(max_length=20, db_column='VolumeDoseUnit', blank=True)
    orderid = models.CharField(max_length=20, db_column='OrderID', blank=True)
    orderedas = models.CharField(max_length=110, db_column='OrderedAs', blank=True)
    event = models.CharField(max_length=45, db_column='EventTag', blank=True)
    resultval = models.FloatField(db_column='ResultVal', blank=True)
    class Meta:
        db_table = u'a_Medication'


class a_Micro(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.DateTimeField(null=True, db_column='EventDate', blank=True)
    eventid = models.IntegerField(null=False, db_column='EventID')
    eventname = models.CharField(max_length=45, db_column='EventName', blank=True)
    accession = models.CharField(max_length=20, db_column='Accession', blank=True)
    source = models.CharField(max_length=35, db_column='Source', blank=True)
    class Meta:
        unique_together = (("patientvisitid", "date"),)
        db_table = u'a_Micro'
        ordering = ['-date']  # so query is ordered by date, not upk


class a_MicroReport(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    eventid = models.IntegerField(null=False, db_column='EventID')
    accession = models.CharField(max_length=20, db_column='Accession', blank=True)
    text = models.TextField(db_column='MicroReport', blank=True)
    class Meta:
        unique_together = (("patientvisitid", "eventid"),)
        db_table = u'a_MicroReport'


class a_Surgical(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.IntegerField(null=False, db_column='BegDate')
    primary = models.CharField(max_length=1, db_column='PrimaryProcedure', blank=True)
    procedure = models.CharField(max_length=50, db_column='SurgProcedure', blank=True)
    predx = models.CharField(max_length=60, db_column='PreDx', blank=True)
    postdx = models.CharField(max_length=60, db_column='PostDx', blank=True)
    class Meta:
        unique_together = (("patientvisitid", "date"),)
        db_table = u'a_Surgical'


class a_Ventilator(models.Model):
    patientvisitid = models.IntegerField(primary_key=True, db_column='PatientVisitID')
    date = models.IntegerField(null=False, db_column='EventDate')
    eventname = models.CharField(max_length=20, db_column='EventName', blank=True)
    resultval = models.CharField(max_length=30, db_column='ResultVal', blank=True)
    class Meta:
        unique_together = (("patientvisitid", "date"),)
        db_table = u'a_Ventilator'


class a_groupmember(models.Model):
    object = models.CharField(max_length=600, blank=True)
    name = models.CharField(max_length=45, db_column='rollupName')
    groupname = models.CharField(max_length=600, db_column='groupName') # Field name made lowercase.
    labname = models.CharField(max_length=600, db_column='labName', blank=True) # Field name made lowercase.
    group_rank = models.IntegerField(null=True, blank=True)
    upk = models.IntegerField(primary_key=True)
    upperbound = models.FloatField(null=True, db_column='upperBounds', blank=True)
    lowerbound = models.FloatField(null=True, db_column='lowerBounds', blank=True)
    uppernormal = models.FloatField(null=True, db_column='upperNormalRange', blank=True)
    lowernormal = models.FloatField(null=True, db_column='lowerNormalRange', blank=True)
    femaleuppernormal = models.FloatField(null=True, db_column='femaleUpperNormalRange', blank=True)
    femalelowernormal = models.FloatField(null=True, db_column='femaleLowerNormalRange', blank=True)
    order_in_group = models.IntegerField(null=True, db_column='orderInGroup', blank=True)
    isdiscrete = models.IntegerField(null=True, db_column='isDiscrete', blank=True)
    units = models.CharField(max_length=15, db_column='units')
    class Meta:
        db_table = u'a_groupmember'


class lab_739(models.Model):
    patientvisitid = models.IntegerField(db_column='PatientVisitID')
    eventdate = models.DateTimeField(db_column='EventDate')
    eventcode = models.CharField(max_length=6, db_column='EventCode')
    eventvalue = models.FloatField(null=True, db_column='EventValue', blank=True)
    eventunit = models.CharField(max_length=30, db_column='EventUnit', blank=True)
    eventtext = models.CharField(max_length=50, db_column='EventText', blank=True)
    rangelow = models.FloatField(null=True, db_column='RangeLow', blank=True)
    rangehigh = models.FloatField(null=True, db_column='RangeHigh', blank=True)
    rangeother = models.CharField(max_length=12, db_column='RangeOther', blank=True)
    flag = models.CharField(max_length=4, db_column='Flag', blank=True)
    upk = models.IntegerField(primary_key=True, db_column='upk')
    class Meta:
        db_table = u'lab_739'


class marstorootcodes(models.Model):
    marscode = models.CharField(primary_key=True,max_length=6, db_column='marsCode')
    rootcode = models.CharField(max_length=6, db_column='rootCode')
    class Meta:
        db_table = u'marstorootcodes'


class rootgroupmember(models.Model):
    root = models.CharField(primary_key=True,max_length=6, db_column='root')
    cerner = models.CharField(max_length=40, db_column='cerner')
    labname = models.CharField(max_length=30, db_column='labname')
    groupname = models.CharField(max_length=20, db_column='groupname')
    grouprank = models.IntegerField(db_column='grouprank')
    orderingroup = models.IntegerField(db_column='orderingroup')
    datatable = models.CharField(max_length=16, db_column='datatable')
    datatype = models.CharField(max_length=1, db_column='datatype')
    class Meta:
        db_table = u'rootgroupmember'
        ordering = ['orderingroup']  # so query is ordered by date, not upk


class displayparams(models.Model):
    root = models.CharField(primary_key=True,max_length=6, db_column='root')
    displaytype = models.CharField(max_length=8, db_column='displayType')
    mindd = models.FloatField(null=True, db_column='minDisplayDefault', blank=True)
    minrd = models.FloatField(null=True, db_column='minRangeDefault', blank=True)
    maxrd = models.FloatField(null=True, db_column='maxRangeDefault', blank=True)
    maxdd = models.FloatField(null=True, db_column='maxDisplayDefault', blank=True)
    unitsdefault = models.CharField(max_length=8, db_column='unitsDefault')
    class Meta:
        db_table = u'displayparams'

