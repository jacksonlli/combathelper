/* Set the width of the sidebar to 250px and the left margin of the page content to 250px */
function openNav() {
  document.getElementById("mySidebar").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
}

/* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
function closeNav() {
  document.getElementById("mySidebar").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
}

var request = new XMLHttpRequest
request.open('GET', 'http://localhost:5000/player', true)
request.onload = function() {
	var data = JSON.parse(this.response)

	if (request.status >= 200 && request.status < 400) {
    data.forEach(player => {
      console.log(player.name)
    })
	} else {
    console.log('error')
	}
}
request.send()