const userId = document.querySelector(".feedback-section").dataset.userId;

  async function sendFeedback(value) {
    const res = await fetch(`/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_id: userId,
        was_satisfied: value
      })
    });

    if (res.ok) {
      highlightAnswer(value);
    }
  }

  function highlightAnswer(value) {
    const yesBtn = document.getElementById("yesBtn");
    const noBtn = document.getElementById("noBtn");

    if (value === true) {
      yesBtn.className = "btn btn-success";
      noBtn.className = "btn btn-outline-danger";
    } else {
      yesBtn.className = "btn btn-outline-success";
      noBtn.className = "btn btn-danger";
    }
  }

  window.addEventListener("DOMContentLoaded", async () => {
    const res = await fetch(`/feedback/${userId}`);
    const data = await res.json();

    if (data.was_satisfied !== null) {
      highlightAnswer(data.was_satisfied);
    }
  });