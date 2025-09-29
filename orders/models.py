from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.


User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [("PENDING","Pending"),("PAID","Paid"),("CANCELLED","Cancelled")]
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="PAID")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    ticket_type = models.ForeignKey("events.TicketType", on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def line_total(self):
        return self.qty * self.unit_price
