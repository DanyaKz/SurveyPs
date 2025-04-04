document.addEventListener("DOMContentLoaded", async () => {
    const resultDiv = document.getElementById("result");

    try {
        const response = await fetch("/get_portrait");
        if (!response.ok) {
            resultDiv.innerHTML = "<p>Произошла ошибка при получении данных.</p>";
            return;
        }
        const data = await response.json();
        console.log(data)
        const text = await data.portrait;

        let total = data.stats.total_responses;
        let sat = data.stats.satisfied;
        let unsat = data.stats.unsatisfied;
        let conclusion = `<br><strong>Опрос ${pluralizeThrow(data.stats.total_users)} 
            <u>${pluralizeStudents(data.stats.total_users)}</u>
        <br>На вопрос "Повлиял ли данный опрос на Ваше понимание дальнейшего профессионального пути?" 
            ${pluralizeAnswer(total)} <u>${pluralizeStudents(total)}</u> 
        <br> Положительно: <u>${sat} (${(sat/total*100).toFixed(2)}%)</u>
        <br> Отрицательно: <u>${unsat} (${(unsat/total*100).toFixed(2)}%)</u>
            </strong>`

        resultDiv.innerHTML = text + conclusion;
    
    } catch (error) {
        console.error("Ошибка запроса:", error);
        resultDiv.innerHTML = "<p>Не удалось загрузить результат.</p>";
    }
});

function pluralizeStudents(n) {
    n = Math.abs(n) % 100;
    const n1 = n % 10;

    if (n > 10 && n < 20) return `${n} студентов`;
    if (n1 > 1 && n1 < 5) return `${n} студента`;
    if (n1 === 1) return `${n} студент`;
    return `${n} студентов`;
}

function pluralizeAnswer(n) {
    n = Math.abs(n) % 100;
    const n1 = n % 10;

    if (n > 10 && n < 20) return `ответили`;
    if (n1 > 1 && n1 < 5) return `ответило`;
    if (n1 === 1) return `ответил(а)`;
    return `ответили`;
}

function pluralizeThrow(n) {
    n = Math.abs(n) % 100;
    const n1 = n % 10;

    if (n > 10 && n < 20) return `прошли`;
    if (n1 > 1 && n1 < 5) return `прошло`;
    if (n1 === 1) return `прошел(а)`;
    return `прошли`;
}