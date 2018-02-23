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


function plotSpread(dest, data, package, title){
    var dates = getArray(data, 'date');
    var prices = getArray(data, 'resid');
    var std = package.std;
    var top = setArray(dates.length, 2*std);
    var bottom = setArray(dates.length, -2*std);

    var trace1 = {
        x: dates,
        y: prices,
        name: 'Residual',
    };

    var trace2 = {
        x: dates,
        y: top,
        line: {
            color: 'red',
            dash: 'dash',
        },
        showlegend: false,
    };

    var trace3 = {
        x: dates,
        y: bottom,
        line: {
            color: 'red',
            dash: 'dash',
        },
        showlegend: false,
    };
    var layout = {};
    var data = [trace1, trace2, trace3];

    if (title != null){
        var layout = {title: title};
    }
    Plotly.newPlot(dest, data, layout);
};




function plot(dest, data, date, price, title=null){
    var dates = getArray(data, date);
    var plotdata = [];
    var layout = {};
    for (var i in price){
        prices = getArray(data, price[i]);
        trace = {
            x: dates,
            y: prices,
            name: price[i],
        };
        plotdata.push(trace);
    };

    if (title != null){
        var layout = {title: title};
    }
    Plotly.newPlot(dest, plotdata, layout);
};


function plotScatter(dest, data, package, date, price, title=null){
    var dates = getArray(data, date);
    var layout = {};
    var k = package.k;
    var b = package.b;
    var fitline = [];

    dep = getArray(data, price[0]);
    indep = getArray(data, price[1])
    for (var i in indep){
        fitline.push(indep[i]*k+b);
    };
    trace1 = {
        x: indep,
        y: dep,
        name: 'Scatter plot',
        mode: 'markers',
    };
    trace2 = {
        x: indep,
        y: fitline,
        name: 'Fit line',
    };
    plotdata = [trace1, trace2]

    if (title != null){
        var layout = {title: title};
    }
    Plotly.newPlot(dest, plotdata, layout);
};


function getArray(data, column){
    var dates = [];
    for (var i in data){
        dates.push(data[i][column]);
    };
    return dates
};


function validName(raw){
    var output = raw;
    if (raw.indexOf('$') > -1){
        output = raw.replace('$', '');
    };
    return output
};

function setArray(len, value){
    output = [];
    for(var i=0; i<len; i++){output.push(value);};
    return output
};


function dateRange(url, start, end){
    if (start != "")
    {
        url = url + "start=" + start;
    };

    if (end != "")
    {
        url = url +"&end=" + end;
    };

    url = url + "&id=";
    return url
};



