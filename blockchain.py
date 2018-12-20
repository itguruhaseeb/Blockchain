#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 23:08:51 2018

@author: haseeb
"""

#To be installed
#Flask==0.12.2: pip install Flask==0.12.2
#Postman HTTP Client: https://www.getpostman.com

#Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.createBlock(nonce = 1, previousHash = '0')
        
    def createBlock(self, nonce, previousHash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': nonce,
                 'previousHash': previousHash}
        self.chain.append(block)
        return block
    
    def getPreviousBlock(self):
        return self.chain[-1]
    
    def proofOfWork(self, previousNonce):
        newNonce = 1
        checkProof = False
        while checkProof is False:
            #Miners will have to solve the problem below
            hashOperation = hashlib.sha256(str(newNonce**2 - previousNonce**2).encode()).hexdigest()
            if hashOperation[:6] == '000000':
                checkProof = True
            else:
                newNonce += 1
        return newNonce
    
    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()
    
    def isChainValid(self, chain):
        previousBlock = chain[0]
        blockIndex = 1
        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['previousHash'] != self.hash(previousBlock):
                return False
            previousNonce = previousBlock['nonce']
            nonce = block['nonce']
            hashOperation = hashlib.sha256(str(nonce**2 - previousNonce**2).encode()).hexdigest()
            if hashOperation[:6] != '000000':
                return False
            previousBlock = block
            blockIndex += 1
        return True      

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

#Creating a Blockchain
blockchain = Blockchain()

#Mining a new block
@app.route('/mineblock', methods=['GET'])
def mineBlock():
    previousBlock = blockchain.getPreviousBlock()
    previousNonce = previousBlock['nonce']
    nonce = blockchain.proofOfWork(previousNonce)
    previousHash = blockchain.hash(previousBlock)
    block = blockchain.createBlock(nonce, previousHash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'previousHash': block['previousHash']}
    return jsonify(response), 200

#Getting the full Blockchain
@app.route('/getchain', methods = ['GET'])
def getChain():
    response = {'chain': blockchain.chain,
                'totalCount':len(blockchain.chain)}
    return jsonify(response), 200

#Checking if the Blockchain is valid
@app.route('/isvalidchain', methods = ['GET'])
def isValidChain():
    isValid = blockchain.isChainValid(blockchain.chain)
    if isValid:
        response = {'message':'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The Blockchain is not valid'}
    return jsonify(response), 200

#Running the app
app.run(host='blockchain.haseebafsar.com', port = 5000)    
