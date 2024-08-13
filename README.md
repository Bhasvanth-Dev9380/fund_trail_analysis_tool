

# 🚀 BigchainDB on Docker Desktop

## 🛠️ Setup Overview

1. **BigchainDB with Docker Desktop**: We run BigchainDB using a Docker Desktop image on a local machine to send and retrieve transactions efficiently.

   ![image](https://github.com/user-attachments/assets/b9a47ba2-4b03-483b-acfe-7ef8d16e2d30)

2. **Transaction Handling with `script.js`**: We use `script.js` to post and retrieve transactions. This script leverages Node.js, providing a streamlined method to interact with the BigchainDB API.

   ```bash
   node script.js
   ```

3. **Automation with Flask (`app.py`)**: The entire process is automated using `app.py`, which employs Flask to create a simple and effective web interface for transaction management. This allows users to interact with BigchainDB through a web application, making the process seamless and accessible.

## 🐳 BigchainDB and Docker Setup

### Step-by-Step Guide

1. **Install Docker Desktop**: Make sure Docker Desktop is installed and running on your local machine. If not, download and install it from [Docker's official site](https://www.docker.com/products/docker-desktop).

2. **Pull the BigchainDB Docker Image**: Use the following command to pull the BigchainDB image:

   ```bash
   docker pull bigchaindb/bigchaindb
   ```

3. **Run BigchainDB Container**: Once the image is pulled, run the container:

   ```bash
   docker run -d --name bigchaindb -p 9984:9984 -p 9985:9985 -p 27017:27017 bigchaindb/bigchaindb
   ```

   - `-d`: Runs the container in detached mode.
   - `--name`: Names the container `bigchaindb`.
   - `-p`: Maps the container ports to your local machine for access.

4. **Verify BigchainDB is Running**: Check if BigchainDB is running by accessing `http://localhost:9984/api/v1/`.

   You should see a JSON response indicating that the BigchainDB server is active.

## 📜 Transaction Management

### Using `script.js` for Transactions

- **Post Transactions**: You can post transactions to BigchainDB using `script.js`. This script handles the creation and posting of assets to the blockchain.

- **Retrieve Transactions**: Similarly, `script.js` can retrieve and verify transactions from the blockchain.

   ```javascript
   // Example snippet from script.js
   const BigchainDB = require('bigchaindb-driver');
   const conn = new BigchainDB.Connection('http://localhost:9984/api/v1/');

   // Post a transaction
   conn.postTransaction(transaction).then(...);

   // Retrieve a transaction
   conn.getTransaction(transactionId).then(...);
   ```

### Automate with Flask (`app.py`)

- **Flask Integration**: We use Flask in `app.py` to automate transaction handling. The Flask app provides endpoints that interact with the `script.js` functions, making it easier to perform blockchain operations via HTTP requests.

   ```python
   from flask import Flask, request, jsonify
   import script

   app = Flask(__name__)

   @app.route('/post', methods=['POST'])
   def post_transaction():
       data = request.json
       response = script.post_transaction(data)
       return jsonify(response)

   @app.route('/retrieve/<transaction_id>', methods=['GET'])
   def retrieve_transaction(transaction_id):
       response = script.retrieve_transaction(transaction_id)
       return jsonify(response)

   if __name__ == '__main__':
       app.run(debug=True)
   ```

- **Deployment**: To run the Flask application, use the following command:

   ```bash
   python app.py
   ```

   This starts the web server on `http://localhost:5000`, where you can access the endpoints for posting and retrieving transactions.

## 🔍 Additional Resources

- **BigchainDB Documentation**: [BigchainDB Documentation](https://docs.bigchaindb.com/projects/server/en/latest/)
- **Docker Documentation**: [Docker Desktop Documentation](https://docs.docker.com/desktop/)
- **Flask Documentation**: [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)

## 🏆 Key Features

- **Decentralized**: BigchainDB provides a decentralized database with blockchain characteristics.
- **Flexible Querying**: You can perform complex queries on the data stored in BigchainDB.
- **Automated**: With Flask, the transaction process is automated, reducing manual overhead.
- **Dockerized**: Easy setup and deployment using Docker, making it accessible across different environments.

