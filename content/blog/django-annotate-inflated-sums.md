---
id: 159
created: '2026-11-27T12:00:00+00:00'
modified: '2026-11-27T12:00:00+00:00'
title: Why Django annotate() triples your sum when you add a count
slug: django-annotate-inflated-sums
status: PB
description: Two $5 tickets and three helpers should still mean $10 in sales. Reproduce an inflated Django sum, see why DISTINCT undercounts, and fix the queryset.
level: INTERMEDIATE
type: TUTORIAL
tag_list:
- id: 1
  name: Django
  slug: django
- id: 2
  name: Models
  slug: models
author: 1
---
An event organizer sells two $5 tickets. The dashboard says $10. You add a count of volunteers to the same Django queryset, and suddenly the dashboard says $30. Nobody bought another ticket. The new join changed what a row means **before** the database calculated the sum.

The fix is to sum the tickets **per event, inside their own query**, then attach that number to the event. Don't reach for `Sum(..., distinct=True)`: in this example it turns $30 into $5, not $10.

## Reproduce the wrong total

Here are the models for a small event app. Each ticket row represents one sale. Each helper row represents one volunteer assignment. Amounts are integer cents in a single currency.

```python
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=80)


class Ticket(models.Model):
    event = models.ForeignKey(Event, related_name="tickets", on_delete=models.CASCADE)
    cents = models.IntegerField()


class Helper(models.Model):
    event = models.ForeignKey(Event, related_name="helpers", on_delete=models.CASCADE)
```

After migrating the models in a disposable app, import them in the Django shell. Give one workshop two identically priced tickets and three helpers. Give a second event a helper but no tickets: it should remain visible on the organizer's report.

```python
workshop = Event.objects.create(name="Workshop")
meetup = Event.objects.create(name="Meetup")
for cents in (500, 500):
    Ticket.objects.create(event=workshop, cents=cents)
for _ in range(3):
    Helper.objects.create(event=workshop)
Helper.objects.create(event=meetup)
```

Now ask for the helper count and ticket revenue together. The third annotation checks a tempting repair in the same query:

```python
from django.db.models import Count, Sum

report = Event.objects.annotate(
    helpers_n=Count("helpers"),
    gross=Sum("tickets__cents"),
    distinct_gross=Sum("tickets__cents", distinct=True),
)
print(list(report.order_by("pk").values_list("helpers_n", "gross", "distinct_gross")))
# On a fresh database: [(6, 3000, 500), (1, None, None)]
```

The workshop joins ticket A to helpers 1, 2 and 3, then ticket B to helpers 1, 2 and 3. The database counts six helper appearances and adds 500 cents six times. Try `print(report.query)` and look for both child tables joined to the event before the grouping.

## Choose what counts as a duplicate

For headcount, the unit is a helper assignment, so `Count("helpers", distinct=True)` counts its primary key once. For sales, the unit is a **ticket**, not a **price**. Both real tickets cost 500 cents. Summing distinct amounts keeps only one of those values, even though the tickets have different primary keys. The [Django aggregation guide](https://docs.djangoproject.com/en/5.2/topics/db/aggregation/#combining-multiple-aggregations) explains the multiple-join problem; [SQLite's aggregate reference](https://www.sqlite.org/lang_aggfunc.html) spells out which input values DISTINCT removes.

A fixture with one ticket and one helper won't catch either error. A fixture with two *different* prices catches the inflated join but lets the distinct-price repair pass. The equal prices are deliberate.

## Sum tickets before counting helpers

```python
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce

ticket_totals = (
    Ticket.objects.filter(event_id=OuterRef("pk"))
    .order_by()
    .values("event_id")
    .annotate(total=Sum("cents"))
    .values("total")
)

report = Event.objects.annotate(
    helpers_n=Count("helpers"),
    gross=Coalesce(Subquery(ticket_totals), 0),
)
assert list(report.order_by("pk").values_list("helpers_n", "gross")) == [
    (3, 1000),
    (1, 0),
]
```

Read from the inside out. The filter picks tickets for the current event. The empty `order_by()` clears model ordering; the first `values()` sets the grouping key. The last one selects just the total. Because the filter pins a single event and the group is that event, the inner query can return at most one row. For the meetup it returns **no row**, so the outer `Coalesce` supplies zero. The only child rows left to count in the outer query are helper assignments. Django documents this sequence under [aggregates within a Subquery](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#using-aggregates-within-a-subquery-expression).

We ran both querysets on Django 5.2.14 with SQLite 3.53.1. The assertion checks correctness, not speed. If your page displays revenue alone, the simple sum over tickets doesn't need the helper join or this workaround. If you're reviewing a dashboard in a [Django project with source code](/projects/), trace each displayed number back to the rows it should count. A useful regression test for this report: adding a volunteer must change headcount without moving revenue by a cent.
