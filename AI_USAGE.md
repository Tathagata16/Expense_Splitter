# AI_USAGE.md

## Overview

This document describes how AI tools were used during the development of the Expense Splitter application.

AI was treated as an assistant for:

* brainstorming,
* exploring implementation alternatives,
* accelerating boilerplate development,
* debugging,
* deployment troubleshooting.

All AI-generated outputs were manually reviewed, tested, and modified before being incorporated into the final system.

---

# AI Tools Used

## 1. ChatGPT

### Usage

Used throughout the project for:

* architectural discussions,
* database schema validation,
* Django REST Framework implementation guidance,
* React integration assistance,
* debugging deployment issues,
* generating documentation templates.

### Role

Served as a technical advisor and pair programmer rather than an autonomous code generator.

---

# Representative Prompts Used

Examples of prompts used during development include:

---

## Prompt 1

```text
now we'll be starting with the #feature_3, which is starting an expense in a group or with a member on the app. 
for an one to one expense, database treats it as a group, just type = direct, rest same...
and for starting an expense in a group,
1. anyone can start an expense
    also while starting an expense, the split may occur in different types (mentioned in the schema)
2 . that person can select which group members to add in the expense...
3. at a time a group member may have more than one expense running...
4. the group shows net owes or owed for each member in the group, and the user's net balance itself highlighted...
5. there is a settle feature in the group as well to settle some part of the expense


so in the frontend, there might be another section for one to one expense balances...


now...for adding expense, the user adding gets a form to add some data about the transaction...you can take the input fields from the schema...

the schema looks like this....
Expense table->
expense_id

group_id

paid_by

amount

currency

description

split_type

expense_date

created_at

ExpenseSplit
split_id

expense_id

user_id

amount_owed


settlements_table...
settlement_id

group_id

paid_by

received_by

amount

currency

settlement_date

notes

settlements from each user in the group, should reflect inside the settlement history...for each transaction...


now for your clarity implementing...you can ask the necessary questions regarding gaps in your understanding...

I'll be making a new app for the expenses...
so plan accordingly
```

### Purpose

Plan the expense app inside the django app

---

## Prompt 2

```text
1. the split types are...
equal, percentage, share and exact..
2. no the person who initiates the transaction, automatically pays its part...
3. no a transaction amount cannot be edited...use a modal before submitting the expense add form to make sure the user avoid wrong entry...
4. yes, partially allowed...
5. should support usd and INR for now...there will be an option for an user to see the values in usd/inr(toggle button)
6. Reject overpaying...
7.separate tabs...for each transaction..as I said, each group can have multiple transactions with different group members...
8. Global group wise balances and per user balance in a transaction and in the group total..both
        Just to be clear on this point...A group may contain sevaral transactions..each transaction may have different members on it...
      when user clicks on a transaction, they can see, how much everybody's balance, how much is his balance in that transaction...
      and over the group, the user can see his overall balance to pay or to get from others...

9. after searching, if a user creates....one on one transaction with the user, it automatically creates direct group...

10.both

```

### Purpose

Give AI the architectural context and clarity and fill logical gaps

---

## Prompt 3

```text
ok so the new feature that I'm going to code now is csv import...
lets set the context first
1. The app has a csv import section, where the csv contains payers name, who paid who, date, amount...
2. the csv might contain data inconsistencies...
3. the data have to be serialized first, processed to make sense for our app. ...


our app currently have this architecture built alraedy....
-> an user creates  a group
->an user initiates an expense in the group and adds participants for that expense...
-> an user can add the split type on how money should be split 
-> 3 split types are there..

let me give you the schemas....
Users->
id
username
email
password
created_at

Groups->
id
group_name
group_type
created_by
admin
description
created_at

Group members..
group_id
user_id

joined_at

left_at

Expenses..
expense_id

group_id

paid_by

amount

currency

description

split_type

expense_date

created_at


Expense splits..
split_id

expense_id

user_id

amount_owed

Settlements..
settlement_id

group_id

paid_by

received_by

amount

currency

settlement_date

notes

so what the csv import app will do is...
save the import data
find out the annomallies that will rise while adding expenses and splits to the db
the users sees an popup while the processing happens on the csv about the anomalies and the change needed for the row to be included in the expense/split

if the user approves move forward
else exclude the row...

 my plan for imports schema is like this...
import jobs..
import_job_id

uploaded_by

created_at

status

import anomalies..
anomaly_id

import_job_id

row_number

anomaly_type

description

proposed_action

user_decision

then the serialized data is save in the db accordingly...
now ask me the important questions to clarify this feature..
I want an new django app for this feature..

```

### Purpose

Assist with building the csv import feature

---

# Cases Where AI Output Was Incorrect

The following examples illustrate situations where AI-generated suggestions were incorrect or incomplete, and how they were identified and corrected.

---

# Case 1: Exact Split Logic

## AI Suggestion

The initial implementation assumed that all participants, including the payer, would explicitly provide exact split values.

This led to validation logic equivalent to:

```text
sum(amount_owed) == expense_amount
```

---

## Problem Identified

The intended user experience required that:

* users specify only the other participants' shares,
* the payer's share be calculated automatically.

The AI-generated approach contradicted the desired product behaviour.

---

## How It Was Detected

Manual walkthrough of example scenarios revealed inconsistencies between the implementation and the intended workflow.

---

## Final Decision

The validation was modified to require:

```text
sum(participant_shares) < expense_amount
```

The payer's share is computed as:

```text
expense_amount − participant_shares
```

---

# Case 2: Percentage Split Implementation

## AI Suggestion

The generated implementation attempted to calculate totals using:

```python
split["amount_owed"]
```

for percentage-based splits.

---

## Problem Identified

Percentage splits only provided:

```python
split["percentage"]
```

This caused runtime errors.

---

## How It Was Detected

Code review identified a mismatch between:

* serializer expectations,
* frontend payload structure,
* backend processing logic.

---

## Final Decision

The implementation was revised to:

1. calculate participant shares using percentages,
2. derive the payer's percentage automatically,
3. generate explicit ExpenseSplit records for all participants.

---

# Case 3: Deployment and CORS Configuration

## AI Suggestion

The initial deployment guidance configured:

```python
CORS_ALLOWED_ORIGINS
```

using the Railway backend domain.

---

## Problem Identified

CORS validation depends on the browser origin, which in this architecture is the Vercel frontend domain.

Using the backend domain failed to satisfy browser preflight checks.

---

## How It Was Detected

Browser developer tools showed:

```text
Access-Control-Allow-Origin
```

errors during signup requests.

---

## Final Decision

The configuration was updated to allow:

```text
https://expense-splitter-iota-silk.vercel.app
```

instead of the backend domain.

---

# Case 4: Direct Expense Modelling

## AI Suggestion

An early recommendation involved creating separate models and APIs for direct expenses.

---

## Problem Identified

This duplicated:

* balance logic,
* settlement logic,
* expense handling workflows.

---

## How It Was Detected

Architectural review highlighted substantial overlap with standard groups.

---

## Final Decision

Direct expenses were modelled as groups with a dedicated type field:

```text
DIRECT
```

allowing reuse of existing infrastructure.

---

# Validation Strategy for AI Output

AI-generated suggestions were never incorporated without verification.

Validation methods included:

* manual code review,
* scenario walkthroughs,
* unit-level testing using Postman,
* end-to-end frontend testing,
* deployment verification in production environments.

---

# Reflection

AI significantly accelerated development by reducing time spent on:

* boilerplate generation,
* framework-specific syntax lookup,
* debugging guidance,
* documentation drafting.

However, the project demonstrated that effective AI usage requires:

* critical evaluation,
* domain understanding,
* systematic testing.

Several important architectural decisions emerged only after identifying and correcting shortcomings in AI-generated suggestions.

The final implementation reflects human judgement informed by, rather than replaced by, AI assistance.
