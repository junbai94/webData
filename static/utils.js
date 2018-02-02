function plotBBANDS(dest, data, date, prices, n, title=null){
    var dates = getArray(data, 'date');
    var spreads = getArray(data, 'spread');
    var ma = getArray(data, 'MA_'+n);
    var upper = getArray(data, 'BollingerU_'+n);
    var lower = getArray(data, 'BollingerL_'+n);


    var trace1 = {
        x: dates,
        y: spreads,
        name: 'Spread',
    };
    var trace2 = {
        x: dates,
        y: ma,
        name: 'MA',
    };
    var trace3 = {
        x: dates,
        y: upper,
        name: 'Upper',
        line: {
            color: 'red',
            dash: 'dash',
        },
    };
    var trace4 = {
        x: dates,
        y: lower,
        name: 'Lower',
        line: {
            color: 'red',
            dash: 'dash',
        },
    };

    var layout = {};
    var data = [trace1, trace2, trace3, trace4];

    if (title != null){
        var layout = {title: title};
    }
    Plotly.newPlot(dest, data, layout);
};


function getArray(data, column){
    var dates = [];
    for (var i in data){
        dates.push(data[i][column]);
    };
    return dates
};


function plot(dest, dates, prices, title=null){
    var data = [{
        x: dates,
        y: prices,
    }];
    var layout = {}

    if (title != null){
        var layout = {title: title};
    }
    Plotly.newPlot(dest, data, layout);
};