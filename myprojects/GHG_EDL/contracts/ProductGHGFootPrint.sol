// SPDX-License-Identifier: MIT1

// Solidity Contract to accumulate Greenhouse Gas (GHG) Emissions
// on an ethereum blockchain.

// The contract is set up by an entity that produces a product or service
// Data about the product or service is loaded onto the blockchain by the owner.
// Indirect emissions are managed by either linking to the smart contact provided by the supplier
// or by uploading the data directly to the blockchain.

// Data in the smart contracts is encrypted using Pedersen Commitments (off-chain)
// The Commitments can be accumulated to give the total GHG emissions for the product or service.
// The random numbers used to generate the Pedersen Commitments are stored off-chain and communicated between
// the supplier and the owner of the smart contract.
// The entity (owner of the smart contract) can then provide a proof of the total GHG emissions using the
// random numbers used to generate the Pedersen Commitments.

// John McCallig, Dec. 2024
// Licensed under MIT License

//contract definition

pragma solidity ^0.8.0;

contract ProductGHGFootPrint {
    //structures definitions

    struct commitment {
        uint256 commitment_x;
        bool commitment_y_odd;
        uint256 r;
        uint256 r_overflow;
    }

    // Data structure to store the description of the product or service
    struct description_struct {
        address owner;
        string owner_name;
        string productID;
        string product_name;
        string product_type;
        string units; // e.g. unit, kg, tonne, etc.
        string date_created;
        string date_updated;
        string status; // Active or Inactive
        address ancestor; // address of older version of the product GHG data
        address descendant; // address of newer version of the product GHG data
        uint32 total_GHGFootPrint; // total unencrypted GHG emissions for the product or service
        commitment total_GHGFootPrint_commitment; // total encrypted GHG emissions for the product or service
    }

    // Data structure to store the GHG Footprint of the product or service
    // Each reporting line item is stored as a GHG Footprint (e.g. 'Gross Scope 1 greenhouse gas emissions')
    // Each GHG Footprint is identified by a unique ID
    // GHG data from the supplier can be linked to the suppliers smart contract using
    // the contract address and the GHG Footprint ID
    // The GHG Footprint is stored as a Pedersen Commitment

    struct GHGFootPrint_struct {
        uint16 GHGFootPrint_ID; // unique ID for the GHG Footprint in this smart contract
        uint16 GHGFootPrint_scope;
        uint8 GHGFootPrint_disaggregation; // 0 = no disaggregation, 1+ = specific disaggregation
        string GHGFootPrint_category; // description of category (e.g. )
        // Data given where data is stored in the suppliers contract
        address GHGFootPrint_contract; // Address of the suppliers contract
        uint16[] contract_GHGFootPrint_IDs; // array of GHG Footprint IDs in the suppliers contract
        // that should be included in this contract. 0 for no contract GHGFootPrint IDs
        bytes GHGFootPrint_signature; // signature of assurer of the GHG Footprint
        uint16 GHGFootPrint_no_units; // number of units used in the product 0 for no units
        // Data given for all GHG Footprints
        commitment GHGFootPrint_commitment;
    }

    // Constructor function
    // The owner of the smart contract is set to the address of the sender
    // The description of the product or service is initialized and total GHG emissions are set to 0

    constructor() {
        owner = msg.sender;
        description.owner = owner; // owner of the smart contract i.e. entity that produces the product or service
        // initialize the description
        description.total_GHGFootPrint = 0;
        description.total_GHGFootPrint_commitment.commitment_x = 0;
        description.total_GHGFootPrint_commitment.commitment_y_odd = false;
        description.total_GHGFootPrint_commitment.r = 0;
        description.total_GHGFootPrint_commitment.r_overflow = 0;
    }

    // State variables - stored in the smart contract

    description_struct private description; // description of the product or service
    GHGFootPrint_struct[] private GHGFootPrints; // array of GHG Footprints
    address public owner; // owner of the smart contract which is public

    //functions

    // Function that the owner can use to set the description of the product or service

    function set_description(
        string memory _owner_name,
        string memory _productID,
        string memory _product_name,
        string memory _product_type,
        string memory _units,
        string memory _date_created,
        string memory _date_updated,
        string memory _status,
        address _ancestor,
        address _descendant
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can set the description");
        description.owner_name = _owner_name;
        description.productID = _productID;
        description.product_name = _product_name;
        description.product_type = _product_type;
        description.units = _units;
        description.date_created = _date_created;
        description.date_updated = _date_updated;
        description.status = _status;
        description.ancestor = _ancestor;
        description.descendant = _descendant;
        return true;
    }

    // Function to get the description of the product or service - anybody can use this function

    function get_description()
        public
        view
        returns (
            address, // owner
            string memory, // owner_name
            string memory, // productID
            string memory, // product_name
            string memory, // product_type
            string memory, // units
            string memory, // date_created
            string memory, // date_updated
            string memory, // status
            address, // ancestor
            address // descendant
        )
    {
        return (
            description.owner,
            description.owner_name,
            description.productID,
            description.product_name,
            description.product_type,
            description.units,
            description.date_created,
            description.date_updated,
            description.status,
            description.ancestor,
            description.descendant
        );
    }

    // Function to set the total GHG emissions for the product or service
    // In this case we also provide r - the blinding factor to unlock the commitment

    function set_total_ghg(
        uint32 _total_GHGFootPrint,
        uint256 _total_GHGFootPrint_commitment_x,
        bool _total_GHGFootPrint_commitment_y_odd,
        uint256 _total_GHGFootPrint_r,
        uint256 _total_GHGFootPrint_r_overflow
    ) public returns (bool) {
        require(
            msg.sender == owner,
            "Only the owner can set the total GHG footprint"
        );
        description.total_GHGFootPrint = _total_GHGFootPrint;
        description
            .total_GHGFootPrint_commitment
            .commitment_x = _total_GHGFootPrint_commitment_x;
        description
            .total_GHGFootPrint_commitment
            .commitment_y_odd = _total_GHGFootPrint_commitment_y_odd;
        description.total_GHGFootPrint_commitment.r = _total_GHGFootPrint_r;
        description
            .total_GHGFootPrint_commitment
            .r_overflow = _total_GHGFootPrint_r_overflow;

        return true;
    }

    // Function to get the total GHG emissions for the product or service
    // Anybody can use this function

    function get_total_ghg()
        public
        view
        returns (uint32, uint256, bool, uint256, uint256)
    {
        return (
            description.total_GHGFootPrint,
            description.total_GHGFootPrint_commitment.commitment_x,
            description.total_GHGFootPrint_commitment.commitment_y_odd,
            description.total_GHGFootPrint_commitment.r,
            description.total_GHGFootPrint_commitment.r_overflow
        );
    }

    // Function to set the GHG Footprints for the product or service
    // Individual line items are stored as GHG Footprints

    function set_ghgfootprint(
        uint16 _GHGFootPrint_ID,
        uint16 _GHGFootPrint_scope,
        uint8 _GHGFootPrint_disaggregation,
        string memory _GHGFootPrint_category,
        address _GHGFootPrint_contract,
        uint16[] memory _contract_GHGFootPrint_IDs,
        bytes memory _GHGFootPrint_signature,
        uint16 _GHGFootPrint_no_units,
        uint256 _GHGFootPrint_commitment,
        bool _GHGFootPrint_commitment_y_odd
    ) public returns (bool) {
        require(msg.sender == owner, "Only the owner can add GHG Footprints");
        require(
            _GHGFootPrint_scope == 1 ||
                _GHGFootPrint_scope == 2 ||
                _GHGFootPrint_scope == 3,
            "Scope must be 1, 2 or 3"
        );
        // Check if the GHG Footprint ID already exists
        for (uint i = 0; i < GHGFootPrints.length; i++) {
            require(
                GHGFootPrints[i].GHGFootPrint_ID != _GHGFootPrint_ID,
                "GHG Footprint ID already exists"
            );
        }
        // Add GHG Footprint to the array
        GHGFootPrints.push(
            GHGFootPrint_struct({
                GHGFootPrint_ID: _GHGFootPrint_ID,
                GHGFootPrint_scope: _GHGFootPrint_scope,
                GHGFootPrint_disaggregation: _GHGFootPrint_disaggregation,
                GHGFootPrint_category: _GHGFootPrint_category,
                GHGFootPrint_contract: _GHGFootPrint_contract,
                contract_GHGFootPrint_IDs: _contract_GHGFootPrint_IDs,
                GHGFootPrint_signature: _GHGFootPrint_signature,
                GHGFootPrint_no_units: _GHGFootPrint_no_units,
                GHGFootPrint_commitment: commitment({
                    commitment_x: _GHGFootPrint_commitment,
                    commitment_y_odd: _GHGFootPrint_commitment_y_odd,
                    r: 0,
                    r_overflow: 0
                })
            })
        );
        return true;
    }

    // Function to get all the GHG Footprints for the product or service
    // using the GHG Footprint ID
    // Anybody can use this function

    function get_ghgfootprints()
        public
        view
        returns (GHGFootPrint_struct[] memory)
    {
        return GHGFootPrints;
    }
}
