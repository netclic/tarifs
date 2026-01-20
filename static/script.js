// Gestion de l'affichage du champ plateforme (utile seulement en mode tableau)

// Variables pour mémoriser les dates du mode séjour
const inputDebut = document.getElementById('date_debut');
const inputFin = document.getElementById('date_fin');
const inputNbJours = document.getElementById('nb_jours');

let memoSejour = {
    debut: inputDebut.value,
    fin: inputFin.value,
    nb: inputNbJours.value
};

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

document.getElementsByName('mode').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const mode = e.target.value;
        const plateGroup = document.getElementById('plateforme-group');
        const year = new Date().getFullYear();

        // NETTOYAGE : On cache et on vide les sections de résultats dès qu'on change de mode
        document.querySelectorAll('.result-section').forEach(section => {
            section.classList.add('hidden');
            // On vide aussi les contenus pour repartir à zéro
            const tbody = section.querySelector('tbody');
            if (tbody) tbody.innerHTML = '';
            const list = section.querySelector('ul');
            if (list) list.innerHTML = '';
        });

        if (mode === 'tableau') {
            // Sauvegarde des dates actuelles avant de passer en mode tableau
            memoSejour.debut = inputDebut.value;
            memoSejour.fin = inputFin.value;
            memoSejour.nb = inputNbJours.value;

            // Passage aux dates de l'année complète
            inputDebut.value = `${year}-01-01`;
            inputFin.value = `${year}-12-31`;
            majNbJours(); // Recalcule le nombre de jours pour l'année

            if (plateGroup) plateGroup.style.display = 'block';
        } else {
            // Retour au mode détail : on restaure les dates mémorisées
            inputDebut.value = memoSejour.debut;
            inputFin.value = memoSejour.fin;
            inputNbJours.value = memoSejour.nb;

            if (plateGroup) plateGroup.style.display = 'none';
        }
    });
});

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
        // day[0] contient déjà "mercredi  04-04-2026" grâce à Python
        const prixLabel = day[1].toFixed(2).padStart(7, ' '); 
        li.innerText = `${day[0]} : ${prixLabel} €`;
        list.appendChild(li);
    });

    document.getElementById('results-detail').classList.remove('hidden');
}