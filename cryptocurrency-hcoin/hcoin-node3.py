#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 19:05:46 2019

@author: haseeb
"""

#Creating a cryptocurrency on top of blockchain called "hcoin"

#To be installed
#Flask==0.12.2: pip install Flask==0.12.2
#Postman HTTP Client: https://www.getpostman.com
#requests==2.18.4: pip install requests==2.18.4

#Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        
        #The transaction is required to transform a regular blockchain into a cryptocurrency
        self.transactions = []
        self.createBlock(nonce = 1, previousHash = '0')
        
        #The nodes transform a blockchain into a decentralized blockchain
        #Be it a cryptocurrency, a smart contract etc.
        self.nodes = set()
        
    def createBlock(self, nonce, previousHash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': nonce,
                 'previousHash': previousHash,
                 'transactions': self.transactions}
        self.transactions = []
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

    def addTransaction(self, sender, reciever, amount):
        self.transactions.append({'sender': sender, 
                                  'reciever': reciever, 
                                  'amount': amount})
        #Finally return the index of block to which this transaction will be added
        previousBlock = self.getPreviousBlock()
        
        #this means we return the last block of the chain
        #which the miners will use it to add to the chain their newly mined block
        return previousBlock['index'] + 1 
    
    def addNode(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add( parsedUrl.netloc )
    
    #This is where the consensus protocol over decentralized blockchain is taken care of    
    def replaceChain(self):
        network = self.nodes
        longestChain = None
        maxLength    = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://{node}/getchain')
            if response.status_code == 200:
                length = response.json()['totalCount']
                chain  = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an unique address for the distibuted node
nodeAddress = str(uuid4()).replace('-', '')

#Creating a Blockchain
blockchain = Blockchain()

#Mining a new block
@app.route('/mineblock', methods=['POST'])
def mineBlock():
    previousBlock = blockchain.getPreviousBlock()
    previousNonce = previousBlock['nonce']
    nonce = blockchain.proofOfWork(previousNonce)
    previousHash = blockchain.hash(previousBlock)
    #Whenever a miner mines a block he gets a hcoin. Here the miner is hardcoded
    #as myself 'Haseeb' this could be replaced with a miner name, id etc from the miner db
    blockchain.addTransaction( nodeAddress, 'Anna', 1 )
    block = blockchain.createBlock(nonce, previousHash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'previousHash': block['previousHash'],
                'transactions': block['transactions']}
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

#Adding a new transaction to the Blockchain
@app.route('/addtransaction', methods = ['POST'])
def addTransaction():
    json = request.get_json()
    transactionKeys = ['sender', 'reciever', 'amount']
    if not all(key in json for key in transactionKeys):
        return "The transaction request has missing transaction keys", 400
    index = blockchain.addTransaction(json['sender'], json['reciever'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain
    
# Connecting new nodes
@app.route('/connectnode', methods = ['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "Node list is empty", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {'message': 'The new nodes are added to the network',
                'totalNodes': list(blockchain.nodes)}
    return jsonify(response), 201

#Replacing the chain by the longest chain if needed
@app.route('/replacechain', methods = ['GET'])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {'message':'The chain was replaced by the longest chain',
                    'newChain': blockchain.chain}
    else:
        response = {'message': 'The blockchain is in sync. No need to replace the chain as it is the largest chain',
                    'actualChain': blockchain.chain}
    return jsonify(response), 200   
        
#Running the app
app.run(host='blockchain.haseebafsar.com', port = 5003)    