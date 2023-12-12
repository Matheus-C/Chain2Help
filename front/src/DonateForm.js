
import { JsonRpcProvider } from "@ethersproject/providers";
import { ethers } from "ethers";
import { InputBox__factory } from "@cartesi/rollups";

// OBS: change Echo DApp address as appropriate
const DAPP_ADDRESS = "0x70ac08179605AF2D9e75782b8DEcDD3c22aA4D0C";

// Standard configuration for local development environment
const INPUTBOX_ADDRESS = "0x59b22D57D4f067708AB0c00552767405926dc768";
const HARDHAT_DEFAULT_MNEMONIC =
    "test test test test test test test test test test test junk";
const HARDHAT_LOCALHOST_RPC_URL = "http://localhost:8545";

// This component presents an input field and adds its contents as an input for the Echo DApp

function handleSubmit(event) {
    event.preventDefault();
    const sendInput = async () => {
        setLoading(true);
        // Start a connection
        const provider = new JsonRpcProvider(HARDHAT_LOCALHOST_RPC_URL);
        const signer = ethers.Wallet.fromMnemonic(
            HARDHAT_DEFAULT_MNEMONIC,
            `m/44'/60'/0'/0/${accountIndex}`
        ).connect(provider);

        // Instantiate the InputBox contract
        const inputBox = InputBox__factory.connect(
            INPUTBOX_ADDRESS,
            signer
        );

        // Encode the input
        const inputBytes = ethers.utils.isBytesLike(value)
            ? value
            : ethers.utils.toUtf8Bytes(value);

        // Send the transaction
        const tx = await inputBox.addInput(DAPP_ADDRESS, inputBytes);
        console.log(`transaction: ${tx.hash}`);
        toast({
            title: "Transaction Sent",
            description: "waiting for confirmation",
            status: "success",
            duration: 9000,
            isClosable: true,
            position: "top-left",
        });

        // Wait for confirmation
        console.log("waiting for confirmation...");
        const receipt = await tx.wait(1);

        // Search for the InputAdded event
        const event = receipt.events?.find((e) => e.event === "InputAdded");

        setLoading(false);
        toast({
            title: "Transaction Confirmed",
            description: `Input added => index: ${event?.args.inputIndex} `,
            status: "success",
            duration: 9000,
            isClosable: true,
            position: "top-left",
        });
        console.log(`Input added => index: ${event?.args.inputIndex} `);
    };
    sendInput();
}

const form = document.getElementById("form");
form.addEventListener("submit", handleSubmit);

export default DonateForm;