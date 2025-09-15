from flask import Flask, send_from_directory, request, jsonify, abort
import os
import json

def load_json(file_path: str) -> dict:
    """Read a JSON file and return it as a dictionary"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fuzzy_query_json(data: dict, partial_key: str):
    """
    Fuzzy query JSON keys.
    Returns a dictionary of all matched key-value pairs where the key starts with partial_key.
    """
    result = {k: v for k, v in data.items() if k.startswith(partial_key)}
    return result

def build_entry(chain_id: int, contract_address: str) -> str:
    return f"{chain_id}:{contract_address}"

app = Flask(__name__)

BASE_DIR = os.path.abspath("cryptoassets")  # root directory

@app.route("/cryptoassets/evm/<int:chain_id>/erc20-signatures.json")
def get_cryptoassets(chain_id):
    # directory path
    dir_path = os.path.join(BASE_DIR, str(chain_id))
    file_path = os.path.join(dir_path, "erc20-signatures.json")
    print("ZYD file_path:", file_path)
    
    if os.path.exists(file_path):
        return send_from_directory(dir_path, "erc20-signatures.json", mimetype="application/json")
    else:
        abort(404, description=f"No JSON file for chain_id {chain_id}")

@app.route("/v1/dapps")
def get_dapps():
    # get query args
    output = request.args.get("output")
    version = request.args.get("eip712_signatures_version")
    chain_id = request.args.get("chain_id")
    contracts = request.args.get("contracts")  # consider only one contract

    # simple check
    if not all([output, version, chain_id, contracts]):
        abort(400, description="Missing required query parameters")

    file_path = os.path.join(os.path.abspath("v1/dapps"), "tip712_v2.json")
    print("ZYD file_path:", file_path)

    # load JSON file
    data = load_json(file_path)

    # Partial key to query
    partial_key = build_entry(chain_id, contracts.lower())
    matches = fuzzy_query_json(data, partial_key)

    result = {}
    result[output] = {}
    if matches:
        print("Matched results:")
        for k, v in matches.items():
            print(f"{k} -> {v}")
            # Split by colon
            parts = k.split(":")

            chain_id = parts[0]
            contract = parts[1]
            schema_hash = parts[2]

            print("chainId:", chain_id)
            print("contract:", contract)
            print("schema_hash:", schema_hash)
            
            if not result.get(output, {}).get(contract, {}):
                result[output][contract] = {}
            result[output][contract][schema_hash] = v

    else:
        print(f"No matches found for {partial_key}")
        abort(404, description=f"No JSON file for chain_id {partial_key}")
    
    print("result:", result)
    response_data = [result]

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
