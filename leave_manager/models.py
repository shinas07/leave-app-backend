from django.db import models
from accounts.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField(default=0) 
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_duration(self):
            if not self.start_date or not self.end_date:
                return 0
                
            working_days = 0
            current_date = self.start_date
            
            while current_date <= self.end_date:
                if current_date.weekday() != 6:  # Skip Sundays
                    working_days += 1
                current_date += timedelta(days=1)
                
            return working_days

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError('End date must be after start date.')

    def save(self, *args, **kwargs):
        self.duration = self.calculate_duration()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.get_leave_type_display()} ({self.status})"
    

class YearlyLeaveBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    total_leaves = models.IntegerField(default=40)
    leaves_taken = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'year')

    @property
    def remaining_leaves(self):
        return self.total_leaves - self.leaves_taken