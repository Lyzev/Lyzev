const cache = new Map()

const repocards = document.getElementsByTagName('gh-repocards')
for (let i = 0; i < repocards.length; i++) {
    const url = 'https://api.github.com/users/' + repocards[i].getAttribute('user') + '/repos';
    const request = new XMLHttpRequest();
    request.open("GET", url, false);
    request.send();
    const data = JSON.parse(request.responseText)
    for (let i = 0; i < data.length; i++) {
        cache.set(data[i].full_name.toUpperCase(), data[i])
    }
    shuffle(data)
    for (let j = 0; j < Math.min(parseInt(repocards[i].getAttribute("repos")), data.length); j++) {
        const repocard = document.createElement('gh-repocard')
        repocard.setAttribute('user', repocards[i].getAttribute('user'))
        repocard.setAttribute('repo', data[j].name)
        repocards[i].appendChild(repocard)
    }
    repocards[i].style.display = 'flex'
    repocards[i].style.flexDirection = 'column'
    repocards[i].style.alignItems = 'center'
    repocards[i].style.justifyContent = 'center'
}

const repocard = document.getElementsByTagName('gh-repocard')
for (let i = 0; i < repocard.length; i++) {
    generateRepocard(repocard[i].getAttribute("user"), repocard[i].getAttribute("repo"), repocard[i])
}

async function generateRepocard(user, repo, container) {
    let data = cache.get((user + "/" + repo).toUpperCase())
    if (data == null) {
        const url = 'https://api.github.com/repos/' + user + '/' + repo;
        const request = new XMLHttpRequest();
        request.open("GET", url, false);
        request.send();
        data = JSON.parse(request.responseText)
    }

    const card = document.createElement('div');
    card.style.borderRadius = '10px'
    card.style.padding = '10px'
    card.style.margin = '10px'
    card.style.height = 'fit-content'
    card.style.width = 'fit-content'
    card.style.background = '#161616'
    card.style.display = 'flex';
    card.style.minWidth = '450px'

    const imgContainer = document.createElement('div');

    const img = document.createElement('img');
    img.src = data.owner.avatar_url;
    img.style.borderRadius = '50%'
    img.height = 80
    img.width = 80
    imgContainer.appendChild(img)

    const dataContainer = document.createElement('div');
    dataContainer.style.marginLeft = '10px'
    dataContainer.style.display = 'flex'
    dataContainer.style.flexDirection = 'column'
    dataContainer.style.alignItems = 'flex-start'

    const name = document.createElement('a');
    name.style.fontSize = '20px'
    name.href = data.html_url
    name.target = '_blank"'
    name.innerHTML = data.full_name

    const desc = document.createElement('p');
    desc.style.fontSize = '12px'
    desc.style.color = '#AAAAAA'
    desc.style.margin = '0'
    desc.innerHTML = data.description

    const statsContainer = document.createElement('div');
    statsContainer.style.display = 'flex'

    const statsContainer1 = document.createElement('div');
    statsContainer1.style.margin = '5px'
    statsContainer1.style.display = 'flex'
    statsContainer1.style.flexDirection = 'column'
    statsContainer1.style.alignItems = 'center'
    statsContainer1.style.justifyContent = 'center'
    const forks = document.createElement('a');
    forks.style.fontSize = '16px'
    forks.style.margin = '0'
    forks.href = data.html_url + '/network/members'
    forks.target = '_blank"'
    forks.innerHTML = data.forks_count
    const forksLabel = document.createElement('p');
    forksLabel.innerHTML = 'Forks'
    forksLabel.style.fontSize = '12px'
    forksLabel.style.color = '#AAAAAA'
    forksLabel.style.margin = '0'
    statsContainer1.appendChild(forks)
    statsContainer1.appendChild(forksLabel)

    const statsContainer2 = document.createElement('div');
    statsContainer2.style.margin = '5px'
    statsContainer2.style.display = 'flex'
    statsContainer2.style.flexDirection = 'column'
    statsContainer2.style.alignItems = 'center'
    statsContainer2.style.justifyContent = 'center'
    const stars = document.createElement('a');
    stars.style.fontSize = '16px'
    stars.style.margin = '0'
    stars.href = data.html_url + '/stargazers'
    stars.target = '_blank"'
    stars.innerHTML = data.stargazers_count
    const starslabel = document.createElement('p');
    starslabel.innerHTML = 'Stars'
    starslabel.style.fontSize = '12px'
    starslabel.style.color = '#AAAAAA'
    starslabel.style.margin = '0'
    statsContainer2.appendChild(stars)
    statsContainer2.appendChild(starslabel)

    let statsContainer3 = null
    if (data.language != null) {
        statsContainer3 = document.createElement('div');
        statsContainer3.style.margin = '5px'
        statsContainer3.style.margin = '5px'
        statsContainer3.style.display = 'flex'
        statsContainer3.style.flexDirection = 'column'
        statsContainer3.style.alignItems = 'center'
        statsContainer3.style.justifyContent = 'center'
        const lang = document.createElement('a');
        lang.style.fontSize = '16px'
        lang.style.margin = '0'
        lang.href = data.html_url + '/search?l=' + data.language
        lang.target = '_blank"'
        lang.innerHTML = data.language
        const langLabel = document.createElement('p');
        langLabel.innerHTML = 'Language'
        langLabel.style.fontSize = '12px'
        langLabel.style.color = '#AAAAAA'
        langLabel.style.margin = '0'
        statsContainer3.appendChild(lang)
        statsContainer3.appendChild(langLabel)
    }

    statsContainer.appendChild(statsContainer1)
    statsContainer.appendChild(statsContainer2)
    if (statsContainer3 != null)
        statsContainer.appendChild(statsContainer3)

    dataContainer.appendChild(name)
    dataContainer.appendChild(desc)
    dataContainer.appendChild(statsContainer)

    card.appendChild(imgContainer)
    card.appendChild(dataContainer)

    container.appendChild(card)
}

function shuffle(sourceArray) {
    for (let i = 0; i < sourceArray.length - 1; i++) {
        const j = i + Math.floor(Math.random() * (sourceArray.length - i));

        const temp = sourceArray[j];
        sourceArray[j] = sourceArray[i];
        sourceArray[i] = temp;
    }
    return sourceArray;
}