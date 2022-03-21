document.getElementById("dd").onchange = function(){filter_data()};

function filter_data(){
    //data = '{{ season_totals|tojson }}'
    //console.log(data)
    //for (var key in data) {
        //console.log(data[key])
        //}

// FILTER SEASON TOTAL TABLE
    let table_season, rows_season, cells_season, filter_season, year_season;
    table_season = document.getElementById('season-total-table');
    rows_season = table_season.getElementsByTagName('tr');
    filter_season = document.getElementById('dd').value;
    console.log(filter_season)
    for (let row_season of rows_season) {
        cells_season = row_season.getElementsByTagName('td');
        year_season = cells_season[0] || null;
        //skip undefined row
        if (year_season == null){
            continue;
        }
        //if career was selected, show all rows
        if (filter_season == 'career'){
            row_season.style.display = '';
            continue;
        }
        //if selected season matches the year, show row
        if (filter_season == year_season.textContent) {
            row_season.style.display = '';
        }
        //if selected season does not match the year, hide row
        else {
            row_season.style.display = 'none';
        }
    }
// FILTER GAME LOG TABLE
    // set variables
    let table, rows, cells, filter, year;
    table = document.getElementById('game-log-table');
    rows = table.getElementsByTagName('tr');
    filter = document.getElementById('dd').value;
    for (let row of rows) {
        cells = row.getElementsByTagName('td');
        year = cells[0] || null;
        //skip undefined row
        if (year == null){
            continue;   
        }
        //if career was selected, show all rows
        if (filter == 'career') {
            row.style.display = '';
            continue;
        }
        //if selected season matches the year, show row
        if (filter == year.textContent){
            row.style.display = '';
        }
        //if selected season does not match the year, hide row
        else {
            row.style.display = 'none';
        }
    }

// CHANGE CHART
    // get selected value from drop down meny
    var selected_season = document.getElementById("dd").value;

    // need to reset canvas to completely destroy old chart
    var reset_canvas = function() {
        // remove canvas
        document.getElementById('chart-canvas').remove();
        // replace canvas
        // create new canvas
        var canvas = document.createElement('canvas')
        // re-ID canvas
        canvas.id = 'chart-canvas'
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
        var career_chart = new Chart(document.getElementById("chart-canvas"), {
            type: "bar",
            data: career_chart_data,
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
        var games_played = jsonData[selected_season]["GP"];
        // create chart
        var chart = new Chart(document.getElementById("chart-canvas"), {
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
                }, {
                    data: games_played,
                    label: "Games Played",
                    borderColor: 'gray',
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
