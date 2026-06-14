from django.conf import settings
from django.db import models

from groups.models import Group


class Expense(models.Model):


    class Currency(models.TextChoices):
        INR = "INR", "Indian Rupee"
        USD = "USD", "US Dollar"

    class SplitType(models.TextChoices):
        EQUAL = "EQUAL", "Equal"
        EXACT = "EXACT", "Exact"
        PERCENTAGE = "PERCENTAGE", "Percentage"
        SHARE = "SHARE", "Share"

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expenses_paid",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.INR,
    )

    description = models.CharField(
        max_length=255,
    )

    split_type = models.CharField(
        max_length=20,
        choices=SplitType.choices,
    )

    expense_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.description} - {self.amount}"
    

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="splits",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_splits",
    )

    amount_owed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    shares = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["expense", "user"],
                name="unique_expense_user_split",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} owes "
            f"{self.amount_owed}"
        )
    

class Settlement(models.Model):
    class Currency(models.TextChoices):
        INR = "INR", "Indian Rupee"
        USD = "USD", "US Dollar"

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="settlements",
    )

    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="settlements_paid",
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="settlements_received",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.INR,
    )

    settlement_date = models.DateField()

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.paid_by.username} → "
            f"{self.received_by.username}"
        )























