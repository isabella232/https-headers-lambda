'use strict';
exports.handler = (event, context, callback) => {
    const response = event.Records[0].cf.response;
    const headers = response.headers;

    headers['X-Content-Type-Options']    = "nosniff";
    headers['X-XSS-Protection']          = "1; mode=block";
    callback(null, response);
};
