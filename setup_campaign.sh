cd ../rollups-examples/common-contracts/
yarn deploy

cd ../frontend-console/

WALLET_0=0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266
WALLET_1=0x70997970C51812dc3A010C7d01b50e0d17dc79C8

ERC20=0x2797a6a6D9D94633BA700b52Ad99337DdaFA3f52

timestamp=$(( $(date +%s) + 60 ))
end_date=$(($timestamp + 900))

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

echo ""
echo ""
echo "===========> Check the balance of the account $WALLET_0 (creator)"
yarn start inspect --url http://localhost:8080/inspect/ --payload "balance/$WALLET_0"

echo ""
echo ""
echo "===========> List all campaigns"
yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign"

echo ""
echo ""
echo "===========> Check the campaign created"
yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0"

echo ""
echo ""
echo "===========> Transfer founds of account $WALLET_0 to $WALLET_1"
cast send '0x2797a6a6D9D94633BA700b52Ad99337DdaFA3f52' "transfer(address,uint256)(bool)" '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' 2000 --mnemonic "test test test test test test test test test test test junk" --mnemonic-index 0 --rpc-url "http://localhost:8545"

echo ""
echo ""
echo "===========> Check the founds of account $WALLET_1 before the deposit"
yarn start inspect --url http://localhost:8080/inspect/ --payload "balance/$WALLET_1"

echo ""
echo ""
echo "===========> Deposit 2000 founds of account $WALLET_1"
yarn start erc20 deposit --amount 2000 --accountIndex 1

echo ""
echo ""
echo "===========> Check the founds of account $WALLET_1 after the deposit"
yarn start inspect --url http://localhost:8080/inspect/ --payload "balance/$WALLET_1"

echo ""
echo ""
echo "===========> Donates 1000 founds of account $WALLET_1 to the created campaign"
yarn start input send --accountIndex 1 --payload '{
    "method": "donate",
    "args": {
        "campaign_id": 0,
        "amount": 1000
    }
}'

echo ""
echo ""
echo "===========> Check the founds of account $WALLET_1 (donor) after the donation"
yarn start inspect --url http://localhost:8080/inspect/ --payload "balance/$WALLET_1"

echo ""
echo ""
echo "===========> Check the founds of account $WALLET_0 (receiver) after the donation"
yarn start inspect --url http://localhost:8080/inspect/ --payload "balance/$WALLET_1"

echo ""
echo ""
echo "===========> List all campaign 0 donations"
yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0/donations"

echo ""
echo ""
echo "===========> Check the campaign founds updated"
yarn start inspect --url http://localhost:8080/inspect/ --payload "campaign/0"

echo ""
echo ""
echo "===========> End the campaign 0 before the ending date"
yarn start input send --payload '{
    "method": "end",
    "args": {
        "campaign_id": 0,
        "force": true
    }
}'

echo ""
echo ""
echo "===========> Campaign creator withdraws the money"
yarn start input send --payload '{
    "method": "withdraw",
    "args": {
        "erc20": "'$ERC20'",
        "amount": 1000
    }
}'

echo ""
echo ""
echo "===========> Check the founds of account $WALLET_0 (creator) after the withdraw"
yarn start inspect --url http://localhost:8080/inspect/ --payload "balance/$WALLET_0"

echo ""
echo ""
echo "===========> Account $WALLET_0 tries to withdraw more money than it has"
yarn start input send --payload '{
    "method": "withdraw",
    "args": {
        "erc20": "'$ERC20'",
        "amount": 500
    }
}'

echo ""
echo ""
echo "===========> List all notices generated from this interations"
yarn start notice list --url http://localhost:8080/graphql

echo ""
echo ""
echo "===========> Force time advance to check vouchers and reports generated"
curl -H "Content-type: application/json" --data '{"id":1336,"jsonrpc":"2.0","method":"evm_increaseTime","params":[864010]}' http://localhost:8545

echo ""
echo ""
echo "===========> List all vouchers generated from this interations"
yarn start voucher list --url http://localhost:8080/graphql

echo ""
echo ""
echo "===========> List all reports generated from this interations"
yarn start report list --url http://localhost:8080/graphql

