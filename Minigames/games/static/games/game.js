document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#startgame').addEventListener('click', startgame); 
    

    
    load_homepage();
});
// thinking of encasing everything in a if(data.roomid == document.getElementsByClassName('room').innerHTML) so that it only loads for your specific
let url = `ws://${window.location.host}/ws/socket-server/`
const gameSocket = new WebSocket(url)



function load_homepage(){
    var loads = 0
    var modal = document.getElementById("myModal");
    var span = document.getElementsByClassName("close")[0];
    span.onclick = function() {
        modal.style.display = "none";
    }
    
      
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
                            const checker_spot = []
                            console.log("ace is the place", place)
                            
                            if(place["available_space"].length ==0){
                                alert(place["player_turn"] + " loses")
                            }
                            if (place["player_turn"] == "AI" && place["available_space"].length >0){
                                setTimeout(function(){
                                    gameSocket.send(JSON.stringify({
                                        "name": document.getElementById("name").innerHTML,
                                        "roomid": document.getElementById("room").innerHTML,
                                        "AIturn": "Make AI Move"
                                    }))
                                }, 2000);
                            }
                            for(let count=0; count < place['open_spaces'].length; count++){
                                if(document.getElementById(place['open_spaces'][count]).innerHTML != ''){
                                    checker_spot.push(place['open_spaces'][count])
                                    console.log("new checker spot",checker_spot, checker_spot.length)
                                }
                                document.getElementById(place['open_spaces'][count]).innerHTML = ''
                                
                                
                            }
                                
                            for(let checker=0; checker < place["player_one"].length; checker++){
                                if(document.getElementById(place["player_one"][checker]).innerHTML == '' && checker_spot.length >0){
                                    
                                }
                                
                                document.getElementById(place["player_one"][checker]).innerHTML = `
                                <img src="/games/files/userimages/games_boardgames_artboard_15-512.png" style="width: 100%"/>
                                `
                                for(let king=0; king < place["kings"].length; king++){
                                    
                                    if(String(place["player_one"][checker]) == String(place["kings"][king])){
                                        
                                        document.getElementById(place["player_one"][checker]).innerHTML = `
                                        <img src="/games/files/userimages/black checker king.png" style="width: 100%"/>
                                        `
                                    }
                                    
                                }
                                
                                
                                
                            }
                            

                            for(let checker=0; checker < place["player_two"].length; checker++){
                                if(document.getElementById(place["player_two"][checker]).innerHTML == '' && checker_spot.length >0){
                                    
                                }
                                document.getElementById(place["player_two"][checker]).innerHTML = `
                                <img src="/games/files/userimages/red checker.png" style="width: 100%"/>
                                `
                                for(let king=0; king < place["kings"].length; king++){
                                    
                                    if(String(place["player_two"][checker]) == String(place["kings"][king])){
                                        
                                        document.getElementById(place["player_two"][checker]).innerHTML = `
                                        <img src="/games/files/userimages/red checker king.png" style="width: 100%"/>
                                        `
                                    }
                                    
                                }
                                
                                
                            }

                        })
                        
                    })
                    
                    for(let i =0; i < 8; i++){
                        for(let j=0; j < 4; j++){
                            let k = j * 2
                            let l = j * 2 +1

                            if( i % 2 == 0){
                                    
                                document.getElementById(i +"," +k).style.backgroundColor ="black"
                                
                            }
                            if( i % 2 != 0){
                                
                                document.getElementById(i +"," +l).style.backgroundColor ="black"
                            }

                        }
                    }
                    if(loads <= 0){
                        for(let i =0; i < 8; i++){
                            for(let j=0; j < 4; j++){
                                let k = j * 2
                                let l = j * 2 +1

                                function move(){
                                    
                                    
                                    fetch('/board/' + document.getElementById("room").innerHTML)
                                    .then(response => response.json())
                                    .then(placement =>{
                                        placement.forEach(place=>{
                                            if (place["player_turn"] == document.getElementById("name").innerHTML){
                                                for(let count=0; count < place['open_spaces'].length; count++){
                                                    document.getElementById(place['open_spaces'][count]).style.backgroundColor ='black'     
                                                }
                                                for(let checker=0; checker < place["available_space"].length; checker++){
                                                    
                                                    if( place['available_space'][checker][0] == String([i,k])){
                                                        
                                                        document.getElementById(place["available_space"][checker][1]).style.backgroundColor = "blue"
                                                        document.getElementById(place["available_space"][checker][1]).addEventListener('click', moving)
                                                        function moving(){
                                                            
                                                            gameSocket.send(JSON.stringify({
                                                                "name": document.getElementById("name").innerHTML,
                                                                "roomid": document.getElementById("room").innerHTML,
                                                                "moved": [place["available_space"][checker][0], [place["available_space"][checker][1]]]
                                                            }))
                                                            loads +=1
                                                            document.getElementById(place["available_space"][checker][1]).removeEventListener('click', moving)
                                                        }
                                                        
                                                    }
                                                    if( place['available_space'][checker][0] == String([i,l])){
                                                        
                                                        document.getElementById(place["available_space"][checker][1]).style.backgroundColor = "blue"
                                                        document.getElementById(place["available_space"][checker][1]).addEventListener('click', moving)
                                                        function moving(){
                                                            
                                                            
                                                            gameSocket.send(JSON.stringify({
                                                                "name": document.getElementById("name").innerHTML,
                                                                "roomid": document.getElementById("room").innerHTML,
                                                                "moved": [place["available_space"][checker][0], [place["available_space"][checker][1]]]
                                                            }))
                                                            document.getElementById(place["available_space"][checker][1]).removeEventListener('click', moving)
                                                            loads +=1
                                                        }
                                                        

                                                    }
                                                }
                                            }
                                            
                                        })

                                    })
                                }
                                function jump(){
                                    fetch('/board/' + document.getElementById("room").innerHTML)
                                    .then(response => response.json())
                                    .then(placement =>{
                                        placement.forEach(place=>{
                                            if (place["player_turn"] == document.getElementById("name").innerHTML){
                                                for(let checker=0; checker < place["jumps"].length; checker++){
                                                    console.log("checking stuff", place['jumps'][checker][0] , [i,k])
                                                    if( place['jumps'][checker][0] == String([i,k])){
                                                        console.log("checking stuff", place['jumps'][checker][0] , [i,k])
                                                        for(let jump_checker=0; jump_checker < place["jumps"][checker][1].length; jump_checker++){
                                                            document.getElementById(place["jumps"][checker][1][jump_checker]).style.backgroundColor = "blue"
                                                            document.getElementById(place["jumps"][checker][1][jump_checker]).addEventListener('click', jumping)
                                                            function jumping(){
                                                                // we have do delete the last value of place["jumps"][checker][1] and replace it with place["jumps"][checker][1][jump_checker]
                                                                // to do this i am thinking of creating a const variable 
                                                                const checkers_jumped = place["jumps"][checker][1]
                                                                checkers_jumped.push(place["jumps"][checker][1][jump_checker])
                                                                gameSocket.send(JSON.stringify({
                                                                    "name": document.getElementById("name").innerHTML,
                                                                    "roomid": document.getElementById("room").innerHTML,
                                                                    "moved": [place["jumps"][checker][0], place["jumps"][checker][1]]
                                                                }))
                                                                loads+=1
                                                                document.getElementById(place["jumps"][checker][1][jump_checker]).removeEventListener('click', jumping)
                                                            }
                                                        }
                                                        
                                                    }
                                                    if( place['jumps'][checker][0] == String([i,l])){
                                                        console.log("this is jumps available",place['jumps'][checker])
                                                        for(let jump_checker=0; jump_checker < place["jumps"][checker][1].length; jump_checker++){
                                                            document.getElementById(place["jumps"][checker][1][jump_checker]).style.backgroundColor = "blue"
                                                            document.getElementById(place["jumps"][checker][1][jump_checker]).addEventListener('click', jumping)
                                                            function jumping(){
                                                                
                                                                gameSocket.send(JSON.stringify({
                                                                    "name": document.getElementById("name").innerHTML,
                                                                    "roomid": document.getElementById("room").innerHTML,
                                                                    "moved": [place["jumps"][checker][0], place["jumps"][checker][1]]
                                                                }))
                                                                loads+=1
                                                                document.getElementById(place["jumps"][checker][1][jump_checker]).removeEventListener('click', jumping)
                                                                
                                                            }
                                                        }
                                                        

                                                    }
                                                }
                                            }

                                        })

                                    })
                                }
                                
                                if( i % 2 == 0){
                                    
                                    document.getElementById(i +"," +k).addEventListener('click', move.bind())
                                    document.getElementById(i +"," +k).addEventListener('click', jump.bind())
                                    
                                }
                                if( i % 2 != 0){
                                    
                                    document.getElementById(i +"," +l).addEventListener('click', move.bind())
                                    document.getElementById(i +"," +l).addEventListener('click', jump.bind())
                                }
                            
                            }
                        }
                        loads +=1
                    }
                    // not sure if this needs to be here at the moment
                    fetch('/board/' + document.getElementById("room").innerHTML)
                    .then(response => response.json())
                    .then(placement =>{
                        
                    })
                }
                else {
                    while ( i< data.team_owners.length){
                        console.log(data.team_owners)
                        if(!document.getElementById("team_one").innerHTML.includes(data.team_owners[i])){
                            document.getElementById("team_one").innerHTML += `
                            <option value="${data.team_owners[i]}">${data.team_owners[i]}</option>
                            `
                            document.getElementById("team_two").innerHTML += `
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
                let i =0;
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

