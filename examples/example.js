var http = require('http');

const options = {
    host: 'http://163.117.129.205',
    port: '80',
    path: 'api/lemmas/programar',
    method: 'GET'
}

http.get(options, (resp) => {
    let body = '';
    resp.on('data', (d) => {
        body += d;
    });
    resp.on('end', () => {
        let parsed = JSON.stringify(body);
        console.log(parsed)
    })
})