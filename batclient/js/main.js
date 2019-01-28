//const API_ENDPOINT = "http://localhost:8000/api"
var lightAnims = ["red", "green", "orange"];

// Create top bank of blinking lights
for(let y = 0; y < 3; y++) {
  for(let x = 0; x < 19; x++) {
    let dur = (Math.random() * 1700) + 200;
    let delay = Math.random() * 1500;
    var animColour = lightAnims[Math.floor(Math.random() * lightAnims.length)];
    document.getElementById('main').innerHTML += `<div class="light" style="animation-name: ${animColour}; 
      top: ${290-110+(y*28)}px; left: ${265+(x*35)}px; 
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
      top: ${598-110+(y*28)}px; left: ${265+(x*35)}px; 
      animation-duration: ${dur}ms; animation-delay: ${delay}ms"></div>`;
  }
}

//
// Connect to API and populate dropdown lists
//
function connect(endpoint) {
  endpoint = endpoint.endsWith('/') ? endpoint.substring(0, endpoint.length - 1) : endpoint
  API_ENDPOINT = endpoint;

  document.getElementById('connectEndpoint').value = "Please wait..."
  document.getElementById('connectButton').style.visibility = "hidden"

  fetch(`${API_ENDPOINT}/predict/params`)
  .then(resp => resp.json())
  .then(data => {
    forceSelect = document.getElementById('force');
    for(let force of data.force) {
      let forceName = force.replace("Metropolitan Police Service", "Greater London")
      forceName = forceName.replace("Police", "")
      forceName = forceName.replace("Constabulary", "")
      
      forceSelect.innerHTML += `<option value="${force}">${forceName}</option>`
    }
    crimeSelect = document.getElementById('crime');
    for(let crime of data.crime) {
      crimeSelect.innerHTML += `<option value="${crime}">${crime}</option>`
    }   
    
    document.getElementById('connectPanel').style.visibility = 'hidden'
  })
  .catch(err => {
    console.log(err);
    printOut("MAINFRAME ERROR<br>API PROBLEM!", true)
  })
}

//
// Call API and model, and process results
//
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

  computeStart()
  clearPrintout()

  fetch(`${API_ENDPOINT}/predict`, req)
  .then(resp => resp.json())
  .then(data => {
    let caught = data.caughtProb * 100;
    caught = parseInt(caught);
    let gotAway = data.notCaughtProb * 100;
    gotAway = parseInt(gotAway);        
    printOut(`Caught: ${caught}%<br>Get Away: ${gotAway}%`)
    computeDone()
  })
  .catch(err => {
    console.log(req);
    console.log(err);
    printOut("MAINFRAME ERROR<br>API PROBLEM!", true)
  })
}

function clearPrintout() {
  document.getElementById('result').innerHTML = ""
  document.getElementById('result').style.visibility = 'hidden'
  document.getElementById('result').style.animation = ''
}

function computeStart() {
  document.getElementById('computePanel').style.visibility = 'visible'

  for(let l of document.getElementsByClassName('light')) {
    l.style.animationDuration = ((Math.random() * 150) + 20) + 'ms'
  }
}

function computeDone() {
  document.getElementById('computePanel').style.visibility = 'hidden'

  for(let l of document.getElementsByClassName('light')) {
    l.style.animationDuration = ((Math.random() * 1700) + 200) + 'ms';
  }
}

function printOut(msg, err=false) {
  clearPrintout()

  setTimeout(() => {
    document.getElementById('result').style.color = err ? 'red' : 'black'
    document.getElementById('result').innerHTML = msg
    document.getElementById('result').style.visibility = 'visible'
    document.getElementById('result').style.animation = 'printout 2s'
  }, 50)
}  

// ENTRYPOINT - START HERE

computeDone()

// If endpoint set in config.js
if(API_ENDPOINT) {
  connect(API_ENDPOINT)
}