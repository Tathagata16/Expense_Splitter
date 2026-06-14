from django.urls import path

from .views import DirectGroupView, ExpenseCreateView, ExpenseDetailView, GroupBalanceView, GroupExpenseHistoryView, SettlementCreateView, SettlementHistoryView

urlpatterns = [
    path("",ExpenseCreateView.as_view(),name="expense-create"),

    path(
    "groups/<int:group_id>/",
    GroupExpenseHistoryView.as_view(),
    name="group-expenses"),

    path(
    "<int:expense_id>/",
    ExpenseDetailView.as_view(),
    name="expense-detail"),

    path(
    "groups/<int:group_id>/balances/",
    GroupBalanceView.as_view(),
    name="group-balances"),

    path(
    "settlements/",
    SettlementCreateView.as_view(),
    name="create-settlement"),


    path(
    "groups/<int:group_id>/settlements/",
    SettlementHistoryView.as_view(),
    name="settlement-history"),

    path(
    "direct/",
    DirectGroupView.as_view(),
    name="direct-group"),
]