from flask import Flask, render_template, request, jsonify

from categories import EXPENSE_CATEGORIES
from sheets import add_transaction

app = Flask(__name__)

@app.route("/")
def home():
    return render_template(
        "index.html",
        categories=EXPENSE_CATEGORIES,
    )


@app.route("/submit", methods=["POST"])
def submit_form():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received.",
        }), 400

    transaction_type = data.get("transaction_type")
    note = data.get("note", "").strip()

    try:
        amount = round(float(data.get("amount", 0)), 2)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Please enter a valid amount.",
        }), 400

    if amount <= 0:
        return jsonify({
            "success": False,
            "message": "Amount must be greater than zero.",
        }), 400

    if transaction_type not in ("income", "expense"):
        return jsonify({
            "success": False,
            "message": "Invalid transaction type.",
        }), 400

    need_or_want = ""
    reason = ""

    if transaction_type == "expense":
        need_or_want = data.get("need_or_want", "")
        reason = data.get("reason", "")

        if need_or_want not in ("Need", "Want"):
            return jsonify({
                "success": False,
                "message": "Please choose Need or Want.",
            }), 400

        if reason not in EXPENSE_CATEGORIES:
            return jsonify({
                "success": False,
                "message": "Please choose a valid spending category.",
            }), 400

    try:
        add_transaction(
            transaction_type=transaction_type,
            amount=amount,
            note=note,
            need_or_want=need_or_want,
            reason=reason,
        )

    except Exception:
        app.logger.exception("Failed to save transaction to Google Sheets.")

        return jsonify({
            "success": False,
            "message": (
                "Couldn't save your transaction to Google Sheets. "
                "Please check the server terminal for details."
            ),
        }), 500

    return jsonify({
        "success": True,
        "message": "Transaction saved to Google Sheets successfully!",
    })


if __name__ == "__main__":
    app.run(debug=True)