"""
metaimage/models.py
"""

from django.db import models
from person.models import Users


# Таблица generations
class Generations(models.Model):
    prompt = models.TextField()
    response = models.TextField()
    cost = models.IntegerField()

    def __str__(self):
        return "%s" % self.prompt

    class Meta:
        db_table = "Generations"
        verbose_name = "Generations"
        verbose_name_plural = "Generations"


class UsersGenerations(models.Model):
    user_id = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="user_generations"
    )
    generations_id = models.ForeignKey(
        Generations, on_delete=models.CASCADE, related_name="user_generations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "User ID: %s, Time of created: %s" % (self.user_id, self.created_at)

    class Meta:
        db_table = "UsersGenerations"
        verbose_name = "Users Generations"
        verbose_name_plural = "Users Generations"
        # unique_together = (('user_id', 'generations_id'),)


class Transactions(models.Model):
    amount = models.PositiveIntegerField()
    type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s" % self.amount

    class Meta:
        db_table = "Transactions"
        verbose_name = "Transactions"
        verbose_name_plural = "Transactions"


class UsersTransactions(models.Model):
    user_id = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="user_transactions"
    )
    transactions_id = models.ForeignKey(
        Transactions, on_delete=models.CASCADE, related_name="user_transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
