from django.db import models
import uuid, math



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

    sections = models.CharField(max_length=5, default='ABCDE')
    
    def __str__(self):
        return self.name
    
    def get_post(self):
        if self.post == 'P': return 'PGT'
        elif self.post == 'T': return 'TGT'
        return 'COACH'
    
    def get_limit(self):
        if self.post == 'C': return 4
        if self.post == 'N': return math.inf
        return 2

    
class Table(models.Model):
    teacher = models.ForeignKey(to=Teacher, on_delete=models.CASCADE)
    day = models.SmallIntegerField()

    p1 = models.CharField(max_length=12, default='F')
    p2 = models.CharField(max_length=12, default='F')
    p3 = models.CharField(max_length=12, default='F')
    p4 = models.CharField(max_length=12, default='F')
    p5 = models.CharField(max_length=12, default='F')
    p6 = models.CharField(max_length=12, default='F')
    p7 = models.CharField(max_length=12, default='F')
    p8 = models.CharField(max_length=12, default='F')

    def get_classes(self):
        return [
            self.p1, self.p2, self.p3, self.p4, 
            self.p5, self.p6, self.p7, self.p8
        ]
    
    def trim(self):
        if self.teacher.post != 'C':
            self.p1 = ''.join(self.p1.split())
            self.p2 = ''.join(self.p2.split())
            self.p3 = ''.join(self.p3.split())
            self.p4 = ''.join(self.p4.split())
            self.p5 = ''.join(self.p5.split())
            self.p6 = ''.join(self.p6.split())
            self.p7 = ''.join(self.p7.split())
            self.p8 = ''.join(self.p8.split())
        super().save()
    

    
class Absent(models.Model):
    date = models.DateField()
    teacher = models.ForeignKey(to=Teacher, on_delete=models.CASCADE)
    exempt = models.BooleanField(default=False)
    s1 = models.BooleanField(default=True)
    s2 = models.BooleanField(default=True)