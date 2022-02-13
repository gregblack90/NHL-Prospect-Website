document.getElementById("dd").onchange = function(){update_chart()};

// this function updates the chart within the myCanvas canvas
function update_chart(){

    // get selected value from drop down meny
    var selected_season = document.getElementById("dd").value;

    // nned to reset canvas to completely destroy old chart
    var reset_canvas = function() {
        // remove canvas
        document.getElementById('myCanvas').remove();
        // replace canvas
        // create new canvas
        var canvas = document.createElement('canvas')
        // re-ID canvas
        canvas.id = 'myCanvas'
        // tell it where to go
        var container = document.querySelector('.chart-holder')
        // append canvas
        container.appendChild(canvas);
        };
    reset_canvas()
    
    // remove iframes
    var iframes = document.querySelectorAll('iframe');
    for (var i = 0; i < iframes.length; i++) {
        iframes[i].parentNode.removeChild(iframes[i]);
    }

    // if 'selected season' was chosen, generate nothing
    if(selected_season == 'select_season') {
        return;
    }
    // if 'career' was chosen, generate proper chart
    else if(selected_season == 'career') {
        // parse data from backend
        var data_career = '{{ max_totals|tojson }}'
        var unique_season = '{{ unique_season|tojson }}'
        var json_careerData = JSON.parse(data_career)
        var json_uniqueSeason = JSON.parse(unique_season)
        // need to assmble lists to be displayed in bar chart
        // create array of unique seasons to loop over
        array = json_uniqueSeason
        // create empty arrays
        var total_goals = [];
        var total_assists = [];
        var total_points = [];
        var total_gp = [];
        // for each season, update arrays with total goals, assists, points and gp for each unique season
        array.forEach(function (item) {
            total_goals.push(json_careerData[item]["Goals"])
            total_assists.push(json_careerData[item]["Assists"])
            total_points.push(json_careerData[item]["Points"])
            total_gp.push(json_careerData[item]["GP"])
        })
        // create chart data
        var career_chart_data = {
            labels: json_uniqueSeason,
            datasets: [{
                label: 'Goals',
                backgroundColor: 'red',
                data: total_goals
            }, {
                label: 'Assists',
                backgroundColor: 'green',
                data: total_assists
            }, {
                label: 'Points',
                backgroundColor: 'blue',
                data: total_points
            },{
                label: 'Games Played',
                backgroundColor: 'gray',
                data: total_gp
            }]
        };
        // create chart
        var career_chart = new Chart(document.getElementById("myCanvas"), {
            type: "bar",
            data: career_chart_data
        })
        }
    // if anything else, i.e. a season value, was chosen, generate proper chart
    else {
        // parse data from backend
        var data = '{{ data_dict|tojson }}';
        var jsonData = JSON.parse(data);
        var goals = jsonData[selected_season]["Goals"];
        var assists = jsonData[selected_season]["Assists"];
        var points = jsonData[selected_season]["Points"];
        var dates = jsonData[selected_season]["Dates"];
        // create chart
        var chart = new Chart(document.getElementById("myCanvas"), {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    data: goals,
                    label: "Goals",
                    borderColor: "#3e95cd",
                    fill: false
                }, {
                    data: assists,
                    label: "Assists",
                    borderColor: "#8e5ea2",
                    fill: false
                }, {
                    data: points,
                    label: "Points",
                    borderColor: "#3cba9f",
                    fill: false
                }]},
            options: {
                title: {
                display: true,
                text: selected_season + ': Cumulative Season Totals'
                },
                hover: {
                mode: 'index',
                intersect: true
                },}
            });
        };
    }