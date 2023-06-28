from django.db import models
import uuid



# Create your models here.
class Teacher(models.Model):

    POSTS = [
        ('P', 'PGT'), 
        ('T', 'TGT'),
        ('C', 'COACH')
    ]

    uid = models.UUIDField(default=uuid.uuid4) 
    name = models.CharField(max_length=32)
    post = models.CharField(max_length=1, choices=POSTS, default='T')   
    
    def __str__(self):
        return self.name
    
    def get_post(self):
        if self.post == 'P': return 'PGT'
        elif self.post == 'T': return 'TGT'
        return 'COACH'

    
class Table(models.Model):
    teacher = models.ForeignKey(to=Teacher, on_delete=models.CASCADE)
    day = models.SmallIntegerField()

    p1 = models.CharField(max_length=3, default='F')
    p2 = models.CharField(max_length=3, default='F')
    p3 = models.CharField(max_length=3, default='F')
    p4 = models.CharField(max_length=3, default='F')
    p5 = models.CharField(max_length=3, default='F')
    p6 = models.CharField(max_length=3, default='F')
    p7 = models.CharField(max_length=3, default='F')
    p8 = models.CharField(max_length=3, default='F')

    def get_classes(self):
        return [
            self.p1, self.p2, self.p3, self.p4, 
            self.p5, self.p6, self.p7, self.p8
        ]
    
class Absent(models.Model):
    date = models.DateField()
    teacher = models.ForeignKey(to=Teacher, on_delete=models.CASCADE)
    exempt = models.BooleanField(default=False)
