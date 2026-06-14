from collections import defaultdict
from decimal import Decimal
from urllib import request

from django.db import transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from groups.models import Group, GroupMember

from .models import Expense, ExpenseSplit, Settlement
from .serializers import (
    ExpenseCreateSerializer,
    ExpenseHistorySerializer,
    ExpenseDetailSerializer,
    GroupBalanceSerializer,
    SettlementCreateSerializer,
    SettlementHistorySerializer,
    DirectExpenseSerializer,
)

from django.contrib.auth import get_user_model

from groups.services import (
    get_or_create_direct_group,
)

User = get_user_model()


class ExpenseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = ExpenseCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        group = (
            Group.objects.filter(
                id=data["group_id"],
                memberships__user=request.user,
                memberships__left_at__isnull=True,
            )
            .distinct()
            .first()
        )

        if not group:
            return Response(
                {"error": "You are not a member of this group."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if data["split_type"] == Expense.SplitType.EQUAL:
            participant_ids = set(data["participant_ids"])

            participant_ids.add(request.user.id)

            if len(participant_ids) < 2:
                return Response(
                    {
                        "error": (
                            "An expense must involve "
                            "at least two distinct participants."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            active_members = set(
                GroupMember.objects.filter(
                    group=group,
                    left_at__isnull=True,
                    user_id__in=participant_ids,
                ).values_list(
                    "user_id",
                    flat=True,
                )
            )

            if active_members != participant_ids:
                return Response(
                    {"error": "All participants must be active group members."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            expense = Expense.objects.create(
                group=group,
                paid_by=request.user,
                amount=data["amount"],
                currency=data["currency"],
                description=data["description"],
                split_type=data["split_type"],
                expense_date=data["expense_date"],
            )

            share = data["amount"] / Decimal(len(participant_ids))

            for user_id in participant_ids:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=user_id,
                    amount_owed=share,
                )

        elif data["split_type"] == Expense.SplitType.EXACT:
            splits = data["splits"]

            participant_ids = {
                split["user_id"]
                for split in splits
            }

            participant_ids.add(request.user.id)

            if len(participant_ids) < 2:
                return Response(
                    {
                        "error": (
                            "An expense must involve "
                            "at least two participants."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            active_members = set(
                GroupMember.objects.filter(
                    group=group,
                    left_at__isnull=True,
                    user_id__in=participant_ids,
                ).values_list(
                    "user_id",
                    flat=True,
                )
            )

            if active_members != participant_ids:
                return Response(
                    {
                        "error": (
                            "All participants must "
                            "be active group members."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            expense = Expense.objects.create(
                group=group,
                paid_by=request.user,
                amount=data["amount"],
                currency=data["currency"],
                description=data["description"],
                split_type=data["split_type"],
                expense_date=data["expense_date"],
            )

            total_assigned = sum(
                Decimal(str(split["amount_owed"]))
                for split in splits
            )

            payer_share = (
                data["amount"]
                - total_assigned
            )

            for split in splits:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=split["user_id"],
                    amount_owed=split["amount_owed"],
                )

            ExpenseSplit.objects.create(
                expense=expense,
                user=request.user,
                amount_owed=payer_share,
            )

        elif data["split_type"] == Expense.SplitType.PERCENTAGE:
            splits = data["splits"]

            participant_ids = {
                split["user_id"]
                for split in splits
            }

            participant_ids.add(request.user.id)

            if len(participant_ids) < 2:
                return Response(
                    {
                        "error": (
                            "An expense must involve "
                            "at least two participants."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            active_members = set(
                GroupMember.objects.filter(
                    group=group,
                    left_at__isnull=True,
                    user_id__in=participant_ids,
                ).values_list(
                    "user_id",
                    flat=True,
                )
            )

            if active_members != participant_ids:
                return Response(
                    {
                        "error": (
                            "All participants must "
                            "be active group members."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            expense = Expense.objects.create(
                group=group,
                paid_by=request.user,
                amount=data["amount"],
                currency=data["currency"],
                description=data["description"],
                split_type=data["split_type"],
                expense_date=data["expense_date"],
            )

            total_percentage = sum(
                Decimal(str(split["percentage"]))
                for split in splits
            )

            payer_percentage = (
                Decimal("100")
                - total_percentage
            )

            payer_share = (
                data["amount"]
                * payer_percentage
                / Decimal("100")
            )

            for split in splits:
                percentage = Decimal(
                    str(split["percentage"])
                )

                amount_owed = (
                    data["amount"]
                    * percentage
                    / Decimal("100")
                )

                ExpenseSplit.objects.create(
                    expense=expense,
                    user_id=split["user_id"],
                    amount_owed=amount_owed,
                )

            ExpenseSplit.objects.create(
                expense=expense,
                user=request.user,
                amount_owed=payer_share,
            )

        return Response(
            {
                "message": "Expense added successfully.",
                "expense_id": expense.id,
            },
            status=status.HTTP_201_CREATED,
        )


class GroupExpenseHistoryView(generics.ListAPIView):
    serializer_class = ExpenseHistorySerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs["group_id"]

        return (
            Expense.objects.filter(
                group_id=group_id,
                group__memberships__user=self.request.user,
                group__memberships__left_at__isnull=True,
            )
            .select_related("paid_by")
            .prefetch_related("splits")
            .distinct()
            .order_by(
                "-expense_date",
                "-created_at",
            )
        )


class ExpenseDetailView(generics.RetrieveAPIView):
    serializer_class = ExpenseDetailSerializer

    permission_classes = [IsAuthenticated]

    lookup_url_kwarg = "expense_id"

    def get_queryset(self):
        return (
            Expense.objects.filter(
                group__memberships__user=self.request.user,
                group__memberships__left_at__isnull=True,
            )
            .select_related("paid_by")
            .prefetch_related("splits__user")
            .distinct()
        )


class GroupBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):

        group = (
            Group.objects.filter(
                id=group_id,
                memberships__user=request.user,
                memberships__left_at__isnull=True,
            )
            .distinct()
            .first()
        )

        if not group:
            return Response(
                {"error": "You are not a member of this group."},
                status=status.HTTP_403_FORBIDDEN,
            )

        balances = defaultdict(
            lambda: {
                "user_id": None,
                "username": "",
                "net_balance": Decimal("0.00"),
            }
        )

        expenses = (
            Expense.objects.filter(group=group)
            .select_related("paid_by")
            .prefetch_related("splits__user")
        )

        for expense in expenses:

            payer = expense.paid_by

            balances[payer.id]["user_id"] = payer.id

            balances[payer.id]["username"] = payer.username

            balances[payer.id]["net_balance"] += expense.amount

            for split in expense.splits.all():

                user = split.user

                balances[user.id]["user_id"] = user.id

                balances[user.id]["username"] = user.username

                balances[user.id]["net_balance"] -= split.amount_owed

        settlements = Settlement.objects.filter(group=group).select_related(
            "paid_by",
            "received_by",
        )

        for settlement in settlements:

            balances[settlement.paid_by_id]["user_id"] = settlement.paid_by_id

            balances[settlement.paid_by_id]["username"] = settlement.paid_by.username

            balances[settlement.paid_by_id]["net_balance"] += settlement.amount

            balances[settlement.received_by_id]["user_id"] = settlement.received_by_id

            balances[settlement.received_by_id][
                "username"
            ] = settlement.received_by.username

            balances[settlement.received_by_id]["net_balance"] -= settlement.amount

        serializer = GroupBalanceSerializer(
            balances.values(),
            many=True,
        )

        return Response(serializer.data)


class SettlementCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        serializer = SettlementCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        group = (
            Group.objects.filter(
                id=data["group_id"],
                memberships__user=request.user,
                memberships__left_at__isnull=True,
            )
            .distinct()
            .first()
        )

        if not group:
            return Response(
                {"error": "You are not a member of this group."},
                status=status.HTTP_403_FORBIDDEN,
            )

        receiver_id = data["received_by"]

        if receiver_id == request.user.id:
            return Response(
                {"error": "Cannot settle with yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        receiver_exists = GroupMember.objects.filter(
            group=group,
            user_id=receiver_id,
            left_at__isnull=True,
        ).exists()

        if not receiver_exists:
            return Response(
                {"error": "Receiver is not an active group member."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        balances = defaultdict(Decimal)

        expenses = (
            Expense.objects.filter(group=group)
            .select_related("paid_by")
            .prefetch_related("splits")
        )

        for expense in expenses:

            balances[expense.paid_by_id] += expense.amount

            for split in expense.splits.all():

                balances[split.user_id] -= split.amount_owed

        settlements = Settlement.objects.filter(group=group)

        for settlement in settlements:

            balances[settlement.paid_by_id] += settlement.amount

            balances[settlement.received_by_id] -= settlement.amount

        receiver_balance = balances[receiver_id]

        payer_balance = balances[request.user.id]

        if payer_balance >= Decimal("0"):
            return Response(
                {"error": "You do not owe money."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if receiver_balance <= Decimal("0"):
            return Response(
                {"error": "Receiver is not owed money."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_settlement = min(
            abs(payer_balance),
            receiver_balance,
        )

        if data["amount"] > max_settlement:
            return Response(
                {"error": "Settlement amount exceeds outstanding balance."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        settlement = Settlement.objects.create(
            group=group,
            paid_by=request.user,
            received_by_id=receiver_id,
            amount=data["amount"],
            currency=data["currency"],
            settlement_date=data["settlement_date"],
            notes=data.get(
                "notes",
                "",
            ),
        )

        return Response(
            {
                "message": "Settlement recorded successfully.",
                "settlement_id": settlement.id,
            },
            status=status.HTTP_201_CREATED,
        )


class SettlementHistoryView(generics.ListAPIView):
    serializer_class = SettlementHistorySerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs["group_id"]

        is_member = Group.objects.filter(
            id=group_id,
            memberships__user=self.request.user,
            memberships__left_at__isnull=True,
        ).exists()

        if not is_member:
            return Settlement.objects.none()

        return (
            Settlement.objects.filter(group_id=group_id)
            .select_related(
                "paid_by",
                "received_by",
            )
            .order_by(
                "-settlement_date",
                "-created_at",
            )
        )


class DirectGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = DirectExpenseSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        other_user_id = serializer.validated_data["user_id"]

        if other_user_id == request.user.id:
            return Response(
                {"error": "Cannot create a direct group with yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            other_user = User.objects.get(id=other_user_id)

        except User.DoesNotExist:

            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        existing_group = (
            Group.objects.filter(
                group_type="DIRECT",
                memberships__user=request.user,
                memberships__left_at__isnull=True,
            )
            .filter(
                memberships__user=other_user,
                memberships__left_at__isnull=True,
            )
            .distinct()
            .first()
        )

        created = existing_group is None

        group = get_or_create_direct_group(
            request.user,
            other_user,
        )

        return Response(
            {
                "group_id": group.id,
                "created": created,
            }
        )
