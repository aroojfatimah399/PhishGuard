"""Generate a SYNTHETIC demo dataset (data/sample_emails.csv).

This exists only so the app and tests run out of the box. It is NOT a real
dataset: metrics measured on it are unrealistically high. For the final
submission, train on a real corpus (see data/README.md and prepare_dataset.py).
"""
import csv
import random
from pathlib import Path

rnd = random.Random(42)
NAMES = ["Ayesha", "Bilal", "Sara", "Omar", "Hina", "Daniel", "Priya", "Lucas", "Mei", "Zain"]
BRANDS = ["PayPal", "Microsoft", "Apple", "Amazon", "Netflix", "DHL", "FedEx", "Google", "Facebook", "Dropbox"]
BANKS = ["Habib Bank", "Chase", "HSBC", "Wells Fargo", "Standard Chartered", "Barclays", "Meezan Bank"]
LEGIT_DOMAINS = ["amazon.com", "microsoft.com", "google.com", "github.com", "linkedin.com", "dropbox.com"]


def bad_url(brand):
    b = brand.lower().replace(" ", "")
    tld = rnd.choice(["top", "xyz", "click", "com", "net", "support", "tk"])
    return rnd.choice([
        f"http://{b}-secure-login.{tld}/verify?id={rnd.randint(1000, 99999)}",
        f"http://{b}.account-update.{tld}/signin",
        f"http://{rnd.randint(11,223)}.{rnd.randint(0,255)}.{rnd.randint(0,255)}.{rnd.randint(1,254)}/{b}/login",
        f"http://bit.ly/{rnd.choice(['3xYz','2aBc','4Qrs','1KLm'])}{rnd.randint(10,99)}",
        f"https://secure.{b}.verify-{rnd.randint(10,99)}.{tld}/auth",
        f"http://www.{b}-support.{tld}/help/{rnd.randint(100,999)}"])


def good_url(domain=None):
    d = domain or rnd.choice(LEGIT_DOMAINS)
    return f"https://www.{d}/{rnd.choice(['account','orders','docs','help','notifications'])}"


PHISH = [
    lambda n, b, bank: (f"URGENT: Your {b} account has been suspended",
        f"Dear Customer,\n\nWe noticed unusual activity and your {b} account has been suspended. You must "
        f"verify your password and card details within {rnd.choice([12,24,48])} hours or the account will "
        f"be permanently closed.\n\nClick here: {bad_url(b)}\n\n{b} Security Team"),
    lambda n, b, bank: (f"Action required: confirm your {bank} login",
        f"Dear {bank} user,\n\nTo avoid restriction of your online banking, confirm your login credentials "
        f"immediately. Log in now: {bad_url(bank)}\n\nFailure to respond will lead to account termination."),
    lambda n, b, bank: (f"Congratulations! You've won ${rnd.randint(5,90)*1000:,}",
        f"Dear winner,\n\nYou have been selected in our {b} loyalty lottery. To claim your prize, provide "
        f"your bank account details and a small processing fee via gift cards. Keep this confidential.\n"
        f"Claim: {bad_url(b)}"),
    lambda n, b, bank: (f"Your {b} refund of ${rnd.randint(40,900)}.{rnd.randint(10,99)} is waiting",
        f"Hello {n},\n\nWe could not deposit your refund. Update your card number and security code to "
        f"receive it. This offer expires today.\n{bad_url(b)}"),
    lambda n, b, bank: (f"Package delivery failed - {b}",
        f"Your parcel could not be delivered. Download the attached shipping form or open {bad_url(b)} "
        f"and enter your card details to pay the redelivery fee within 24 hours."),
    lambda n, b, bank: ("Quick favour needed",
        f"Hi {n},\n\nI'm in a meeting and cannot talk. I need you to purchase {rnd.randint(3,8)} gift cards "
        f"for a client today and send me the codes. Do not discuss this with anyone. I will reimburse you."),
    lambda n, b, bank: (f"Security alert: someone signed in to your {b} account",
        f"We detected a login from an unknown device. Confirm your identity or your account will be locked: "
        f"{bad_url(b)}\nVerify your password now."),
    # subtle / hard positives (little pressure language)
    lambda n, b, bank: (f"{n}, a document was shared with you",
        f"{n} shared 'Q{rnd.randint(1,4)} budget review' with you. View the file here {bad_url('dropbox')} "
        f"to sign in and open it."),
    lambda n, b, bank: (f"Invoice #{rnd.randint(1000,9999)} attached",
        f"Hello,\n\nPlease see the attached invoice and sign in to the portal at {bad_url(b)} to approve "
        f"payment. Let me know once done."),
    lambda n, b, bank: (f"Payroll update for {n}",
        f"HR has updated the payroll portal. Re-enter your bank details and login at {bad_url('microsoft')} "
        f"before the next pay cycle."),
]

LEGIT = [
    lambda n, b, bank: (f"Notes from {rnd.choice(['Tuesday','Monday','Thursday'])}'s project meeting",
        f"Hi team,\n\nThanks for joining. Next steps: {n} will update the test plan, we review the dashboard "
        f"charts on Friday at {rnd.randint(9,16)}:00 in Room {rnd.randint(100,320)}. Slides are on the shared drive.\n\nBest,\nImran"),
    lambda n, b, bank: (f"Your order #{rnd.randint(10000,99999)} has shipped",
        f"Hello {n},\n\nYour order has shipped and should arrive in {rnd.randint(2,6)} business days. Track it "
        f"at {good_url('amazon.com')}. No action is needed.\n\nThanks for shopping with us."),
    lambda n, b, bank: (f"Receipt for your {b} subscription",
        f"Hi {n},\n\nThanks for your payment of ${rnd.randint(5,60)}.{rnd.randint(10,99)}. You can download "
        f"your receipt from {good_url()}. Questions? Reply to this email."),
    lambda n, b, bank: ("Assignment deadline reminder",
        f"Dear students,\n\nThis is a reminder that the cybersecurity lab report is due next {rnd.choice(['Monday','Wednesday','Friday'])}. "
        f"Submit it on the course portal. Office hours are Thursday 2-4pm. Regards, Dr. {n}"),
    lambda n, b, bank: ("Weekly newsletter: new articles and events",
        f"Hello {n},\n\nThis week: a guide to Python virtual environments, an intro to Streamlit, and our "
        f"community meetup on Saturday. Read more at {good_url('github.com')}. Unsubscribe any time."),
    lambda n, b, bank: (f"New sign-in to your {b} account",
        f"Hi {n},\n\nWe noticed a new sign-in from a Windows laptop. If this was you, no action is needed. "
        f"If not, review your activity at {good_url()} or change your password from your account settings."),
    lambda n, b, bank: ("Lunch on Friday?",
        f"Hey {n}, are we still on for lunch on Friday? I was thinking the place near the library at "
        f"{rnd.randint(12,13)}:30. Let me know. Thanks!"),
    lambda n, b, bank: (f"Invoice {rnd.randint(1000,9999)} for March consulting",
        f"Hi {n},\n\nAttached is the invoice for March. Payment is due within 30 days by bank transfer to the "
        f"account on the invoice. Thank you for your business.\n\nRegards, Accounts"),
    lambda n, b, bank: ("URGENT: server maintenance tonight",
        f"Team, urgent heads-up: the staging server will be down tonight from 22:00 to 23:00 for maintenance. "
        f"Please save your work. Details are on the wiki. - IT"),
    lambda n, b, bank: (f"Interview confirmation - {rnd.choice(['Tuesday','Thursday'])}",
        f"Dear {n},\n\nWe are pleased to confirm your interview on {rnd.choice(['Tuesday','Thursday'])} at "
        f"{rnd.randint(9,15)}:00. Please bring a copy of your CV. We look forward to meeting you."),
]


def main(n_per_class=500):
    rows, seen = [], set()
    for label, templates in ((1, PHISH), (0, LEGIT)):
        count = 0
        while count < n_per_class:
            subj, body = rnd.choice(templates)(rnd.choice(NAMES), rnd.choice(BRANDS), rnd.choice(BANKS))
            if (subj, body) in seen:
                continue
            seen.add((subj, body)); rows.append((subj, body, label)); count += 1
    rnd.shuffle(rows)
    out = Path(__file__).resolve().parent.parent / "data" / "sample_emails.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["subject", "body", "label"]); w.writerows(rows)
    print(f"Wrote {len(rows)} synthetic emails to {out}")


if __name__ == "__main__":
    main()
