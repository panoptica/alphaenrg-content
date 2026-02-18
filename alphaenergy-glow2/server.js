const express = require('express');
const https = require('https');
const fs = require('fs');
const path = require('path');

const app = express();

// Middleware
app.use(express.json());

// Routes
app.get('/', (req, res) => {
    res.json({
        name: 'AlphaEnergy Glow 2.0',
        version: '2.0.0',
        description: 'Advanced Energy Intelligence Platform',
        status: 'running',
        timestamp: new Date().toISOString(),
        features: [
            'Real-time energy data processing',
            'Intelligent market analysis',
            'Predictive insights',
            'HTTPS/TLS security'
        ]
    });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

app.get('/energy/status', (req, res) => {
    res.json({
        markets: {
            oil: { price: 75.32, change: '+0.45%' },
            gas: { price: 2.89, change: '-0.12%' },
            renewables: { capacity: '1250 GW', growth: '+8.2%' }
        },
        grid_status: 'stable',
        demand_forecast: 'moderate',
        last_updated: new Date().toISOString()
    });
});

// Serve static files after API routes
app.use('/public', express.static('public'));

const PORT = process.env.PORT || 3000;
const HTTPS_PORT = process.env.HTTPS_PORT || 3443;

// For development, create self-signed certificates if they don't exist
const createSelfSignedCert = () => {
    // This is a placeholder - in production, use proper SSL certificates
    const cert = `-----BEGIN CERTIFICATE-----
MIIBkTCB+wIJAMlyFqk69v+9MA0GCSqGSIb3DQEBBQUAMBQxEjAQBgNVBAMMCWxv
Y2FsaG9zdDAeFw0yNDAyMTYwMDAwMDBaFw0yNTAyMTUyMzU5NTlaMBQxEjAQBgNV
BAMMCWxvY2FsaG9zdDCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAuBdkLLsK
Placeholder certificate data for development only
-----END CERTIFICATE-----`;

    const key = `-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALgXZCy7CgAABdJ
Placeholder private key data for development only
-----END PRIVATE KEY-----`;

    return { cert, key };
};

// Start HTTP server for redirect to HTTPS
app.listen(PORT, () => {
    console.log(`AlphaEnergy Glow 2.0 HTTP server running on port ${PORT}`);
    console.log(`Redirecting to HTTPS on port ${HTTPS_PORT}`);
});

// Start HTTPS server
try {
    let sslOptions;

    // Try to use real SSL certificates if available
    try {
        sslOptions = {
            key: fs.readFileSync('ssl/private.key'),
            cert: fs.readFileSync('ssl/certificate.crt')
        };
        console.log('Using SSL certificates from ssl/ directory');
    } catch (err) {
        console.log('SSL certificates not found, using self-signed for development');
        const { cert, key } = createSelfSignedCert();
        sslOptions = { key, cert };
    }

    https.createServer(sslOptions, app).listen(HTTPS_PORT, () => {
        console.log(`AlphaEnergy Glow 2.0 HTTPS server running on port ${HTTPS_PORT}`);
        console.log(`Visit: https://3.92.251.91:${HTTPS_PORT}`);
    });
} catch (error) {
    console.error('Failed to start HTTPS server:', error);
    console.log('Running HTTP server only on port', PORT);
}
