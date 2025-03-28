function parseCSV(file, callback) {
    Papa.parse(file, {
        header: true,
        complete: function(results) {
            callback(results.data);
        }
    });
}

function createCharts(data) {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const rollingAveragePeriod = parseInt(document.getElementById('rollingAveragePeriod').value, 10);

    const filteredData = filterDataByDateRange(data, startDate, endDate);

    const timestamps = filteredData.map(row => new Date(row.Timestamp).getTime());
    const frequencies = [5000000, 10000000, 15000000, 20000000, 25000000];

    const signalStrengthData = frequencies.map(freq => ({
        name: `${freq / 1000000} MHz`,
        data: filteredData.map(row => [parseFloat(row[`Signal_Strength_${freq}`])])
    }));

    const snrData = frequencies.map(freq => ({
        name: `${freq / 1000000} MHz`,
        data: filteredData.map(row => [parseFloat(row[`SNR_${freq}`])])
    }));

    const drapData = filteredData.map(row => parseFloat(row.DRAP_Value));
    const sunData = filteredData.map(row => parseFloat(row.Sun_Elevation));
    const flareData = filteredData.map(row => parseFloat(row.Normalized_Value));

    createHighcharts('signalStrengthChart', 'Signal Strength', timestamps, signalStrengthData, 'Time', 'Signal Strength', rollingAveragePeriod);
    createHighcharts('snrChart', 'Signal/Noise Ratio', timestamps, snrData, 'Time', 'Signal/Noise Ratio', rollingAveragePeriod);

    createHeatmap(
        'flareHeatmap', 
        'Flaring Values', 
        timestamps, 
        flareData, 
        "Flare", 
        [
            [0, '#000000'],
            [Math.log10(0.1) / Math.log10(20000), '#FF00FF'],
            [Math.log10(1) / Math.log10(20000), '#0000FF'],
            [Math.log10(10) / Math.log10(20000), '#00FFFF'],
            [Math.log10(100) / Math.log10(20000), '#008000'],
            [Math.log10(1000) / Math.log10(20000), '#FFA500'],
            [Math.log10(10000) / Math.log10(20000), '#800080'],
            [1, '#FF0000']
        ],
        Math.min(0.01),
        Math.max(20000),
        "logarithmic"
    );

    createHeatmap(
        'sunHeatmap', 
        'Sun Elevation', 
        timestamps, 
        sunData, 
        "Sun Elevation", 
        [
            [-1, '#000000'],
            [-0.1, '#000000'],
            [0, '#FF4500'],
            [1, '#FFFF00']
        ],
        -10,
        90
    );

    createHeatmap(
        'drapHeatmap', 
        'DRAP Values', 
        timestamps, 
        drapData, 
        "DRAP", 
        [
            [0, '#00008B'],
            [0.1, '#0000FF'],
            [0.2, '#00FFFF'],
            [0.3, '#00FF00'],
            [0.4, '#ADFF2F'],
            [0.5, '#FFFF00'],
            [0.6, '#FFD700'],
            [0.7, '#FFA500'],
            [0.8, '#FF4500'],
            [0.9, '#FF0000'],
            [1, '#8B0000']
        ],
        0,
        30
    );
}

function filterDataByDateRange(data, startDate, endDate) {
    if (!startDate && !endDate) return data;

    const startTimestamp = startDate ? new Date(startDate).getTime() : -Infinity;
    const endTimestamp = endDate ? new Date(endDate).getTime() : Infinity;

    return data.filter(row => {
        const timestamp = new Date(row.Timestamp).getTime();
        return timestamp >= startTimestamp && timestamp <= endTimestamp;
    });
}

function calculateRollingAverage(data, period) {
    let result = [];
    if (isNaN(period) || period < 1) period = 1;
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push(null);
        } else {
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j][0];
            }
            result.push(sum / period);
        }
    }
    return result;
}

function createHighcharts(elementId, title, timestamps, series, xLabel, yLabel, rollingAveragePeriod) {
    const rollingAverageSeries = series.map(s => ({
        name: s.name,
        data: calculateRollingAverage(s.data, rollingAveragePeriod)
    }));

    Highcharts.chart(elementId, {
        chart: {
            type: 'line'
        },
        title: {
            text: title
        },
        xAxis: {
            categories: timestamps.map(timestamp => new Date(timestamp).toLocaleTimeString()),
        },
        yAxis: {
            title: {
                text: yLabel
            }
        },
        series: rollingAverageSeries.map(s => ({
            name: s.name,
            data: s.data
        })),
        colors: Highcharts.defaultOptions.colors,
        backgroundColor: document.body.classList.contains('dark-mode') ? '#121212' : '#FFFFFF',
    });
}

function createHeatmap(elementId, title, timestamps, data, datatype, stops, minVal, maxVal, scaleType = 'linear') {
    Highcharts.chart(elementId, {
        chart: {
            type: 'heatmap',
            height: 150
        },
        legend: {
            enabled: false
        },
        title: {
            text: ""
        },
        xAxis: {
            categories: timestamps.map(timestamp => new Date(timestamp).toLocaleTimeString()),
            labels: {
                enabled: false
            }
        },
        yAxis: {
            categories: [''],
            labels: {
                formatter: function () {
                    if (this.value === '') {
                        return '<tspan class="hidden-label">Z.ZZZ</tspan>';
                    }
                    return this.value;
                }
            },
            title: {
                text: title,
            }
        },
        colorAxis: {
            min: minVal,
            max: maxVal,
            type: scaleType,
            stops: stops
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.series.yAxis.categories[this.point.y] + ' ' + this.series.xAxis.categories[this.point.x] + '</b><br>' +
                    'Value: <b>' + this.point.value + '</b>';
            }
        },
        series: [{
            name: datatype,
            borderWidth: 0,
            turboThreshold: 0,
            data: data.map((value, i) => [i, 0, value])
        }]
    });

    updateHiddenLabelColor();
}

function updateHiddenLabelColor() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    const hiddenLabels = document.querySelectorAll('.hidden-label');
    hiddenLabels.forEach(label => {
        label.style.fill = isDarkMode ? '#121212' : '#FFFFFF';
    });
}

function updateChartsTheme() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    const charts = Highcharts.charts;

    charts.forEach(chart => {
        if (chart) {
            chart.update({
                chart: {
                    backgroundColor: isDarkMode ? '#121212' : '#FFFFFF',
                    plotBorderColor: isDarkMode ? '#606063' : '#C0C0C0'
                },
                title: {
                    style: {
                        color: isDarkMode ? '#FFFFFF' : '#000000'
                    }
                },
                xAxis: {
                    labels: {
                        style: {
                            color: isDarkMode ? '#FFFFFF' : '#000000'
                        }
                    }
                },
                yAxis: {
                    labels: {
                        style: {
                            color: isDarkMode ? '#FFFFFF' : '#000000'
                        }
                    },
                    title: {
                        style: {
                            color: isDarkMode ? '#FFFFFF' : '#000000'
                        }
                    }
                },
                legend: {
                    itemStyle: {
                        color: isDarkMode ? '#FFFFFF' : '#000000'
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? '#333333' : '#FFFFFF',
                    style: {
                        color: isDarkMode ? '#FFFFFF' : '#000000'
                    }
                }
            });
        }
    });

    updateHiddenLabelColor();
}

document.getElementById('refreshButton').addEventListener('click', () => {
    fetch('trainingdata.csv')
        .then(response => response.text())
        .then(csv => {
            parseCSV(csv, createCharts);
        })
        .catch(error => console.error("Error loading CSV:", error));
});

function setPastHoursRange(hours) {
    const now = new Date();
    const end = new Date(now);
    const start = new Date(now.getTime() - hours * 60 * 60 * 1000);

    document.getElementById('startDate').value = formatDateForInput(start);
    document.getElementById('endDate').value = formatDateForInput(end);
    document.getElementById('refreshButton').click();
}

function shiftTimeRange(hours) {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    if (!startDateInput.value || !endDateInput.value) {
        alert('Please set both start and end dates first.');
        return;
    }

    const start = new Date(startDateInput.value);
    const end = new Date(endDateInput.value);
    const shiftMilliseconds = hours * 60 * 60 * 1000;

    start.setTime(start.getTime() + shiftMilliseconds);
    end.setTime(end.getTime() + shiftMilliseconds);

    startDateInput.value = formatDateForInput(start);
    endDateInput.value = formatDateForInput(end);
    document.getElementById('refreshButton').click();
}

function formatDateForInput(date) {
    return date.getFullYear().toString() + '-' +
           (date.getMonth() + 1).toString().padStart(2, '0') + '-' +
           date.getDate().toString().padStart(2, '0') + 'T' +
           date.getHours().toString().padStart(2, '0') + ':' +
           date.getMinutes().toString().padStart(2, '0');
}


document.getElementById('past6hButton').addEventListener('click', () => setPastHoursRange(6));
document.getElementById('past12hButton').addEventListener('click', () => setPastHoursRange(12));
document.getElementById('past24hButton').addEventListener('click', () => setPastHoursRange(24));

document.getElementById('moveLeft3Button').addEventListener('click', () => shiftTimeRange(-24));
document.getElementById('moveLeft2Button').addEventListener('click', () => shiftTimeRange(-12));
document.getElementById('moveLeft1Button').addEventListener('click', () => shiftTimeRange(-6));
document.getElementById('moveRight1Button').addEventListener('click', () => shiftTimeRange(6));
document.getElementById('moveRight2Button').addEventListener('click', () => shiftTimeRange(12));
document.getElementById('moveRight3Button').addEventListener('click', () => shiftTimeRange(24));

fetch('trainingdata.csv')
    .then(response => response.text())
    .then(csv => {
        parseCSV(csv, createCharts);
    })
    .catch(error => console.error("Error loading CSV:", error));

const toggleButton = document.getElementById('toggleDarkMode');
toggleButton.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    toggleButton.textContent = document.body.classList.contains('dark-mode') ? '🌞' : '🌙';
    updateChartsTheme();
});
