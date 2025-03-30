document.getElementById("surveyForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const requiredFields = form.querySelectorAll("[required]");

    for (let field of requiredFields) {
        if (field.type === "radio") {
            const radios = form.querySelectorAll(`input[name="${field.name}"]`);
            const isChecked = Array.from(radios).some(r => r.checked);

            if (!isChecked) {
                const label = radios[0].closest(".formbold-input-radio-wrapper")?.querySelector(".formbold-form-label")?.innerText || field.name;
                alert("Пожалуйста, выберите вариант: " + label);
                radios[0].scrollIntoView({ behavior: "smooth", block: "center" });
                radios[0].focus();
                return;
            }
        }

        else if (!field.value.trim()) {
            const placeholder = field.placeholder || field.name;
            alert("Пожалуйста, заполните поле: " + placeholder);
            field.scrollIntoView({ behavior: "smooth", block: "center" });
            field.focus();
            return;
        }
    }

    const modal = document.getElementById("m-loading");
    modal.style.display = "block";

    const res = await fetch("/submit", {
        method: "POST",
        body: formData
    });

    const { thread_id, run_id } = await res.json();

    let answer = null;
    while (!answer) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const check = await fetch(`/check-status?thread_id=${thread_id}&run_id=${run_id}`);
        const data = await check.json();
        if (data.answer) {
            answer = data.answer;
        }
    }

    window.location.href = `/cv/${thread_id}__${run_id}`;
});
