document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#startgame').addEventListener('click', startgame); 
    document.querySelector('#roll-dice').addEventListener('click', rolldice);
    document.querySelector('#end-turn').addEventListener('click', endturn);

    
    load_homepage();
});
// thinking of encasing everything in a if(data.roomid == document.getElementsByClassName('room').innerHTML) so that it only loads for your specific
let url = `ws://${window.location.host}/ws/socket-server/`
const gameSocket = new WebSocket(url)
var player_turn = "unknown"
var remove_oldpos = []


function load_homepage(){
    var loads = 0
    var modal = document.getElementById("myModal");
    
    
      
    // since gameSocket creates another instance once it receives data, perhaps I can have gameSocket update an already established javascript.
    gameSocket.onmessage = function(e){
        let data = JSON.parse(e.data)
        console.log('Data:', data)
        if(data.type === 'firstload'){
            e.preventDefault();
            gameSocket.send(JSON.stringify({
                "name": document.getElementById("name").innerHTML,
                "roomid": document.getElementById("room").innerHTML,
            }))
            
            
        }
        console.log("this is room",document.getElementById('room').innerHTML)
    
        if(data.type === document.getElementById('room').innerHTML){
            console.log("hello there")
            
            fetch('/started/' + document.getElementById("room").innerHTML)
            .then(response => response.json())
            .then(started =>{
                if(started ==  true){
                    document.getElementById("myModal").style.display = "none";
                    fetch('/board/' + document.getElementById("room").innerHTML)
                    .then(response => response.json())
                    .then(placement =>{
                        
                        
                        placement.forEach(place=>{

                            player_turn= place["player_turn"]
                            console.log("ace is the place", place)

                            if (player_turn == document.getElementById("name").innerHTML){
                                if(place["rolled_dice"]== false){
                                    document.getElementById("roll-dice").style.display = "show"
                                    document.getElementById("end-turn").style.display = "none"
                                    
                                }
                                else{
                                    document.getElementById("end-turn").style.display = "show"
                                }
                            }
                            else{
                                document.getElementById("roll-dice").style.display = "none"
                                document.getElementById("end-turn").style.display = "none"
                            }
                            const monop_pieces = ["/games/files/userimages/monopoly-game-piece-car (1).jpg", "/games/files/userimages/monopoly-game-piece-battleship.jpg","/games/files/userimages/monopoly-game-piece-dog.jpg", "/games/files/userimages/monopoly-game-piece-hat.jpg"]
                            for(let oldpos=0; oldpos < remove_oldpos.length; oldpos++){
                                const element = document.getElementById(remove_oldpos[oldpos]);
                                element.remove();
                            }
                            for(let position=0; position < place["positions"].length; position++){
                                let y = position*15
                                
                                document.getElementById(place["positions"][position]).innerHTML+= `
                                <svg width="45" height="45" y="${y}" style="border:1px solid" id="gamepiece${place["positions"][position]}">
                                    <defs>
                                    <clipPath id="myCircle">
                                        <rect  stroke="black" width="78" height="100"></rect>
                                    </clipPath>
                                    </defs>
                                    <image width="45" height="45" xlink:href="${monop_pieces[position]}" clip-path="url(#myCircle)" />
                                </svg>
                                `  
                                remove_oldpos.push("gamepiece"+place["positions"][position])
                                
                            }

                        
                           
                            

                           

                        })
                        
                    })
                    
                    
                    if(loads <= 0){
                        
                            

                        
                            
                        
                        loads +=1
                    }
                    // not sure if this needs to be here at the moment

                }
                
                else {
                    let i =0;
                    while ( i< data.team_owners.length){
                        console.log(data.team_owners)
                        if(!document.getElementById("team_one").innerHTML.includes(data.team_owners[i])){
                            document.getElementById("team_one").innerHTML += `
                            <option value="${data.team_owners[i]}">${data.team_owners[i]}</option>
                            `
                            document.getElementById("team_two").innerHTML += `
                            <option value="${data.team_owners[i]}">${data.team_owners[i]}</option>
                            `
                            document.getElementById("team_three").innerHTML += `
                            <option value="${data.team_owners[i]}">${data.team_owners[i]}</option>
                            `
                            document.getElementById("team_four").innerHTML += `
                            <option value="${data.team_owners[i]}">${data.team_owners[i]}</option>
                            `
                            
                            
                            
                            if(data.team_owners[i] !="AI" ){
                                document.getElementById("lobby_players").innerHTML += `
                                ${data.team_owners[i]}
                                <br>
                                `
                            }
                        }
                        i++;
                    }
                }
                
            })


            console.log("this is loads", loads)  
        }
    
    


        
    }
    
}

function startgame(e){
    e.preventDefault();
    document.getElementById("myModal").style.display = "none";
    gameSocket.send(JSON.stringify({
        "name": document.getElementById("name").innerHTML,
        "roomid": document.getElementById("room").innerHTML,
        "started": true,
        "team_one": document.getElementById("team_one").value,
        "team_two": document.getElementById("team_two").value,
    }))
}

// When we make this function work, we have to also set the value of the rolled_dice table to true
function rolldice(e){
    e.preventDefault();
    alert(Math.floor(Math.random() * 12))
    const node = document.createElement("p");
    node.innerHTML = "chicken poptart"
    document.getElementById("gamelog").appendChild(node)
    gameSocket.send(JSON.stringify({
        "name": document.getElementById("name").innerHTML,
        "roomid": document.getElementById("room").innerHTML,
        "moved": true,
        
    }))
    return ;
}

// When we make this function work, we have to also set the value of the rolled_dice table to false
function endturn(e){
    e.preventDefault();
    alert("ROLL DICE TIME FOR"+ player_turn)
}
 