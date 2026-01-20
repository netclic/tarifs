// Gestion de l'affichage du champ plateforme (utile seulement en mode tableau)
document.getElementsByName('mode').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const plateGroup = document.getElementById('plateforme-group');
        if (plateGroup) {
            plateGroup.style.display = e.target.value === 'tableau' ? 'block' : 'none';
        }
    });
});

const inputDebut = document.getElementById('date_debut');
const inputFin = document.getElementById('date_fin');
const inputNbJours = document.getElementById('nb_jours');

// Mise à jour de la date de fin quand on change début ou nombre de jours
function majDateFin() {
    if (inputDebut.value && inputNbJours.value) {
        const debut = new Date(inputDebut.value);
        const nbJours = parseInt(inputNbJours.value);
        // Date de fin = début + N jours (ex: du 1er au 8 = 7 jours/nuitées)
        const fin = new Date(debut);
        fin.setDate(debut.getDate() + nbJours);
        inputFin.value = fin.toISOString().split('T')[0];
    }
}

// Mise à jour du nombre de jours quand on change la date de fin
function majNbJours() {
    if (inputDebut.value && inputFin.value) {
        const debut = new Date(inputDebut.value);
        const fin = new Date(inputFin.value);
        const diffTime = fin - debut;
        // Différence brute en jours (sans le +1 inclusif)
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        inputNbJours.value = diffDays > 0 ? diffDays : 1;
    }
}

inputDebut.addEventListener('change', majDateFin);
inputNbJours.addEventListener('input', majDateFin);
inputFin.addEventListener('change', majNbJours);

document.getElementById('calc-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const mode = formData.get('mode');
    
    // On cache les sections de résultats précédentes
    document.querySelectorAll('.result-section').forEach(s => s.classList.add('hidden'));

    if (mode === 'tableau') {
        await afficherTableau(formData);
    } else {
        await afficherDetail(formData);
    }
});

async function afficherTableau(formData) {
    const params = new URLSearchParams(Object.fromEntries(formData)).toString();
    const plate = formData.get('plateforme');
    
    const response = await fetch(`/tableau?${params}`);
    const data = await response.json();

    const tbody = document.querySelector('#tarifs-table tbody');
    tbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.debut}</td><td>${row.fin}</td><td>${row.periode}</td><td>${row.prix_semaine_unit} €</td><td>${row.prix_weekend_unit} €</td><td>${row.prix_semaine_7j}</td>`;
        tbody.appendChild(tr);
    });

    const downloadBtn = document.querySelector('.btn-download');
    downloadBtn.href = `/download-csv${plate ? '?plateforme=' + plate : ''}`;
    document.getElementById('results-table').classList.remove('hidden');
}

async function afficherDetail(formData) {
    const params = new URLSearchParams(Object.fromEntries(formData)).toString();
    const response = await fetch(`/detail?${params}`);
    const data = await response.json();

    document.getElementById('total-price').innerHTML = `<strong>Total : ${data.total.toFixed(2)} €</strong> (${data.nb_nuitees} nuits)`;
    document.getElementById('avg-price').innerHTML = `Prix moyen par nuit : ${data.moyenne.toFixed(2)} €`;

    const list = document.getElementById('daily-list');
    list.innerHTML = '';
    data.details.forEach(day => {
        const li = document.createElement('li');
        li.innerText = `${day[0]} : ${day[1].toFixed(2)} €`;
        list.appendChild(li);
    });

    document.getElementById('results-detail').classList.remove('hidden');
}