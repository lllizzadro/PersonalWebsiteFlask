const rollBtn = document.getElementById('roll-btn');
const countInput = document.getElementById('count');
const sidesInput = document.getElementById('sides');
const results = document.getElementById('results');

rollBtn.addEventListener('click', function() {
    const count = Number(countInput.value);
    const sides = Number(sidesInput.value);
    const rolls = [];
    let total = 0;

    for(let i = 0; i < count; i++)
    {
        rolls.push(Math.floor(Math.random() * sides) + 1);
        total += rolls[i];
    }

    results.textContent = `You rolled ${count} ${sides}-sided dice:\nResults: ${rolls.join(', ')}\nTotal: ${total}`;
});