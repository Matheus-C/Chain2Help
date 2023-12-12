timestamp=$(( $(date +%s) + 30 ))
end_date=$(($timestamp + 300))

cd ../rollups-examples/frontend-console/

WALLET_0=0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266
WALLET_1=0x70997970C51812dc3A010C7d01b50e0d17dc79C8

ERC20=0x2797a6a6D9D94633BA700b52Ad99337DdaFA3f52

echo "===========> Create an campaign starting in $timestamp and ending in $end_date"
yarn start input send --payload '{
    "method": "create",
    "args": {
        "erc20": "'$ERC20'",
        "title": "Campaign title",
        "description": "Some description",
        "start_date": '$timestamp',
        "end_date": '$end_date',
        "goal": 100000000000000000000000000000000
    }
}'

yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign"

yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0"

cast send $ERC20 "transfer(address,uint256)(bool)" $WALLET_1 2000 --mnemonic "test test test test test test test test test test test junk" --mnemonic-index 0 --rpc-url "http://localhost:8545"

yarn start erc20 deposit --amount 2000 --accountIndex 1

yarn start input send --accountIndex 1 --payload '{
    "method": "donate",
    "args": {
        "campaign_id": 0,
        "amount": 1000
    }
}'

yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0/donations"

yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0"