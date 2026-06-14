from decimal import Decimal

from rest_framework import serializers

from .models import Expense, ExpenseSplit, Settlement
from django.contrib.auth import get_user_model
from decimal import Decimal
User = get_user_model()


class ExpenseCreateSerializer(serializers.Serializer):

    group_id = serializers.IntegerField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = serializers.ChoiceField(
        choices=Expense.Currency.choices,
    )

    description = serializers.CharField(
        max_length=255,
    )

    split_type = serializers.ChoiceField(
        choices=Expense.SplitType.choices,
    )

    expense_date = serializers.DateField()

    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        required=False,
    )

    splits = serializers.ListField(
    child=serializers.DictField(),
    required=False,)

    def validate(self, attrs):
        split_type = attrs["split_type"]

        if split_type == Expense.SplitType.EQUAL:
            participant_ids = attrs.get(
                "participant_ids"
            )
            if not participant_ids:
                raise serializers.ValidationError(
                    "participant_ids are required for EQUAL splits."
                )

            return attrs

        if split_type == Expense.SplitType.EXACT:
            splits = attrs.get("splits")

            if not splits:
                raise serializers.ValidationError(
                    "Splits are required for EXACT expenses."
                )

            total = Decimal("0.00")

            for split in splits:
                if (
                    "user_id" not in split
                    or "amount_owed" not in split
                ):
                    raise serializers.ValidationError(
                        "Each split requires user_id and amount_owed."
                    )

                total += Decimal(
                    str(split["amount_owed"])
                )

            if total >= attrs["amount"]:
                raise serializers.ValidationError(
                    "Participant shares must total less than the expense amount."
                )

            return attrs

        if split_type == Expense.SplitType.PERCENTAGE:
            splits = attrs.get("splits")

            if not splits:
                raise serializers.ValidationError(
                    "Splits are required for PERCENTAGE expenses."
                )

            total_percentage = Decimal("0.00")

            for split in splits:
                if (
                    "user_id" not in split
                    or "percentage" not in split
                ):
                    raise serializers.ValidationError(
                        "Each split requires user_id and percentage."
                    )

                percentage = Decimal(
                    str(split["percentage"])
                )

                if percentage <= 0:
                    raise serializers.ValidationError(
                        "Percentages must be greater than 0."
                    )

                total_percentage += percentage

            if total_percentage >= Decimal("100"):
                raise serializers.ValidationError(
                    "Participant percentages must total less than 100."
                )

            return attrs
        
        raise serializers.ValidationError(
            "Unsupported split type."
        )
    
    def validate_participant_ids(self, value):
        if len(set(value)) != len(value):
            raise serializers.ValidationError(
                "Duplicate participants are not allowed."
            )

        return value

class ExpensePayerSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User

        fields = [
            "id",
            "username",
        ]


class ExpenseHistorySerializer(
    serializers.ModelSerializer
):
    paid_by = ExpensePayerSerializer(
        read_only=True
    )

    participant_count = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Expense

        fields = [
            "id",
            "description",
            "amount",
            "currency",
            "split_type",
            "expense_date",
            "paid_by",
            "participant_count",
        ]

    def get_participant_count(
        self,
        obj,
    ):
        return obj.splits.count()


class ExpenseParticipantSerializer(
    serializers.ModelSerializer
):
    id = serializers.IntegerField(
        source="user.id"
    )

    username = serializers.CharField(
        source="user.username"
    )

    class Meta:
        model = ExpenseSplit

        fields = [
            "id",
            "username",
            "amount_owed",
        ]


class ExpenseDetailSerializer(
    serializers.ModelSerializer
):
    paid_by = ExpensePayerSerializer()

    participants = (
        ExpenseParticipantSerializer(
            source="splits",
            many=True,
        )
    )

    current_user_balance = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Expense

        fields = [
            "id",
            "description",
            "amount",
            "currency",
            "split_type",
            "expense_date",
            "paid_by",
            "participants",
            "current_user_balance",
        ]

    def get_current_user_balance(self,obj):
        request = self.context[
            "request"
        ]

        user = request.user

        user_split = obj.splits.filter(
            user=user
        ).first()

        if not user_split:
            return "0.00"

        amount_owed = (
            user_split.amount_owed
        )

        if obj.paid_by == user:
            return str(
                obj.amount
                - amount_owed
            )

        return str(
            -amount_owed
        )

class GroupBalanceSerializer(
    serializers.Serializer
):
    user_id = serializers.IntegerField()

    username = serializers.CharField()

    net_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

class SettlementCreateSerializer(
    serializers.Serializer
):
    group_id = serializers.IntegerField()

    received_by = serializers.IntegerField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = serializers.ChoiceField(
        choices=Settlement.Currency.choices,
    )

    settlement_date = serializers.DateField()

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )

class SettlementHistorySerializer(
    serializers.ModelSerializer
):
    paid_by_username = serializers.CharField(
        source="paid_by.username",
        read_only=True,
    )

    received_by_username = serializers.CharField(
        source="received_by.username",
        read_only=True,
    )

    class Meta:
        model = Settlement

        fields = [
            "id",
            "paid_by",
            "paid_by_username",
            "received_by",
            "received_by_username",
            "amount",
            "currency",
            "settlement_date",
            "notes",
        ]

class DirectExpenseSerializer(
    serializers.Serializer
):
    user_id = serializers.IntegerField()














