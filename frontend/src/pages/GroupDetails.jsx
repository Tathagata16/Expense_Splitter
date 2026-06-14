import React from 'react'
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext"
import { API_BASE_URL } from '../config/api';


function GroupDetails() {

    const { id } = useParams();

    const navigate = useNavigate();

    const [group, setGroup] = useState(null);

    const [loading, setLoading] = useState(true);

    const [searchTerm, setSearchTerm] = useState("");

    const [searchResults, setSearchResults] = useState([]);

    const [activeTab, setActiveTab] = useState("expenses");

    //store the expenses..
    const [expenses, setExpenses] = useState([]);

    //show/notshow modal to add expense
    const [showExpenseForm, setShowExpenseForm] =
        useState(false);

    //expense form data store
    const [expenseForm, setExpenseForm] =
        useState({
            amount: "",
            description: "",
            currency: "INR",
            expense_date: "",

            split_type: "EQUAL",

            participant_ids: [],

            splits: {},
        });


    const [selectedExpense, setSelectedExpense] =
        useState(null);

    const [expenseDetail, setExpenseDetail] =
        useState(null);

    //STORE balances...
    const [balances, setBalances] =
        useState([]);

    //storing settlements..
    const [settlements, setSettlements] =
        useState([]);

    //settlement form modal states
    const [showSettlementForm, setShowSettlementForm] =
        useState(false);

    const [settlementForm, setSettlementForm] =
        useState({
            received_by: "",
            amount: "",
            currency: "INR",
            settlement_date: "",
            notes: "",
        });

    //gettting the user
    const { user, load } = useAuth();





    //fetching the group details...
    async function fetchGroupDetails() {
        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/groups/${id}/`,
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            if (response.ok) {
                const data = await response.json();

                setGroup(data);
            } else if (
                response.status === 401
            ) {
                navigate("/login");
            } else {
                alert(
                    "Unable to access this group"
                );

                navigate("/");
            }
        } catch (error) {
            console.error(error);

            alert("Something went wrong");

            navigate("/");
        } finally {
            setLoading(false);
        }
    }

    //handling search function
    async function handleSearchUsers() {
        if (!searchTerm.trim()) {
            setSearchResults([]);

            return;
        }

        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/groups/users/search/?q=${searchTerm}`,
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            if (response.ok) {
                const data =
                    await response.json();

                setSearchResults(data);
            }
        } catch (error) {
            console.error(error);
        }
    }

    //handling invite function
    async function handleInviteUser(
        userId
    ) {
        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/groups/${id}/invite/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        Authorization: `Bearer ${accessToken}`,
                    },

                    body: JSON.stringify({
                        user_id: userId,
                    }),
                }
            );

            const data =
                await response.json();

            if (response.ok) {
                alert("Invitation sent!");

                setSearchResults([]);
                setSearchTerm("");
            } else {
                alert(
                    data.error ||
                    "Unable to send invitation"
                );
            }
        } catch (error) {
            console.error(error);

            alert("Something went wrong");
        }
    }

    //fetching existing expenses...
    async function fetchExpenses() {
        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/expenses/groups/${id}/`,
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            if (response.ok) {
                const data = await response.json();

                setExpenses(data);
            }
        } catch (error) {
            console.error(error);
        }
    }

    //submit  a new expense
    async function handleAddExpense() {
        try {
            const accessToken =
                localStorage.getItem("access");

            const payload = {
                group_id: Number(id),

                amount: Number(
                    expenseForm.amount
                ),

                currency:
                    expenseForm.currency,

                description:
                    expenseForm.description,

                split_type:
                    expenseForm.split_type,

                expense_date:
                    expenseForm.expense_date,
            };

            if (
                expenseForm.split_type ===
                "EQUAL"
            ) {
                payload.participant_ids =
                    expenseForm.participant_ids;
            } else if (
                expenseForm.split_type ===
                "EXACT"
            ) {
                payload.splits =
                    Object.entries(
                        expenseForm.splits
                    ).map(
                        ([userId, amount]) => ({
                            user_id:
                                Number(userId),

                            amount_owed:
                                Number(amount),
                        })
                    );
            } else if (
                expenseForm.split_type ===
                "PERCENTAGE"
            ) {
                payload.splits =
                    Object.entries(
                        expenseForm.splits
                    ).map(
                        ([userId, percentage]) => ({
                            user_id:
                                Number(userId),

                            percentage:
                                Number(percentage),
                        })
                    );
            }

            const response = await fetch(
                `${API_BASE_URL}/api/expenses/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        Authorization:
                            `Bearer ${accessToken}`,
                    },

                    body: JSON.stringify(payload),
                }
            );

            const data =
                await response.json();

            if (response.ok) {
                alert(
                    "Expense added successfully!"
                );

                fetchExpenses();

                setExpenseForm({
                    amount: "",
                    description: "",
                    currency: "INR",
                    expense_date: "",

                    split_type: "EQUAL",

                    participant_ids: [],

                    splits: {},
                });

                setShowExpenseForm(false);
            } else {
                alert(
                    data.error ||
                    JSON.stringify(data)
                );
            }
        } catch (error) {
            console.error(error);

            alert("Something went wrong.");
        }
    }

    //fetch expense detail..
    async function fetchExpenseDetail(
        expenseId
    ) {
        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/expenses/${expenseId}/`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${accessToken}`,
                    },
                }
            );

            if (response.ok) {
                const data =
                    await response.json();

                setExpenseDetail(data);

                setSelectedExpense(
                    expenseId
                );
            }
        } catch (error) {
            console.error(error);
        }
    }

    //fetch balances..
    async function fetchBalances() {
        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/expenses/groups/${id}/balances/`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${accessToken}`,
                    },
                }
            );

            if (response.ok) {
                const data =
                    await response.json();

                setBalances(data);
            }
        } catch (error) {
            console.error(error);
        }
    }

    //fetch settlements
    async function fetchSettlements() {
        try {
            const accessToken =
                localStorage.getItem("access");

            const response = await fetch(
                `${API_BASE_URL}/api/expenses/groups/${id}/settlements/`,
                {
                    headers: {
                        Authorization:
                            `Bearer ${accessToken}`,
                    },
                }
            );

            if (response.ok) {
                const data =
                    await response.json();

                setSettlements(data);
            }
        } catch (error) {
            console.error(error);
        }
    }

    //submit a new settlement
    async function handleAddSettlement() {
        try {
            const accessToken =
                localStorage.getItem(
                    "access"
                );

            const response = await fetch(
                `${API_BASE_URL}/api/expenses/settlements/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        Authorization:
                            `Bearer ${accessToken}`,
                    },

                    body: JSON.stringify({
                        group_id: Number(id),

                        received_by:
                            Number(
                                settlementForm.received_by
                            ),

                        amount: Number(
                            settlementForm.amount
                        ),

                        currency:
                            settlementForm.currency,

                        settlement_date:
                            settlementForm.settlement_date,

                        notes:
                            settlementForm.notes,
                    }),
                }
            );

            const data =
                await response.json();

            if (response.ok) {
                alert(
                    "Settlement added successfully."
                );

                fetchSettlements();

                fetchBalances();

                setSettlementForm({
                    received_by: "",
                    amount: "",
                    currency: "INR",
                    settlement_date: "",
                    notes: "",
                });

                setShowSettlementForm(
                    false
                );
            } else {
                alert(
                    data.error ||
                    JSON.stringify(
                        data
                    )
                );
            }
        } catch (error) {
            console.error(error);

            alert(
                "Something went wrong."
            );
        }
    }


    useEffect(() => {
        const accessToken =
            localStorage.getItem("access");

        if (!accessToken) {
            navigate("/login");

            return;
        }

        fetchGroupDetails();
        fetchExpenses();
        fetchBalances();
        fetchSettlements();
    }, [id]);

    if (!group) {
        return (
            <p>Group not found.</p>
        );
    }
    return (
        <div>
            {/*tabs section */}
            <div
                style={{
                    display: "flex",
                    gap: "10px",
                    marginBottom: "20px",
                }}
            >
                <button
                    onClick={() =>
                        setActiveTab("expenses")
                    }
                >
                    Expenses
                </button>

                <button
                    onClick={() =>
                        setActiveTab("balances")
                    }
                >
                    Balances
                </button>

                <button
                    onClick={() =>
                        setActiveTab("settlements")
                    }
                >
                    Settlements
                </button>

                <button
                    onClick={() =>
                        setActiveTab("members")
                    }
                >
                    Members
                </button>
            </div>

            {/*back button */}
            <button
                onClick={() => navigate("/")}
            >
                Back
            </button>
            {/*group details section */}
            <h1>{group.group_name}</h1>

            <p>
                <strong>Description:</strong>{" "}
                {group.description ||
                    "No description"}
            </p>

            <p>
                <strong>Admin:</strong>{" "}
                {group.admin.username}
            </p>


            {/*members section  */}
            {activeTab === "members" && (
                <>
                    <p>
                        <strong>
                            Members ({group.member_count})
                        </strong>
                    </p>

                    <ul>
                        {group.members.map((member) => (
                            <li key={member.id}>
                                {member.username} (
                                {member.email})
                            </li>
                        ))}
                    </ul>
                </>
            )}


            {/*expenses section.. */}
            {activeTab === "expenses" && (
                <>
                    <button
                        onClick={() =>
                            setShowExpenseForm(
                                !showExpenseForm
                            )
                        }
                    >
                        {showExpenseForm
                            ? "Cancel"
                            : "+ Add Expense"}
                    </button>

                    {/*expense form modal */}

                    {showExpenseForm && (
                        <div
                            style={{
                                border: "1px solid black",
                                padding: "10px",
                                marginBottom: "20px",
                            }}
                        >
                            <h3>Add Expense</h3>

                            <input
                                type="number"
                                placeholder="Amount"
                                value={expenseForm.amount}
                                onChange={(e) =>
                                    setExpenseForm({
                                        ...expenseForm,

                                        amount:
                                            e.target.value,
                                    })
                                }
                            />

                            <br />

                            <input
                                type="text"
                                placeholder="Description"
                                value={
                                    expenseForm.description
                                }
                                onChange={(e) =>
                                    setExpenseForm({
                                        ...expenseForm,

                                        description:
                                            e.target.value,
                                    })
                                }
                            />

                            <br />

                            <input
                                type="date"
                                value={
                                    expenseForm.expense_date
                                }
                                onChange={(e) =>
                                    setExpenseForm({
                                        ...expenseForm,

                                        expense_date:
                                            e.target.value,
                                    })
                                }
                            />

                            <br />
                            <select
                                value={expenseForm.split_type}
                                onChange={(e) =>
                                    setExpenseForm({
                                        ...expenseForm,
                                        split_type:
                                            e.target.value,

                                        splits: {},
                                    })
                                }
                            >
                                <option value="EQUAL">
                                    Equal
                                </option>

                                <option value="EXACT">
                                    Exact
                                </option>

                                <option value="PERCENTAGE">
                                    Percentage
                                </option>
                            </select>

                            <p>Select Participants:</p>

                            {group.members
                                .filter(
                                    (member) =>
                                        member.id !== user?.id
                                ).map(
                                    (member) => (
                                        <div key={member.id}>
                                            <label>
                                                <input
                                                    type="checkbox"

                                                    checked={
                                                        expenseForm.participant_ids.includes(
                                                            member.id
                                                        )
                                                    }

                                                    onChange={() => {
                                                        const alreadySelected =
                                                            expenseForm.participant_ids.includes(
                                                                member.id
                                                            );

                                                        setExpenseForm(
                                                            {
                                                                ...expenseForm,

                                                                participant_ids:
                                                                    alreadySelected
                                                                        ? expenseForm.participant_ids.filter(
                                                                            (
                                                                                id
                                                                            ) =>
                                                                                id !==
                                                                                member.id
                                                                        )
                                                                        : [
                                                                            ...expenseForm.participant_ids,

                                                                            member.id,
                                                                        ],
                                                            }
                                                        );
                                                    }}
                                                />

                                                {
                                                    member.username
                                                }
                                            </label>
                                        </div>
                                    )
                                )}
                            {/*selection for exact split, who gets howmuch */}
                            {expenseForm.split_type ===
                                "EXACT" &&

                                expenseForm.participant_ids.map(
                                    (participantId) => {

                                        const member =
                                            group.members.find(
                                                (m) =>
                                                    m.id ===
                                                    participantId
                                            );

                                        return (
                                            <div
                                                key={participantId}
                                            >
                                                <label>
                                                    {
                                                        member.username
                                                    }

                                                    :
                                                </label>

                                                <input
                                                    type="number"

                                                    placeholder="Amount"

                                                    value={
                                                        expenseForm
                                                            .splits[
                                                        participantId
                                                        ] || ""
                                                    }

                                                    onChange={(e) =>
                                                        setExpenseForm(
                                                            {
                                                                ...expenseForm,

                                                                splits: {
                                                                    ...expenseForm.splits,

                                                                    [
                                                                        participantId
                                                                    ]:
                                                                        e
                                                                            .target
                                                                            .value,
                                                                },
                                                            }
                                                        )
                                                    }
                                                />
                                            </div>
                                        );
                                    }
                                )}
                            {/*selectino for percentage split */}
                            {expenseForm.split_type ===
                                "PERCENTAGE" &&

                                expenseForm.participant_ids.map(
                                    (participantId) => {

                                        const member =
                                            group.members.find(
                                                (m) =>
                                                    m.id ===
                                                    participantId
                                            );

                                        return (
                                            <div
                                                key={participantId}
                                            >
                                                <label>
                                                    {
                                                        member.username
                                                    }

                                                    :
                                                </label>

                                                <input
                                                    type="number"

                                                    placeholder="%"

                                                    value={
                                                        expenseForm
                                                            .splits[
                                                        participantId
                                                        ] || ""
                                                    }

                                                    onChange={(e) =>
                                                        setExpenseForm(
                                                            {
                                                                ...expenseForm,

                                                                splits: {
                                                                    ...expenseForm.splits,

                                                                    [
                                                                        participantId
                                                                    ]:
                                                                        e
                                                                            .target
                                                                            .value,
                                                                },
                                                            }
                                                        )
                                                    }
                                                />
                                            </div>
                                        );
                                    }
                                )}
                            <button
                                onClick={handleAddExpense}
                            >
                                Save Expense
                            </button>
                        </div>
                    )}


                    {/*expense modal end---------------------- */}
                    {expenses.length === 0 ? (
                        <p>No expenses yet.</p>
                    ) : (
                        expenses.map((expense) => (
                            <div
                                key={expense.id}

                                style={{
                                    border:
                                        "1px solid black",

                                    padding: "10px",

                                    marginTop: "10px",

                                    cursor: "pointer",
                                }}

                                onClick={() =>
                                    fetchExpenseDetail(
                                        expense.id
                                    )
                                }
                            >
                                <h4>
                                    {expense.description}
                                </h4>

                                <p>
                                    Amount:{" "}
                                    {expense.currency}{" "}
                                    {expense.amount}
                                </p>

                                <p>
                                    Paid by:{" "}
                                    {
                                        expense.paid_by
                                            .username
                                    }
                                </p>

                                <p>
                                    Date:{" "}
                                    {
                                        expense.expense_date
                                    }
                                </p>
                            </div>
                        ))
                    )}

                    {/*expense detail for each expense*/}
                    {expenseDetail && (
                        <div
                            style={{
                                border: "2px solid black",

                                padding: "15px",

                                marginTop: "20px",
                            }}
                        >
                            <h3>
                                Expense Details
                            </h3>

                            <p>
                                Description:{" "}
                                {
                                    expenseDetail.description
                                }
                            </p>

                            <p>
                                Amount:{" "}
                                {
                                    expenseDetail.currency
                                }{" "}
                                {
                                    expenseDetail.amount
                                }
                            </p>

                            <p>
                                Paid by:{" "}
                                {
                                    expenseDetail.paid_by
                                        .username
                                }
                            </p>

                            <p>
                                Your balance:{" "}
                                {
                                    expenseDetail.current_user_balance
                                }
                            </p>

                            <h4>
                                Participants
                            </h4>

                            <ul>
                                {expenseDetail.participants.map(
                                    (participant) => (
                                        <li
                                            key={
                                                participant.id
                                            }
                                        >
                                            {
                                                participant.username
                                            }

                                            {" - owes "}

                                            {
                                                participant.amount_owed
                                            }
                                        </li>
                                    )
                                )}
                            </ul>

                            <button
                                onClick={() => {
                                    setExpenseDetail(
                                        null
                                    );

                                    setSelectedExpense(
                                        null
                                    );
                                }}
                            >
                                Close
                            </button>
                        </div>
                    )}
                </>
            )}

            {/*balances section.. */}
            {activeTab === "balances" && (
                <>
                    {balances.length === 0 ? (
                        <p>
                            No balances available.
                        </p>
                    ) : (
                        balances.map((balance) => (
                            <div
                                key={balance.user_id}
                                style={{
                                    border:
                                        "1px solid black",

                                    padding: "10px",

                                    marginTop: "10px",
                                }}
                            >
                                <strong>
                                    {
                                        balance.username
                                    }
                                </strong>

                                <p>
                                    Net Balance:{" "}
                                    {
                                        balance.net_balance
                                    }
                                </p>
                            </div>
                        ))
                    )}
                </>
            )}


            {/*setttlements tab */}
            {activeTab === "settlements" && (
                <>
                    <button
                        onClick={() =>
                            setShowSettlementForm(
                                !showSettlementForm
                            )
                        }
                    >
                        {showSettlementForm
                            ? "Cancel"
                            : "+ Add Settlement"}
                    </button>
                    {/*settlements modal */}
                    {showSettlementForm && (
                        <div
                            style={{
                                border: "1px solid black",
                                padding: "10px",
                                marginTop: "10px",
                            }}
                        >
                            <h3>Add Settlement</h3>

                            <select
                                value={
                                    settlementForm.received_by
                                }
                                onChange={(e) =>
                                    setSettlementForm({
                                        ...settlementForm,
                                        received_by:
                                            e.target.value,
                                    })
                                }
                            >
                                <option value="">
                                    Select user
                                </option>

                                {group.members
                                    .filter(
                                        (member) =>
                                            member.id !== user?.id
                                    ).map(
                                        (member) => (
                                            <option
                                                key={member.id}
                                                value={member.id}
                                            >
                                                {
                                                    member.username
                                                }
                                            </option>
                                        )
                                    )}
                            </select>

                            <br />

                            <input
                                type="number"
                                placeholder="Amount"
                                value={
                                    settlementForm.amount
                                }
                                onChange={(e) =>
                                    setSettlementForm({
                                        ...settlementForm,
                                        amount:
                                            e.target.value,
                                    })
                                }
                            />

                            <br />

                            <input
                                type="date"
                                value={
                                    settlementForm.settlement_date
                                }
                                onChange={(e) =>
                                    setSettlementForm({
                                        ...settlementForm,
                                        settlement_date:
                                            e.target.value,
                                    })
                                }
                            />

                            <br />

                            <input
                                type="text"
                                placeholder="Notes"
                                value={
                                    settlementForm.notes
                                }
                                onChange={(e) =>
                                    setSettlementForm({
                                        ...settlementForm,
                                        notes:
                                            e.target.value,
                                    })
                                }
                            />

                            <br />

                            <button
                                onClick={
                                    handleAddSettlement
                                }
                            >
                                Save Settlement
                            </button>
                        </div>
                    )}

                    {settlements.length === 0 ? (
                        <p>
                            No settlements yet.
                        </p>
                    ) : (
                        settlements.map(
                            (settlement) => (
                                <div
                                    key={
                                        settlement.id
                                    }
                                    style={{
                                        border:
                                            "1px solid black",

                                        padding: "10px",

                                        marginTop: "10px",
                                    }}
                                >
                                    <p>
                                        <strong>
                                            {
                                                settlement
                                                    .paid_by_username
                                            }
                                        </strong>

                                        {" paid "}

                                        <strong>
                                            {
                                                settlement
                                                    .received_by_username
                                            }
                                        </strong>
                                    </p>

                                    <p>
                                        Amount:{" "}
                                        {
                                            settlement.currency
                                        }{" "}
                                        {
                                            settlement.amount
                                        }
                                    </p>

                                    <p>
                                        Date:{" "}
                                        {
                                            settlement
                                                .settlement_date
                                        }
                                    </p>

                                    {settlement.notes && (
                                        <p>
                                            Notes:{" "}
                                            {
                                                settlement.notes
                                            }
                                        </p>
                                    )}
                                </div>
                            )
                        )
                    )}
                </>
            )}


            {group.is_admin && (
                <div
                    style={{
                        border: "1px solid black",
                        padding: "10px",
                        marginTop: "20px",
                    }}
                >
                    <h3>Invite Users</h3>

                    <input
                        type="text"
                        placeholder="Search username or email"
                        value={searchTerm}
                        onChange={(e) =>
                            setSearchTerm(e.target.value)
                        }
                    />

                    <button
                        onClick={handleSearchUsers}
                    >
                        Search
                    </button>

                    <div
                        style={{ marginTop: "10px" }}
                    >
                        {searchResults.map((user) => (
                            <div
                                key={user.id}
                                style={{
                                    border:
                                        "1px solid gray",

                                    padding: "10px",

                                    marginBottom: "10px",
                                }}
                            >
                                <p>
                                    {user.username} (
                                    {user.email})
                                </p>

                                <button
                                    onClick={() =>
                                        handleInviteUser(
                                            user.id
                                        )
                                    }
                                >
                                    Invite
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default GroupDetails