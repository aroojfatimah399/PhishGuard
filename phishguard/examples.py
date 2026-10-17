"""Example emails for the dashboard's one-click demo buttons."""
EXAMPLES = {
    "Phishing: bank account suspended": (
        "URGENT: Your account has been suspended",
        "Dear Customer,\n\nWe detected unusual activity and your account has been suspended. "
        "You must verify your password and card details within 24 hours or your account will be "
        "permanently closed.\n\nClick here: http://secure-paypal-verify.top/login?id=88231\n\n"
        "Security Team"),
    "Phishing: prize / refund": (
        "Congratulations! You have won $50,000",
        "Dear winner,\n\nYou've been selected to claim your prize. Confirm your bank account details "
        "immediately at http://192.168.44.12/claim to receive your refund. Keep this confidential.\n"),
    "Legitimate: team meeting": (
        "Notes from Tuesday's project meeting",
        "Hi team,\n\nThanks for joining. Next steps: Sara will update the test plan, Ali will "
        "finish the dashboard charts, and we meet again on Friday at 10:00 in Room 204. "
        "The slides are on the shared drive.\n\nBest,\nImran"),
    "Legitimate: order receipt": (
        "Your order #48213 has shipped",
        "Hello Ayesha,\n\nYour order has shipped and should arrive in 3-5 business days. "
        "Track it any time at https://www.amazon.com/your-orders. No action is needed.\n\n"
        "Thanks for shopping with us."),
}
