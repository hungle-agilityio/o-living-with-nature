# Intent: the rental enquiry form

## Problem

The goal for the next six months is at least 10 real contacts about Ở (`docs/intent/website.md`, Q6 and Q7). Today a visitor can only call or write on WhatsApp or Zalo. Some visitors, often from abroad, do not want to call a stranger or open a chat app, and leave without a word. When there is no contact channel yet, the site has no way to be reached at all.

## Goal

A short form in chapter 05 ("ở lại?") lets a visitor leave their name, how to reach them, when they would move in, for how long, and a message, in English at `/` and in Vietnamese at `/vi/`. The owner gets a push on the phone (ntfy) that a message arrived, reads it in `/owner/`, answers by email, WhatsApp or Zalo, and marks it as replied. Each message sent is counted next to the button presses. Messages are deleted 12 months after they arrive.

## Users

- **Visitor:** fills the form under the contact buttons; sees a thank-you line with the owner's reply time, or what to fix.
- **Owner (Bún):** gets a push "New enquiry on Ở" with no personal data in it, reads and marks enquiries in `/owner/`, and sees the number of messages in "Contact counts".

## Out of scope

- Sending a reply, an email or a copy to the visitor; the site never writes to the visitor.
- Booking, an availability calendar, payment.
- A CAPTCHA or any third-party script, a cookie, an IP address or a visitor id.
- Email to the owner (ntfy only).
- Exporting enquiries, attachments, more than one house.
