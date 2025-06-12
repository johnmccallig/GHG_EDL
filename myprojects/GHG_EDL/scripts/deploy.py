#!/usr/bin/python3

from brownie.network.contract import ProjectContract  # type: ignore
from brownie import accounts, ProductGHGFootPrint  # type: ignore

import sys

# add scripts dir to path to allow footprint.py to be imported
sys.path.append("/code/myprojects/GHG_EDL/scripts")

from footprint import data  # import data from footprint.py stored in a data dictionary
import tinyec.ec as tiny
import secrets
import random
import json
import pprint
from nummaster.basic import sqrtmod
from operator import add
import pandas as pd

random.seed(
    1234567890
)  # set seed for reproducibility - randomness is not secure - use secrets library for better randomness

# Utility functions to split a 64 bit number into 2 32 bit numbers
# and reassemble 2 32 bit numbers into a 64 bit number
# for storage in a uint256 on the blockchain


def split_64bit_number(number):
    return number >> 32, number & 0xFFFFFFFF


def reassamble_64bit_number(number1, number2):
    return number1 << 32 | number2


# Utility functions to compress and decompress points on
# an Elliptic curve
# from https://cryptobook.nakov.com/asymmetric-key-ciphers/elliptic-curve-cryptography-ecc


def uncompress_point(compressed_point, p, a, b):
    """
    Uncompresses an elliptic curve point from its compressed form.
    Args:
        compressed_point (tuple): A tuple (x, is_odd) where x is the x-coordinate of the point
                                  and is_odd is a boolean indicating if the y-coordinate is odd.
        p (int): The prime modulus of the finite field.
        a (int): The coefficient 'a' in the elliptic curve equation y^2 = x^3 + ax + b.
        b (int): The coefficient 'b' in the elliptic curve equation y^2 = x^3 + ax + b.
    Returns:
        tuple: The uncompressed point (x, y) on the elliptic curve.
    """

    x, is_odd = compressed_point
    y = sqrtmod(pow(x, 3, p) + a * x + b, p)
    if bool(is_odd) == bool(y & 1):
        return (x, y)
    return (x, p - y)


class Ped_scheme:
    # Class level variables
    # Parameters of the elliptic curve

    # Domain parameters for the `secp256k1` curve
    # (as defined in http://www.secg.org/sec2-v2.pdf)
    name = "secp256k1"
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    a = 0x0000000000000000000000000000000000000000000000000000000000000000
    b = 0x0000000000000000000000000000000000000000000000000000000000000007
    g = (
        0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    )
    h = 1
    curve = tiny.Curve(a, b, tiny.SubGroup(p, g, n, h), name)

    # Utility functions to compress and decompress points on an Elliptic curve

    def compress_point(self, point):
        """Compresses a point on an Elliptic Curve. Returns x value and boolean

        Args:
            point (tinyec point): tinyec point e.g. curve.g.x

        Returns:
            tuple: (x value of point, boolean)
        """
        return (point.x, point.y % 2)

    def uncompress_point_to_tinyec(self, compressed_point):
        """Uncompress a point on an Elliptic Curve.

        Args:
            point (compressed point): x value of point and boolean

        Returns:
            tinyec point: point on elliptic curve
        """
        x, is_odd = compressed_point
        y = sqrtmod(
            pow(x, 3, Ped_scheme.p) + Ped_scheme.a * x + Ped_scheme.b, Ped_scheme.p
        )
        if bool(is_odd) == bool(y & 1):
            return tiny.Point(Ped_scheme.curve, x, y)
        return tiny.Point(Ped_scheme.curve, x, Ped_scheme.p - y)

    # Value of H_x is SHA256 of G.x in Bitcoin
    # https://github.com/AdamISZ/ConfidentialTransactionsDoc/blob/master/essayonCT.pdf
    # Page 6

    H_x = 36444060476547731421425013472121489344383018981262552973668657287772036414144
    H_y = uncompress_point((H_x, False), p, a, b)[1]
    H = tiny.Point(curve, H_x, H_y)

    def commit(self, v):
        """Generate Pedersen Commitment

        Args:
            v (integer): value to be committed to

        Returns:
            tinyec point: point on elliptic curve
            r (integer): random number below order (p) of elliptic curve
        """
        # r = secrets.randbelow(Ped_scheme.curve.field.p) # use secrets library for better randomness
        r = random.randint(1, Ped_scheme.curve.field.p)
        return (v * Ped_scheme.curve.g + r * Ped_scheme.H, r)

    def verify(self, c, v, r):
        """Verify Pedersen Commitment

        Args:
            c (tinyec point on elliptic curve): pedersen commitment
            v (integer): value that was committed
            r (integer): random number used for the commitment

        Returns:
            True/False : Commitment is verified
        """
        return c == v * Ped_scheme.curve.g + r * Ped_scheme.H


def deploy_ProductGHGFootPrint():
    """
    Deploys the ProductGHGFootPrint contract for each company and its products.

    This function performs the following steps:
    1. Creates accounts for each company.
    2. Deploys the ProductGHGFootPrint contract for each product of the company.
    3. Stores the deployed contract address in the data structure.

    The function assumes that `data` is a dictionary where each key is a company name
    and the value is another dictionary containing product information. Each product
    dictionary should have a key that includes the word "Product".

    The function also assumes that `accounts` and `ProductGHGFootPrint` are predefined
    objects available in the scope.

    Example structure of `data`:
    data = {
        "CompanyA": {
            "Product1": {},
            "Product2": {},
            ...
        },
        "CompanyB": {
            "Product1": {},
            ...
        },
        ...
    }

    Prints the account information for each company and the contract address for each product.

    Raises:
        Any exceptions raised by the `accounts.add()` or `ProductGHGFootPrint.deploy()` methods.
    """
    # create accounts for each company
    # and deploy the ProductGHGFootPrint contract
    for company in data:
        account = accounts.add()
        print(f"Account for ", company, "is: ", account)
        data[company]["account"] = account
        # deploy the ProductGHGFootPrint contract
        for product in data[company]:
            if "Product" in product:
                data[company][product]["productghgfootprint"] = (
                    ProductGHGFootPrint.deploy({"from": data[company]["account"]})
                )
                print(
                    f"Contract address for ",
                    company,
                    product,
                    "is: ",
                    data[company][product]["productghgfootprint"].address,
                )


# set the description for each product and company
def set_description():
    for company in data:
        print(f"Company description for: ", company, "transaction")
        print(f"Company", company, "address", data[company]["account"])

        for product in data[company]:
            if "Product" in product:
                print(f"Product description for: ", product, "transaction")
                print(
                    f"Company",
                    company,
                    "owner name",
                    data[company][product]["description"]["owner_name"],
                )

                transaction = data[company][product][
                    "productghgfootprint"
                ].set_description(
                    data[company][product]["description"]["owner_name"],  # owner
                    data[company][product]["description"]["productID"],  # productID
                    data[company][product]["description"][
                        "product_name"
                    ],  # product_name
                    data[company][product]["description"][
                        "product_type"
                    ],  # product_type
                    data[company][product]["description"]["units"],  # units
                    data[company][product]["description"][
                        "date_created"
                    ],  # date_created
                    data[company][product]["description"][
                        "date_updated"
                    ],  # date_updated
                    data[company][product]["description"]["status"],  # status
                    "0x0000000000000000000000000000000000000000",  # ancestor contract
                    "0x0000000000000000000000000000000000000000",  # descendant contract
                    {"from": data[company]["account"]},
                )
                transaction.wait(1)


def create_commitments(p):
    """
    Creates cryptographic commitments for GHG (Greenhouse Gas) footprint values for each product of each company in the data.

    Args:
        p: An object that provides methods for creating and verifying cryptographic commitments.

    The function iterates through the data structure, which is expected to be a nested dictionary with companies as keys,
    products as nested keys, and GHG footprint values as nested dictionaries. For each GHG footprint value, it creates a
    cryptographic commitment and stores the commitment and its associated randomness in the data structure. It also verifies
    the commitment to ensure its correctness.

    The data structure is expected to have the following format:
    {
        "company1": {
            "Product1": {
                "GHG_Footprints": [
                    {
                        "GHGFootprint_value": <value>,
                        "GHGFootPrint_commitment": <commitment>,
                        "GHGFootPrint_commitment_r": <randomness>
                    },
                    ...
                ]
            },
            ...
        },
        ...
    }

    If a GHG footprint value is not present, the function sets the commitment and randomness to (0, 0).

    Raises:
        AssertionError: If the commitment verification fails.
    """
    for company in data:
        for product in data[company]:
            if "Product" in product:
                for footprint in data[company][product]["GHG_Footprints"]:
                    if "GHGFootprint_value" in footprint:
                        commitment = p.commit(int(footprint["GHGFootprint_value"]))
                        footprint["GHGFootPrint_commitment"] = p.compress_point(
                            commitment[0]
                        )
                        footprint["GHGFootPrint_commitment_r"] = commitment[1]

                        assert (
                            p.verify(
                                commitment[0],
                                int(footprint["GHGFootprint_value"]),
                                commitment[1],
                            )
                            == True,
                            "Commitment failed",
                        )
                    else:
                        footprint["GHGFootPrint_commitment"] = (
                            0,
                            0,
                        )
                        footprint["GHGFootPrint_commitment_r"] = 0
    # write data to file for debugging
    # pprint.pprint(str(data))


def upload_footprints():
    """
    Uploads GHG footprints for each product of each company in the data.

    Iterates through the data structure containing companies and their products,
    and posts a blockchain transaction to set the GHG footprint for each product.

    For each footprint:
    - If the footprint is linked, finds the linked contract and sets it.
    - If the footprint is not linked, sets the linked contract to a default value.

    Posts a blockchain transaction to set the GHG footprint for each product with the following details:
    - GHGFootPrint_ID
    - Scope
    - Disaggregation
    - Category
    - Linked contract
    - Linked GHG footprint IDs
    - Signature (defaulted to 0)
    - Units
    - GHG footprint commitment

    Waits for the transaction to be confirmed before proceeding to the next footprint.

    Prints the transaction details for each footprint.

    Note: Assumes `data` is a predefined global variable containing the necessary information.
    """
    for company in data:
        for product in data[company]:
            if "Product" in product:
                print(f"Iterating ", data[company][product])
                for footprint in data[company][product]["GHG_Footprints"]:
                    print(
                        f"Posting transaction for ",
                        data[company][product]["description"]["owner_name"],
                        " Footprint:",
                        footprint["GHGFootPrint_ID"],
                    )

                    # set contract link data for linked footprints
                    if (
                        "GHGFootprint_linked_product" in footprint
                    ):  # check if the footprint is linked
                        linked_contract = find_linked_contract(
                            footprint["GHGFootprint_supplier"],
                            footprint["GHGFootprint_linked_product"],
                        )
                        print("Linked contract is: ", linked_contract)
                        footprint["GHGFootprint_linked_contract"] = linked_contract
                    else:
                        # set contract link data for non-linked footprints to 0
                        footprint["GHGFootprint_linked_contract"] = (
                            "0x0000000000000000000000000000000000000000"
                        )
                        footprint["GHGFootprint_no_units"] = 0
                        footprint["GHGFootprint_IDs"] = []

                    # post Blockchain tx to set GHG footprint for each product
                    transaction1 = data[company][product][
                        "productghgfootprint"
                    ].set_ghgfootprint(
                        footprint["GHGFootPrint_ID"],  # GHGFootPrint_ID
                        footprint["GHGFootPrint_scope"],  # Scope
                        footprint["GHGFootPrint_disaggregation"],  # disaggregation
                        footprint["GHGFootPrint_category"],  # Category
                        footprint["GHGFootprint_linked_contract"],  # linked contract
                        footprint["GHGFootprint_IDs"],  # linked GHG FP IDs
                        0,  # signature
                        footprint["GHGFootprint_no_units"],  # units
                        footprint["GHGFootPrint_commitment"][
                            0
                        ],  # GHG footprint commitment
                        footprint["GHGFootPrint_commitment"][1],  # commitment y
                        {"from": data[company]["account"]},
                    )
                    transaction1.wait(1)
                    print("GHG Setting is:", transaction1)


def find_linked_contract(supplier, product):
    """
    Finds the linked contract address for a given supplier and product.

    Args:
        supplier (str): The name of the supplier.
        product (str): The name of the product.

    Returns:
        address: The contract address of the product's GHG footprint if found.

    Raises:
        ValueError: If the supplier or product is not found in the data.
    """
    if supplier in data and product in data[supplier]:
        product_contract = data[supplier][product]["productghgfootprint"].address
        return product_contract
    else:
        ValueError("Supplier or product not found")


def find_linked_supplier(supplier, product):
    """
    Find the linked supplier for a given product.

    Args:
        supplier (str): The name of the supplier.
        product (str): The name of the product.

    Returns:
        dict: The product dictionary for the supplier and product.

    Raises:
        ValueError: If the supplier or product is not found in the data.
    """
    if supplier in data and product in data[supplier]:
        product_supplier = data[supplier][product]
        return product_supplier
    else:
        ValueError("Supplier or product not found")


def get_footprints(contract_address):
    footprints = []
    footprints = contract_address.get_ghgfootprints()
    print(list(footprints))


def sum_up_footprints(p, footprints, ids=[], scope=0):
    """
    Sums up the greenhouse gas (GHG) footprints and commitments for a given set of footprints.

    Args:
        p: An object that provides the method `uncompress_point_to_tinyec` to uncompress commitments.
        footprints (list): A list of footprint dictionaries, each containing GHG footprint data.
        ids (list, optional): A list of footprint IDs to filter the footprints. Defaults to an empty list.
                              This paramter is used for linked footprints.
        scope (int, optional): The scope level to consider for summing up footprints. Defaults to 0.
                               This parameter is used for linked footprints so that the linked footprints
                               go into the parent company's scope.

    Returns:
        list: A list of totals for each scope, including values, commitments, and commitments r.
              The list is structured as follows:
              - totals[0:3]: Values for each scope.
              - totals[3:6]: Accumulated commitments for each scope.
              - totals[6:]: Accumulated commitments r for each scope.
    """

    totals = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]  # totals for each scope for values [0:3], commitments [3:6] and commitments r [6:]
    # total commitment - zeros will be replaced by accumulated commitments

    for footprint in footprints:
        # print("Footprint is: ", footprint)
        if "GHGFootprint_linked_product" in footprint:
            linked_supplier = find_linked_supplier(
                footprint["GHGFootprint_supplier"],
                footprint["GHGFootprint_linked_product"],
            )
            linked_footprints = linked_supplier["GHG_Footprints"]
            # no of units
            company_commitments_tree.append(
                "Found Supplier" + str(footprint["GHGFootprint_supplier"])
            )

            sum_up = sum_up_footprints(
                p,
                linked_footprints,
                footprint["GHGFootprint_IDs"],
                footprint["GHGFootPrint_scope"],
            )
            company_commitments_tree.append("Supplier sum of c" + str(sum_up[3:6]))
            totals[0:3] = list(map(add, totals[0:3], sum_up[0:3]))
            totals[3:6] = list(map(accumulate_commitments, totals[3:6], sum_up[3:6]))
            totals[6:] = list(map(add, totals[6:], sum_up[6:]))
        else:
            if footprint["GHGFootPrint_ID"] in ids:
                totals[scope - 1] += footprint["GHGFootprint_value"]
                totals[scope - 1 + 6] += footprint[
                    "GHGFootPrint_commitment_r"
                ]  # place rs in totals[6:]
                # uncompress the commitment
                unc_c = p.uncompress_point_to_tinyec(
                    footprint["GHGFootPrint_commitment"]
                )
                totals[scope - 1 + 3] = accumulate_commitments(
                    totals[scope - 1 + 3], unc_c
                )
                company_commitments_tree.append(
                    " fp_id:" + str(footprint["GHGFootPrint_ID"])
                )
                company_commitments_tree.append(unc_c)
            if len(ids) == 0:
                totals[footprint["GHGFootPrint_scope"] - 1] += footprint[
                    "GHGFootprint_value"
                ]
                totals[footprint["GHGFootPrint_scope"] - 1 + 6] += footprint[
                    "GHGFootPrint_commitment_r"
                ]
                # uncompress the commitment
                unc_c = p.uncompress_point_to_tinyec(
                    footprint["GHGFootPrint_commitment"]
                )
                # accumulate the commitments
                totals[footprint["GHGFootPrint_scope"] - 1 + 3] = (
                    accumulate_commitments(
                        totals[footprint["GHGFootPrint_scope"] - 1 + 3], unc_c
                    )
                )
                company_commitments_tree.append(
                    " fp_id:" + str(footprint["GHGFootPrint_ID"])
                )
                company_commitments_tree.append(unc_c)
    return totals


def accumulate_commitments(*commitments):
    """Accumulates multiple commitments on an elliptic curve.

    Args:
        *commitments (tinyec point or int): The commitment points or 0.

    Returns:
        tinyec point or int: The accumulated commitment point or 0 if all inputs are 0.
    """
    pure_commitments = [x for x in commitments if x != 0]  # remove 0 commitments
    if len(pure_commitments) == 0:
        return 0  # return zero if no commitments in list
    else:
        accumulated = pure_commitments[0]
        for c in pure_commitments[1:]:
            accumulated = accumulated + c
        return accumulated


def upload_total_footprint(company, product, v, c, r):
    """
    Uploads the total GHG footprint for a product to the blockchain.

    This function posts a blockchain transaction to set the total GHG footprint for a product.
    It handles the case where the commitment value `r` might overflow the uint256 type in Solidity
    by splitting it into two 32-byte values.

    Args:
        company (dict): A dictionary containing company information, including the account to send the transaction from.
        product (dict): A dictionary containing product information, including the contract instance for setting the GHG footprint.
        v (int): The total GHG footprint value.
        c (list): A list containing two elements:
            - c[0] (int): The total GHG footprint commitment x value.
            - c[1] (int): The total GHG footprint commitment even or odd.
        r (int): The total GHG footprint commitment r value.

    Returns:
        None

    Raises:
        ValueError: If the transaction fails.
    """
    print("Upload GHG Parameters are: ", v, c, r)
    # post Blockchain tx to set total GHG footprint for a product
    # split r into two 32 byte values so as not to overflow uint256 in solidity
    r1, r2 = split_64bit_number(r)
    print("r is: ", r1, "r_2 is;", r2)
    transaction1 = product["productghgfootprint"].set_total_ghg(
        v,  # Total GHG footprint value
        c[0],  # Total GHG footprint commitment x value
        c[1],  # Total GHG footprint commitment even or odd
        r1,  # Total GHG footprint commitment r
        r2,  # Total GHG footprint commitment r overflow
        {"from": company["account"]},
    )
    transaction1.wait(1)
    # print("GHG Setting is:", transaction1)


def user_sum_up_commitments(p, contract_address, linked_fp_ids=[]):
    """
    Sums up the commitments for a user's GHG footprints in a smart contract.
    Args:
        p (Ped_scheme): An instance of the Ped_scheme class for cryptographic operations.
        contract_address (ProjectContract): The smart contract instance from which to retrieve GHG footprints.
        linked_fp_ids (list, optional): A list of linked footprint IDs. Defaults to an empty list.
    Returns:
        int: The total commitments for the user's GHG footprints.
    """
    global user_commitments_tree
    print("Contract address is: ", contract_address)
    footprints = contract_address.get_ghgfootprints()
    # print("User Verify footprints are:", list(footprints))
    total_commitments = 0
    for footprint in footprints:
        # print("Footprint is: ", footprint, "in contract", contract_address)
        # print("linked_fp_ids are: ", linked_fp_ids)
        # print("total commitments: ", total_commitments)
        fp_id = footprint[0]
        scope = footprint[1]
        disaggregation = footprint[2]
        category = footprint[3]
        if footprint[4] != "0x0000000000000000000000000000000000000000":
            linked_contract: ProjectContract = ProductGHGFootPrint.at(footprint[4])
        else:
            linked_contract = footprint[4]
        signature = footprint[6]
        units = footprint[7]
        commitment = footprint[8][0]
        commitment_y = footprint[8][1]
        if linked_contract != "0x0000000000000000000000000000000000000000":
            linked_fp_ids = footprint[5]
            total_commitments = accumulate_commitments(
                total_commitments,
                user_sum_up_commitments(p, linked_contract, linked_fp_ids),
            )
            linked_fp_ids = []
        else:
            if fp_id in linked_fp_ids or len(linked_fp_ids) == 0:
                unc_c = p.uncompress_point_to_tinyec((commitment, commitment_y))
                total_commitments = accumulate_commitments(total_commitments, unc_c)
                user_commitments_tree.append(
                    "Contract: " + str(contract_address) + " fp_id:" + str(fp_id)
                )
                user_commitments_tree.append(unc_c)
    return total_commitments



def get_total_footprint(p, contract_address):
    """
    Retrieves the total GHG footprint from a smart contract.
    Args:
        p (Ped_scheme): An instance of the Ped_scheme class for cryptographic operations.
        contract_address (ProjectContract): The smart contract instance from which to retrieve the total GHG footprint.
    
    Returns:
        tuple: A tuple containing:
            - fp_value (int): The total GHG footprint value.
            - total_commitment (tinyec point): The total GHG footprint commitment as a point on the elliptic curve.
            - total_r (int): The total GHG footprint commitment r value.
    """
    total_fp = contract_address.get_total_ghg()
    #print("Total GHG footprint is: ", total_fp)
    fp_value = total_fp[0]
    fp_commitment = total_fp[1]
    fp_commitment_y = total_fp[2]
    fp_commitment_r1 = total_fp[3]
    fp_commitment_r2 = total_fp[4]

    total_commitment = p.uncompress_point_to_tinyec((fp_commitment, fp_commitment_y))
    total_r = reassamble_64bit_number(fp_commitment_r1, fp_commitment_r2)

    return fp_value, total_commitment, total_r


def print_smart_contract(contract):
    """
    Prints the details of a smart contract including its address, description, and GHG footprints.
    Args:
        contract (dict): A dictionary containing the smart contract details, including:
            - productghgfootprint: The address of the smart contract.
            - description: A dictionary with the description of the contract.
            - GHG_Footprints: A list of GHG footprints associated with the contract.
    Returns:
        None
    """
    print("Smart Contract details: \n")
    print("Smart Contract owner account is: ", contract["productghgfootprint"].owner(), "\n")
    print("Smart Contract address is: ", contract["productghgfootprint"], "\n")
    print("Smart Contract owner name is: ", contract["description"]["owner_name"], "\n")
    print("Smart Contract product ID is: ", contract["description"]["productID"], "\n")
    print("Smart Contract product name is: ", contract["description"]["product_name"], "\n")
    print("Smart Contract product type is: ", contract["description"]["product_type"], "\n")
    print("Smart Contract units are: ", contract["description"]["units"], "\n")
    print("Smart Contract date created is: ", contract["description"]["date_created"], "\n")
    print("Smart Contract date updated is: ", contract["description"]["date_updated"], "\n")
    print("Smart Contract status is: ", contract["description"]["status"], "\n")
    print("Smart Contract owner address is: ", contract["productghgfootprint"].address, "\n")
    #print("Smart Contract ancestor contract is: ", contract["description"]["ancestor"], "\n")
    #print("Smart Contract descendant contract is: ", contract["description"]["descendant"], "\n")
    
    # print the GHG footprints in a DataFrame
    print("GHG Footprints for the contract:\n")
    footprints_df = pd.DataFrame.from_dict(contract["GHG_Footprints"])
    print(footprints_df)
    footprints_df.to_csv("footprints.csv")

    print(
        "Total GHG footprint is: ",
        contract["productghgfootprint"].get_total_ghg(),
        "\n",
    )


# global variable to store user commitments tree
user_commitments_tree = []
company_commitments_tree = []


def main():
    # Create a polynomial commitment object
    p = Ped_scheme()
    deploy_ProductGHGFootPrint()  # deploy the ProductGHGFootPrint contract to the Blockchain for each company and product
    set_description()  # set the description in the smart contract for each product
    create_commitments(p)  # create commitments for each GHG footprint for each company
    upload_footprints()  # upload the GHG footprints for each company to the blockchain and create links between contracts

    # Calculate the total GHG footprint for Company A Product 1 from the sample data (not Blockchain) 
    print("Calculating total GHG footprint for Company A Product 1 from Sample Data")
    total_v_c_r = sum_up_footprints(
        p, data["Company A"]["Product1"]["GHG_Footprints"]
    )  

    # Accumulate the total GHG footprint value, commitment, and commitment r

    total_footprint_value = sum(total_v_c_r[:3])
    total_footprint_commitment = accumulate_commitments(
        total_v_c_r[3], total_v_c_r[4], total_v_c_r[5]
    )
    total_footprint_commitment_r = sum(total_v_c_r[6:])

    print(
        "Total GHG footprint value for Company A Product 1 is: ", total_footprint_value
    )
    print(
        "Total GHG footprint commitment for Company A Product 1 is: ",
        total_footprint_commitment,
    )
    print(
        "Total GHG footprint commitment r for Company A Product 1 is: ",
        total_footprint_commitment_r,
    )

    print(
        "Verify total commitment is: ",
        p.verify(
            total_footprint_commitment,
            total_footprint_value,
            total_footprint_commitment_r,
        ),
    )

    # Upload the total GHG footprint for Company A Product 1 to the blockchain
    print("Uploading total GHG footprint for Company A Product 1 to the blockchain")
    upload_total_footprint(
        data["Company A"],
        data["Company A"]["Product1"],
        total_footprint_value,
        p.compress_point(total_footprint_commitment),
        total_footprint_commitment_r,
    )

    # Print the smart contract details for Company A Product 1
    print("Printing smart contract details for Company A Product 1")

    print_smart_contract(data["Company A"]["Product1"])

    # get the total GHG footprint for Company A Product 1 stored on the blockchain
    value, commitment, commitment_r = get_total_footprint(
        p, data["Company A"]["Product1"]["productghgfootprint"]
    )

    print("User can verify by unlocking the disclosed value of GHG:", value)
    print("using the commitment:", commitment)
    print("and the commitment r:", commitment_r,"/n")
    
    # Verify the commitment

    print("Verification is :", p.verify(commitment, value, commitment_r))

    