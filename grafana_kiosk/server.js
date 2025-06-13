const express = require('express');
const app = express();
const PORT = 3001;


const GRAFANA_URL = 'http://localhost:3000';

app.get('/', (req, res) => {
    const dashboardUrl = `${GRAFANA_URL}/?kiosk`;
    res.send(generateKioskPage(dashboardUrl));
});

function generateKioskPage(dashboardUrl) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grafana Kiosk</title>
        <style>
            body, html { margin: 0; padding: 0; overflow: hidden; }
            iframe { border: none; width: 100vw; height: 100vh; }
        </style>
    </head>
    <body>
        <iframe src="${dashboardUrl}" id="grafana-iframe"></iframe>

    </body>
    </html>
    `;
}

app.listen(PORT, () => {
    console.log(`Servidor proxy corriendo en http://localhost:${PORT}`);
});