---
metadata:
  harness.story: "DEMO-1"
---

# DEMO-1: volume discount on quotes

Synthetic story used to demonstrate the `story-delivery` workflow.

As a buyer, I want a 10% discount on a quote whose total is at least 100.00,
so that bulk purchases are cheaper.

## Acceptance criteria

1. Given lines totalling 100.00 or more, when I request a quote, the response has `total` (before discount),
   `discount` = 10% of total rounded half-up to 2 decimals, and `payable` = total - discount.
2. Given lines totalling less than 100.00, `discount` is 0.00 and `payable` equals `total`.
3. Invalid lines still return 422.
