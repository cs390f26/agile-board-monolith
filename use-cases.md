# Use cases

This system is an agile board for project managers and engineers. A **manager** creates tickets, assigns them to engineers, and monitors progress. An **engineer** works on the tickets assigned to them. Users pick a role by entering a name and a simple password; there are no other accounts.

A **ticket** has a title, a description, a category (new feature or maintenance), an optional time limit, an assigned engineer, and a status. The status is always one of three lanes: **Backlog**, **In progress**, or **Done**. Lanes appear in that order everywhere.

---

## Access

Someone opens the application and chooses who they are.

They enter a name and a simple password. A manager lands on the project dashboard. An engineer lands on their own ticket board.

If the name or password is missing or wrong, sign-in fails and they are told the input is invalid.

### Scenarios

- **Manager sign-in** — Valid manager credentials. They open the project dashboard.
- **Engineer sign-in** — Valid engineer credentials. They open that engineer's ticket board.
- **Invalid input** — Missing or incorrect name or password. They stay on the sign-in page and see that the input is invalid.

---

## View the project dashboard

A manager wants to see the state of all work.

They see every ticket in three lanes (Backlog, In progress, Done). Each lane shows its ticket count. Each ticket shows its title and the engineer it is assigned to. The manager's name is shown in the top right.

When there are no tickets, each lane is empty.

### Scenarios

- **Empty lanes** — There are no tickets. Each lane shows a count of zero and an empty message.
- **Lanes with data** — Each ticket appears in the lane matching its status, with its title and assigned engineer.
- **Counts** — Each lane's count matches the number of tickets it contains.

---

## Filter the dashboard by engineer

A manager wants to see one engineer's work.

They open the engineer dropdown in the top right, which lists every engineer on the project plus an "All engineers" option. Choosing an engineer shows only that engineer's tickets, still grouped in the three lanes. Choosing "All engineers" shows everything again.

### Scenarios

- **Single engineer** — Only tickets assigned to that engineer are shown, and lane counts reflect only those tickets.
- **All engineers** — Every ticket is shown.
- **Engineer with no tickets** — All three lanes are empty.

---

## Add a team member

A manager wants to bring an engineer onto the project.

They provide the engineer's name. The system adds the engineer to the project, and they appear in the dashboard dropdown and can be assigned tickets.

If the name is missing, blank, or already belongs to another engineer, adding fails and the manager is told the input is invalid.

### Scenarios

- **Successful add** — A valid, unique name. The engineer appears in the dropdown.
- **Invalid input** — A blank or duplicate name. No engineer is added.

---

## Create and assign a ticket

A manager wants to give an engineer new work.

They provide:

- a title
- a description
- a category (new feature or maintenance)
- an engineer to assign it to
- optionally, a time limit

The system creates the ticket in the Backlog and it appears on both the dashboard and the assigned engineer's board.

If the title or engineer is missing, or the category is not one of the two allowed values, creation fails and the manager is told the input is invalid.

### Scenarios

- **Successful create** — Valid input. The ticket appears in the Backlog with the chosen engineer.
- **Cancel** — The manager leaves without submitting. No ticket is created.
- **Invalid input** — For example, a missing title. Creation does not proceed and the manager sees that the input is invalid.

---

## View my tickets

An engineer wants to see their own work.

They see only the tickets assigned to them, in the three lanes with a count on each. Tickets belonging to other engineers are never shown. A link takes them back to the sign-in page.

### Scenarios

- **Own tickets only** — Only tickets assigned to this engineer are shown.
- **Empty board** — The engineer has no tickets. Each lane is empty.
- **Unknown engineer** — The engineer does not exist. They are told it was not found.

---

## Update ticket status

An engineer has moved forward, or back, on a ticket.

They move one of their own tickets to another lane (for example, by dragging it). The system updates the ticket's status and the lane counts. The change is visible to the manager on the dashboard.

Engineers can only change status. They cannot create, edit, delete, or reassign tickets.

### Scenarios

- **Move to In progress** — A Backlog ticket moves to In progress. Counts on both lanes update.
- **Move to Done** — An In progress ticket moves to Done. Counts on both lanes update.
- **Move back** — A ticket can be moved to an earlier lane.
- **Not their ticket** — An engineer cannot move a ticket assigned to someone else.

---

## View progress overview

A manager wants a quick read on how the project is going.

They see how many tickets are done compared with the total, and the count in each lane. The overview reflects the current state of all tickets.

### Scenarios

- **Progress summary** — Shows tickets done out of total, plus counts for Backlog, In progress, and Done.
- **No tickets** — All counts are zero.
