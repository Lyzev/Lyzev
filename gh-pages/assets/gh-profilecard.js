const cards = document.getElementsByTagName('gh-profilecard')
for (let i = 0; i < cards.length; i++) {
    generateProfilecard(cards[i].getAttribute("user"), cards[i])
}

async function generateProfilecard(user, container) {
    const url = 'https://api.github.com/users/' + user;
    const request = new XMLHttpRequest();
    request.open("GET", url, false);
    request.send();

    const data = JSON.parse(request.responseText)

    let card = document.createElement('div');
    card.style.borderRadius = '10px'
    card.style.padding = '10px'
    card.style.margin = '10px'
    card.style.height = 'fit-content'
    card.style.width = 'fit-content'
    card.style.background = '#161616'
    card.style.display = 'flex';
    card.style.minWidth = '450px'

    let imgContainer = document.createElement('div');

    let img = document.createElement('img');
    img.src = data.avatar_url;
    img.style.borderRadius = '50%'
    img.height = 80
    img.width = 80
    imgContainer.appendChild(img)

    let dataContainer = document.createElement('div');
    dataContainer.style.marginLeft = '10px'
    dataContainer.style.display = 'flex'
    dataContainer.style.flexDirection = 'column'
    dataContainer.style.alignItems = 'flex-start'

    let name = document.createElement('a');
    name.style.fontSize = '20px'
    name.href = data.html_url
    name.target = '_blank"'
    name.innerHTML = data.login

    let desc = document.createElement('p');
    desc.style.fontSize = '12px'
    desc.style.color = '#AAAAAA'
    desc.style.margin = '0'
    desc.innerHTML = data.bio

    let statsContainer = document.createElement('div');
    statsContainer.style.display = 'flex'

    let statsContainer1 = document.createElement('div');
    statsContainer1.style.margin = '5px'
    statsContainer1.style.display = 'flex'
    statsContainer1.style.flexDirection = 'column'
    statsContainer1.style.alignItems = 'center'
    statsContainer1.style.justifyContent = 'center'
    let followers = document.createElement('a');
    followers.style.fontSize = '16px'
    followers.style.margin = '0'
    followers.href = data.html_url + '?tab=followers'
    followers.target = '_blank"'
    followers.innerHTML = data.followers
    let followerLabel = document.createElement('p');
    followerLabel.innerHTML = 'Followers'
    followerLabel.style.fontSize = '12px'
    followerLabel.style.color = '#AAAAAA'
    followerLabel.style.margin = '0'
    statsContainer1.appendChild(followers)
    statsContainer1.appendChild(followerLabel)

    let statsContainer2 = document.createElement('div');
    statsContainer2.style.margin = '5px'
    statsContainer2.style.display = 'flex'
    statsContainer2.style.flexDirection = 'column'
    statsContainer2.style.alignItems = 'center'
    statsContainer2.style.justifyContent = 'center'
    let following = document.createElement('a');
    following.style.fontSize = '16px'
    following.style.margin = '0'
    following.href = data.html_url + '?tab=following'
    following.target = '_blank"'
    following.innerHTML = data.following
    let followingLabel = document.createElement('p');
    followingLabel.innerHTML = 'Following'
    followingLabel.style.fontSize = '12px'
    followingLabel.style.color = '#AAAAAA'
    followingLabel.style.margin = '0'
    statsContainer2.appendChild(following)
    statsContainer2.appendChild(followingLabel)

    let statsContainer3 = document.createElement('div');
    statsContainer3.style.margin = '5px'
    statsContainer3.style.margin = '5px'
    statsContainer3.style.display = 'flex'
    statsContainer3.style.flexDirection = 'column'
    statsContainer3.style.alignItems = 'center'
    statsContainer3.style.justifyContent = 'center'
    let rep = document.createElement('a');
    rep.style.fontSize = '16px'
    rep.style.margin = '0'
    rep.href = data.html_url + '?tab=repositories'
    rep.target = '_blank"'
    rep.innerHTML = data.public_repos
    let repLabel = document.createElement('p');
    repLabel.innerHTML = 'Repositories'
    repLabel.style.fontSize = '12px'
    repLabel.style.color = '#AAAAAA'
    repLabel.style.margin = '0'
    statsContainer3.appendChild(rep)
    statsContainer3.appendChild(repLabel)

    statsContainer.appendChild(statsContainer1)
    statsContainer.appendChild(statsContainer2)
    statsContainer.appendChild(statsContainer3)

    dataContainer.appendChild(name)
    dataContainer.appendChild(desc)
    dataContainer.appendChild(statsContainer)

    card.appendChild(imgContainer)
    card.appendChild(dataContainer)

    container.appendChild(card)
}