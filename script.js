const fs = require('fs');
const axios = require('axios');
const csv = require('csv-parser');
const bip39 = require('bip39');
const { Ed25519Keypair, Transaction, Connection } = require('bigchaindb-driver');

// Function to generate a keypair using BIP39
const generateKeypair = () => {
    const seed = bip39.mnemonicToSeedSync(bip39.generateMnemonic());
    return new Ed25519Keypair(seed.slice(0, 32));
};

const keypair = generateKeypair();
const API_PATH = 'http://localhost:9984/api/v1/';
const conn = new Connection(API_PATH);

// Read CSV file and prepare data
const readCSVFile = (filePath) => {
    return new Promise((resolve, reject) => {
        const results = [];
        fs.createReadStream(filePath)
            .pipe(csv())
            .on('data', (data) => results.push(data))
            .on('end', () => {
                resolve(results);
            })
            .on('error', (error) => {
                reject(error);
            });
    });
};

// Create a BigchainDB transaction with the CSV data
const createTransaction = async (data) => {
    const assetData = {
        data: {
            type: 'financial_data',
            content: data
        }
    };

    const metadata = { date: new Date().toISOString() };

    // Construct a transaction payload
    const txCreate = Transaction.makeCreateTransaction(
        assetData,
        metadata,
        [Transaction.makeOutput(Transaction.makeEd25519Condition(keypair.publicKey))],
        keypair.publicKey
    );

    // Sign the transaction
    const signedTx = Transaction.signTransaction(txCreate, keypair.privateKey);

    // Post the transaction to BigchainDB
    try {
        const response = await conn.postTransactionCommit(signedTx);
        console.log('Transaction', response.id, 'successfully posted.');
        return response.id;
    } catch (error) {
        console.error('Error posting transaction:', error);
        throw error;
    }
};

// Retrieve a BigchainDB transaction by ID
const retrieveTransaction = async (transactionId) => {
    try {
        const response = await axios.get(`${API_PATH}transactions/${transactionId}`);
        return response.data;
    } catch (error) {
        console.error('Error retrieving transaction:', error);
        throw error;
    }
};

// Save retrieved data to a CSV file
const saveToCSV = (data, filePath) => {
    if (data && data.asset && data.asset.data && data.asset.data.data && data.asset.data.data.content) {
        const content = data.asset.data.data.content;
        if (content.length > 0) {
            const headers = Object.keys(content[0]).join(',') + '\n';
            const rows = content.map(row => Object.values(row).join(',')).join('\n');
            fs.writeFileSync(filePath, headers + rows);
            console.log(`Data saved to ${filePath}`);
        } else {
            console.error('Content array is empty.');
        }
    } else {
        console.error('Content array is missing or incorrectly structured.');
    }
};

// Main function to read CSV, send to BigchainDB, and retrieve it back
const main = async () => {
    const filePath = process.argv[2];
    try {
        const csvData = await readCSVFile(filePath);
        const transactionId = await createTransaction(csvData);
        const retrievedData = await retrieveTransaction(transactionId);
        console.log('Retrieved Data:', JSON.stringify(retrievedData, null, 2));  // Log the retrieved data for inspection
        saveToCSV(retrievedData, 'retrieved/retrieved_transactions.csv');
    } catch (error) {
        console.error('Error:', error);
    }
};

main();
