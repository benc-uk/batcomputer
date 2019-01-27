const API_ENDPOINT = "http://localhost:8000/api"
var lightAnims = ["red", "green", "orange"];

// Create top bank of blinking lights
for(let y = 0; y < 3; y++) {
  for(let x = 0; x < 19; x++) {
    let dur = parseInt((Math.random() * 900) + 100);
    let delay = parseInt((Math.random() * 900) + 100);
    var animColour = lightAnims[Math.floor(Math.random() * lightAnims.length)];
    document.getElementById('main').innerHTML += `<div class="light" style="animation-name: ${animColour}; 
      top: ${291-80+(y*28)}px; left: ${265+(x*35)}px; 
      animation-duration: ${dur}ms; animation-delay: ${delay}ms"></div>`;
  }
}

// Create bottom bank of blinking lights
for(let y = 0; y < 3; y++) {
  for(let x = 0; x < 19; x++) {
    let dur = (Math.random() * 1700) + 200;
    let delay = Math.random() * 1500;
    var animColour = lightAnims[Math.floor(Math.random() * lightAnims.length)];
    document.getElementById('main').innerHTML += `<div class="light" style="animation-name: ${animColour}; 
      top: ${599-80+(y*28)}px; left: ${265+(x*35)}px; 
      animation-duration: ${dur}ms; animation-delay: ${delay}ms"></div>`;
  }
}

function connect() {
  fetch(`${API_ENDPOINT}/predict/params`)
  .then(resp => resp.json())
  .then(data => {
    forceSelect = document.getElementById('force');
    for(let force in data.force) {
      forceSelect.innerHTML += `<option value="${force}">${force}</option>`
    }
    crimeSelect = document.getElementById('crime');
    for(let crime in data.crime) {
      crimeSelect.innerHTML += `<option value="${crime}">${crime}</option>`
    }   
    
    document.getElementById('connectPanel').style.visibility = 'hidden'
  })
  .catch(err => {
    console.log(err);
    printOut("MAINFRAME ERROR<br>API PROBLEM!", true)
  })
}

function compute() {
  let req = {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      force: document.getElementById('force').value,
      crime: document.getElementById('crime').value,
      month: parseInt(document.getElementById('month').value)
    })
  }

  fetch(`${API_ENDPOINT}/predict`, req)
  .then(resp => resp.json())
  .then(data => {
    let caught = data.caughtProb * 100;
    caught = parseInt(caught);
    let gotAway = data.notCaughtProb * 100;
    gotAway = parseInt(gotAway);        
    printOut(`Caught: ${caught}%<br>Get Away: ${gotAway}%`)
  })
  .catch(err => {
    console.log(req);
    console.log(err);
    printOut("MAINFRAME ERROR<br>API PROBLEM!", true)
  })
}

function printOut(msg, err=false) {
  document.getElementById('result').innerHTML = ""
  document.getElementById('result').style.visibility = 'hidden'
  document.getElementById('result').style.animation = ''
  document.getElementById('result').style.color = err ? 'red' : 'black'

  setTimeout(() => {
    document.getElementById('result').innerHTML = msg
    document.getElementById('result').style.visibility = 'visible'
    document.getElementById('result').style.animation = 'printout 2s'
  }, 50)
}  
