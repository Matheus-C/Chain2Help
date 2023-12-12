timestamp=$(( $(date +%s) + 30 ))
end_date=$(($timestamp + 300))

cd ../rollups-examples/frontend-console/

echo "===========> Create an campaign starting in $timestamp and ending in $end_date"
yarn start input send --payload '{
    "method": "create",
    "args": {
        "erc20": "'0xc6e7DF5E7b4f2A278906862b61205850344D4e7d'",
        "title": "Campaign title",
        "description": "Some description",
        "start_date": '$timestamp',
        "end_date": '$end_date',
        "goal": 100000000000000000000000000000000
    }
}'

yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign"

yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0"

# cast send "0xc6e7DF5E7b4f2A278906862b61205850344D4e7d" "transfer(address,uint256)(bool)" "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" 2000 --mnemonic "test test test test test test test test test test test junk" --mnemonic-index 0 --rpc-url "http://localhost:8545"

yarn start erc20 deposit --amount 2000 # --accountIndex 1

yarn start input send --payload '{
    "method": "donate",
    "args": {
        "campaign_id": 0,
        "amount": 1000
    }
}'