# GHG_EDL

## Introduction

GHG_EDL is a prototype an information system that would provide more consistent, accurate and transparent information about GHG emissions. 

This repository supports a chapter in *Contemporary Issues in Sustainable Finance* from the Palgrave Collection.

The chapter is:
GHG Encrypted Distributed Ledger: A system design that enhances the reporting and assurance of greenhouse gas emissions using a blockchain and privacy preserving cryptography. by  [John McCallig](https://people.ucd.ie/john.mccallig)

The link to this chapter will be added as soon as it is available.

Each producer loads information on the Scope 1 & 2 GHG emissions of their product(s)/services(s) into a smart contract (ProductGHGFootPrint) on an ethereum blockchain. Scope 3 emissions can be loaded directly or linked using a transaction on the blockchain to the smart contracts of the products and services necessary for the production of the main product. The emissions data are encrypted using commitments. The random number from these commitments must be communicated over a private secure channel between the supplier and the producer. The producer can then calculate a commitment for the total GHG emissions from their product. They publish the commitment value, the random number used for the commitment and the unencrypted total GHG emissions number. Users of the smart contract can then verify that the individual commitments sum up to the total commitment and that this total commitment can be unlocked using the random number supplied.

You can run the software as follows:

## Prerequisites

You must install https://www.docker.com on your system. This software allows GHG_EDL to run in a virtual machine on your system. This means GHG_EDL runs in its own container and does not affect the files on your system.

You may also need [git](https://git-scm.com/downloads) or [GitHub Desktop](https://desktop.github.com/download/) if it is not already installed.

## Installation

Clone the repository to a local directory.
```
% git clone https://github.com/johnmccallig/GHG_EDL 
```

Install [docker](https://www.docker.com/) and docker-compose.

In a terminal, make sure you are in the cloned directory. Issue the following command

```
% docker compose up -d
```

When the application has terminated (type exit into the command line) you may need to press ctrl-c or issue the following command in another terminal

```
% docker compose down
```

## Running GHG_EDL

### Start docker compose

In the cloned directory
```
% docker compose up -d
```
or 
```
% docker-compose up --build
```
if the container needs to be rebuilt

then 
```
% docker compose exec sandbox bash
```
This command starts the GHG_EDL container and a command line. This command may have to be run in another terminal if the docker compose lines were run in the foreground.

You now be in the command line of the container with a unix virtual machine, the software, and all necessary packages. The software uses brownie as an interface to a test etherium blockchain. See https://eth-brownie.readthedocs.io/en/stable/quickstart.html for more information.

### To run GHG_EDL

```
% cd myprojects/GHG_EDL
% brownie run scripts/deploy.py
```

These commands must be run inside the docker container - see above.

Brownie should start an etherium blockchain and execute the code in scripts/deploy.py which 

- Reads in sample GHG data from footprint.py
- Deploys a smart contract (ProductGHGFootPrint) for each product
- Encrypts the sample data using Pedersen commitments
- Posts the sample data to the smart contracts on the ethereum blockchain
- Post the links between the smart contracts for Scope 3 emissions
- Calculates the total emissions for each product and posts that data unencrypted and in the form of a Pedersen commitment.
- Downloads the encrypted data and verifies that the sum of the commitments for the producers own emissions and the linked scope 3 emissions is equal to the total GHG emissions commitment   

# Making Changes

If you make any changes to the smart contract (contracts/ProductGHGFootPrint.sol) or the deployment script (scripts/deploy.py)

Then you must recompile the project

```
% brownie compile
```
in the GHG_EDL directory.

