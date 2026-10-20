
const form = document.getElementById("transaction-form");
const expenseFields = document.getElementById("expense-fields");
const needOrWantInputs = document.querySelectorAll(
    'input[name="need_or_want"]'
);
const reasonInput = document.getElementById("reason");
const formMessage = document.getElementById("form-message");
const submitButton = document.getElementById("submit-button");

const transactionTypeInputs = document.querySelectorAll(
    'input[name="transaction_type"]'
);

function updateTransactionForm() {
    const selectedType = document.querySelector(
        'input[name="transaction_type"]:checked'
    );

    const isExpense = selectedType?.value === "expense";

    expenseFields.hidden = !isExpense;

    needOrWantInputs.forEach((input) => {
        input.required = isExpense;
    });

    reasonInput.required = isExpense;

    if (!isExpense) {
        needOrWantInputs.forEach((input) => {
            input.checked = false;
        });

        reasonInput.value = "";
    }

    formMessage.textContent = "";
}

transactionTypeInputs.forEach((input) => {
    input.addEventListener("change", updateTransactionForm);
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
        return;
    }

    const formData = new FormData(form);

    const transaction = {
        transaction_type: formData.get("transaction_type"),
        amount: formData.get("amount"),
        note: formData.get("note").trim(),
        need_or_want: formData.get("need_or_want") || "",
        reason: formData.get("reason") || ""
    };

    submitButton.disabled = true;
    formMessage.textContent = "Processing transaction...";

    try {
        const response = await fetch("/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transaction)
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Transaction failed.");
        }

        form.reset();
    updateTransactionForm();
    formMessage.textContent ="✓ Transaction received! Ready for your next entry.";

    } catch (error) {
        formMessage.textContent =
            error.message || "Something went wrong. Please try again.";
    } finally {
        submitButton.disabled = false;
    }
});

updateTransactionForm();
